import functions_framework
from google.cloud import firestore
import json
import base64
from datetime import datetime

db = firestore.Client()

@functions_framework.cloud_event
def process_temperature(cloud_event):
    """
    Тригер: Pub/Sub topic 'sensor-temperature'
    Обробляє дані температурних сенсорів
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
        sensor_type = message_data.get("sensor_type")
        value = message_data.get("value")
        unit = message_data.get("unit")
        location = message_data.get("location")
        timestamp = message_data.get("timestamp")
        
        # Валідація специфічна для температури
        if value < -50 or value > 50:
            print(f"⚠️ Аномальна температура: {value}°C")
        
        # Зберігаємо в Cloud Firestore
        doc_ref = db.collection('temperature_readings').document()
        doc_ref.set({
            'sensor_id': sensor_id,
            'value': value,
            'unit': unit,
            'location': location,
            'timestamp': timestamp,
            'processed_at': datetime.utcnow().isoformat()
        })
        
        print(f"✅ Температура оброблена: {sensor_id} = {value}°C")
        return {'status': 'success'}
        
    except Exception as e:
        print(f"❌ Error processing temperature: {e}")
        return {'status': 'error', 'message': str(e)}