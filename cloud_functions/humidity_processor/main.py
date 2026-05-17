import functions_framework
from google.cloud import firestore
import json
import base64
from datetime import datetime

db = firestore.Client()

@functions_framework.cloud_event
def process_humidity(cloud_event):
    """
    Trigger: Pub/Sub topic 'sensor-humidity'
    Processes data from humidity sensors.
    """
    try:
        # Decode the Pub/Sub message
        pubsub_message = cloud_event.data["message"]
        
        if "data" in pubsub_message:
            message_data = json.loads(base64.b64decode(pubsub_message["data"]).decode())
        else:
            print("No data in message")
            return
        
        # Extract attributes
        sensor_id = message_data.get("sensor_id")
        value = message_data.get("value")
        unit = message_data.get("unit")
        location = message_data.get("location")
        timestamp = message_data.get("timestamp")
        
        # Validate humidity range (0-100%)
        if value < 0 or value > 100:
            print(f"⚠️ Anomalous humidity value: {value}%")
        
        # Determine humidity level
        humidity_level = "normal"
        if value < 30:
            humidity_level = "low"
        elif value > 60:
            humidity_level = "high"
        
        # Save to Firestore
        doc_ref = db.collection('humidity_readings').document()
        doc_ref.set({
            'sensor_id': sensor_id,
            'value': value,
            'unit': unit,
            'location': location,
            'timestamp': timestamp,
            'humidity_level': humidity_level,
            'processed_at': datetime.utcnow().isoformat()
        })
        
        print(f"✅ Humidity processed: {sensor_id} = {value}% ({humidity_level})")
        return {'status': 'success', 'humidity_level': humidity_level}
        
    except Exception as e:
        print(f"❌ Error processing humidity: {e}")
        return {'status': 'error', 'message': str(e)}