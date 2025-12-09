import functions_framework
from google.cloud import firestore
import json
import base64
from datetime import datetime

db = firestore.Client()

@functions_framework.cloud_event
def process_light(cloud_event):
    """
    Тригер: Pub/Sub topic 'sensor-light'
    Обробляє дані датчиків освітлення
    """
    try:
        # Декодуємо дані з Pub/Sub
        pubsub_message = cloud_event.data["message"]
        
        if "data" in pubsub_message:
            message_data = json.loads(base64.b64decode(pubsub_message["data"]).decode())
        else:
            print("No data in message")
            return
        
        # Витягуємо атрибути
        sensor_id = message_data.get("sensor_id")
        value = message_data.get("value")
        unit = message_data.get("unit")
        location = message_data.get("location")
        timestamp = message_data.get("timestamp")
        
        # Визначення рівня освітлення
        light_level = "normal"
        if value < 100:
            light_level = "dark"
        elif value < 500:
            light_level = "dim"
        elif value > 10000:
            light_level = "very_bright"
        
        # Зберігаємо в Cloud Firestore
        doc_ref = db.collection('light_readings').document()
        doc_ref.set({
            'sensor_id': sensor_id,
            'value': value,
            'unit': unit,
            'location': location,
            'timestamp': timestamp,
            'light_level': light_level,
            'processed_at': datetime.utcnow().isoformat()
        })
        
        print(f"✅ Освітлення оброблено: {sensor_id} = {value} lux ({light_level})")
        return {'status': 'success', 'light_level': light_level}
        
    except Exception as e:
        print(f"❌ Error processing light: {e}")
        return {'status': 'error', 'message': str(e)}