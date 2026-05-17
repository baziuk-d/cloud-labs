import asyncio
import random
from datetime import datetime
from typing import Dict, Optional
import httpx
from src.api.emulator.shema import SensorConfig, SensorData, SensorType
from src.services.gcp_pubsub import gcp_pubsub_service


class SensorEmulator:
    def __init__(self):
        self.sensors: Dict[str, SensorConfig] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.is_running = False
        self.http_client: Optional[httpx.AsyncClient] = None
        self.use_pubsub = True  # Flag to use Pub/Sub instead of direct HTTP
    
    def add_sensor(self, config: SensorConfig):
        """Add a sensor configuration"""
        self.sensors[config.sensor_id] = config
    
    def remove_sensor(self, sensor_id: str):
        """Remove a sensor configuration"""
        if sensor_id in self.sensors:
            del self.sensors[sensor_id]
            if sensor_id in self.running_tasks:
                self.running_tasks[sensor_id].cancel()
                del self.running_tasks[sensor_id]
    
    def get_sensor_unit(self, sensor_type: SensorType) -> str:
        """Get the unit for a sensor type"""
        units = {
            SensorType.TEMPERATURE: "°C",
            SensorType.HUMIDITY: "%",
            SensorType.LIGHT: "lux"
        }
        return units.get(sensor_type, "unit")
    
    async def emulate_sensor(self, config: SensorConfig):
        """Emulate a single sensor sending data at specified intervals"""
        while self.is_running:
            try:
                # Generate random sensor value
                value = random.uniform(config.min_value, config.max_value)
                
                # Create sensor data
                sensor_data = SensorData(
                    sensor_id=config.sensor_id,
                    sensor_type=config.sensor_type,
                    value=round(value, 2),
                    unit=self.get_sensor_unit(config.sensor_type),
                    location=config.location,
                    timestamp=datetime.now()
                )
                
                # Send to Pub/Sub or HTTP endpoint
                if self.use_pubsub:
                    # Publish to GCP Pub/Sub
                    message_id = await gcp_pubsub_service.publish_sensor_data(sensor_data)
                    if message_id:
                        print(f"[{config.sensor_id}] Published: {value:.2f} {self.get_sensor_unit(config.sensor_type)} → Message ID: {message_id}")
                    else:
                        print(f"[{config.sensor_id}] Failed to publish to Pub/Sub")
                else:
                    # Fallback to HTTP
                    if self.http_client:
                        try:
                            response = await self.http_client.post(
                                config.target_url,
                                json=sensor_data.model_dump(mode='json'),
                                timeout=5.0
                            )
                            print(f"[{config.sensor_id}] Sent via HTTP: {value:.2f} {self.get_sensor_unit(config.sensor_type)} - Status: {response.status_code}")
                        except httpx.RequestError as e:
                            print(f"[{config.sensor_id}] HTTP Error: {e}")
                
                # Wait for the specified interval
                await asyncio.sleep(config.interval_ms / 1000.0)
            
            except asyncio.CancelledError:
                print(f"[{config.sensor_id}] Sensor emulation stopped")
                break
            except Exception as e:
                print(f"[{config.sensor_id}] Unexpected error: {e}")
                await asyncio.sleep(1)
    
    async def start(self):
        """Start all sensor emulations"""
        if self.is_running:
            raise ValueError("Emulator is already running")
        
        if not self.sensors:
            raise ValueError("No sensors configured. Add sensors before starting.")
        
        self.is_running = True
        
        if not self.use_pubsub:
            self.http_client = httpx.AsyncClient()
        
        for sensor_id, config in self.sensors.items():
            task = asyncio.create_task(self.emulate_sensor(config))
            self.running_tasks[sensor_id] = task
        
        print(f"Started emulation for {len(self.sensors)} sensors (Mode: {'Pub/Sub' if self.use_pubsub else 'HTTP'})")
    
    async def stop(self):
        """Stop all sensor emulations"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        for task in self.running_tasks.values():
            task.cancel()
        
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks.values(), return_exceptions=True)
        
        self.running_tasks.clear()
        
        if self.http_client:
            await self.http_client.aclose()
            self.http_client = None
        
        print("Stopped all sensor emulations")
    
    def get_status(self) -> dict:
        """Get current emulator status"""
        return {
            "is_running": self.is_running,
            "active_sensors": len(self.sensors),
            "mode": "Pub/Sub" if self.use_pubsub else "HTTP",
            "sensors": [sensor.model_dump() for sensor in self.sensors.values()]
        }


# Global emulator instance
emulator = SensorEmulator()