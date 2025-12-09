import json
import os
from typing import Dict, Optional
from google.cloud import pubsub_v1
from google.oauth2 import service_account
from src.api.emulator.shema import SensorData, SensorType
from settings import get_settings

settings = get_settings()


class GCPPubSubService:
    """Service for publishing sensor data to Google Cloud Pub/Sub"""
    
    def __init__(self):
        self.project_id = settings.GCP_PROJECT_ID
        self.publisher: Optional[pubsub_v1.PublisherClient] = None
        self.topic_paths: Dict[SensorType, str] = {}
        self._initialize_publisher()
    
    def _initialize_publisher(self):
        """Initialize Pub/Sub publisher with credentials"""
        try:
            # Load credentials from file
            if os.path.exists(settings.GCP_CREDENTIALS_PATH):
                credentials = service_account.Credentials.from_service_account_file(
                    settings.GCP_CREDENTIALS_PATH
                )
                self.publisher = pubsub_v1.PublisherClient(credentials=credentials)
            else:
                # Use default credentials (for GCP environment)
                self.publisher = pubsub_v1.PublisherClient()
            
            # Initialize topic paths for different sensor types
            self.topic_paths = {
                SensorType.TEMPERATURE: self.publisher.topic_path(
                    self.project_id, 
                    settings.GCP_TOPIC_TEMPERATURE
                ),
                SensorType.HUMIDITY: self.publisher.topic_path(
                    self.project_id, 
                    settings.GCP_TOPIC_HUMIDITY
                ),
                SensorType.LIGHT: self.publisher.topic_path(
                    self.project_id, 
                    settings.GCP_TOPIC_LIGHT
                )
            }
            
            print(f"✅ GCP Pub/Sub initialized for project: {self.project_id}")
            
        except Exception as e:
            print(f"❌ Failed to initialize GCP Pub/Sub: {e}")
            self.publisher = None
    
    async def publish_sensor_data(self, sensor_data: SensorData) -> Optional[str]:
        """
        Publish sensor data to appropriate Pub/Sub topic based on sensor type
        
        Returns:
            Message ID if successful, None otherwise
        """
        if not self.publisher:
            print("⚠️  Publisher not initialized")
            return None
        
        try:
            # Get the appropriate topic for this sensor type
            topic_path = self.topic_paths.get(sensor_data.sensor_type)
            
            if not topic_path:
                print(f"⚠️  No topic configured for sensor type: {sensor_data.sensor_type}")
                return None
            
            # Prepare message data
            message_data = {
                "sensor_id": sensor_data.sensor_id,
                "sensor_type": sensor_data.sensor_type.value,
                "value": sensor_data.value,
                "unit": sensor_data.unit,
                "location": {
                    "latitude": sensor_data.location.latitude,
                    "longitude": sensor_data.location.longitude
                },
                "timestamp": sensor_data.timestamp.isoformat()
            }
            
            # Convert to JSON bytes
            message_bytes = json.dumps(message_data).encode("utf-8")
            
            # Add attributes for filtering and routing
            attributes = {
                "sensor_type": sensor_data.sensor_type.value,
                "sensor_id": sensor_data.sensor_id,
                "origin": "sensor_emulator"
            }
            
            # Publish message
            future = self.publisher.publish(
                topic_path,
                message_bytes,
                **attributes
            )
            
            # Wait for publish to complete
            message_id = future.result()
            
            print(f"📤 Published to {sensor_data.sensor_type.value} topic: {message_id}")
            return message_id
            
        except Exception as e:
            print(f"❌ Failed to publish message: {e}")
            return None
    
    def create_topics_if_not_exist(self):
        """Create Pub/Sub topics if they don't exist"""
        if not self.publisher:
            return
        
        for sensor_type, topic_path in self.topic_paths.items():
            try:
                self.publisher.get_topic(request={"topic": topic_path})
                print(f"✅ Topic exists: {topic_path}")
            except Exception:
                try:
                    self.publisher.create_topic(request={"name": topic_path})
                    print(f"✅ Created topic: {topic_path}")
                except Exception as e:
                    print(f"❌ Failed to create topic {topic_path}: {e}")


# Global instance
gcp_pubsub_service = GCPPubSubService()