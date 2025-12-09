import functions_framework
from google.cloud import firestore
from flask import jsonify
from datetime import datetime

db = firestore.Client()

@functions_framework.http
def get_sensor_history(request):
    """
    HTTP endpoint для отримання історії даних з датчиків
    GET /get_sensor_history?sensor_id=temp-001&sensor_type=temperature&limit=100
    """
    # CORS headers для доступу з браузера
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Отримуємо параметри з query string
        sensor_id = request.args.get('sensor_id')
        sensor_type = request.args.get('sensor_type', 'temperature')
        limit = int(request.args.get('limit', 100))
        start_date = request.args.get('start_date')  # ISO format
        end_date = request.args.get('end_date')      # ISO format
        
        # Мапування типів сенсорів на колекції Firestore
        collection_map = {
            'temperature': 'temperature_readings',
            'humidity': 'humidity_readings',
            'light': 'light_readings'
        }
        
        collection_name = collection_map.get(sensor_type)
        if not collection_name:
            return jsonify({
                'error': 'Invalid sensor type',
                'valid_types': list(collection_map.keys())
            }), 400, headers
        
        # Створюємо запит до Firestore
        query = db.collection(collection_name)
        
        # Фільтр по sensor_id
        if sensor_id:
            query = query.where('sensor_id', '==', sensor_id)
        
        # Фільтр по датам
        if start_date:
            query = query.where('timestamp', '>=', start_date)
        if end_date:
            query = query.where('timestamp', '<=', end_date)
        
        # Сортуємо по timestamp (найновіші спочатку) і обмежуємо кількість
        query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
        
        # Виконуємо запит
        docs = query.stream()
        
        # Формуємо результат
        results = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            results.append(data)
        
        # Статистика для відповіді
        stats = None
        if results and sensor_type == 'temperature':
            values = [r['value'] for r in results]
            stats = {
                'count': len(results),
                'avg': round(sum(values) / len(values), 2),
                'min': round(min(values), 2),
                'max': round(max(values), 2)
            }
        
        response = {
            'success': True,
            'sensor_type': sensor_type,
            'total_records': len(results),
            'readings': results
        }
        
        if stats:
            response['statistics'] = stats
        
        return jsonify(response), 200, headers
        
    except ValueError as e:
        return jsonify({
            'error': 'Invalid parameter value',
            'details': str(e)
        }), 400, headers
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500, headers