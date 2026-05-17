from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from random import uniform
import random
import time
import requests
from threading import Lock

BASE_URL = os.environ.get("BASE_URL", "https://flask-app-509731619895.europe-west1.run.app")

print(f"Running load tests against {BASE_URL}")

# Глобальні лічильники з thread-safe lock
stats_lock = Lock()
stats = {
    'total': 0,
    'success': 0,
    'failed': 0,
    'times': []
}


def get_token():
    payload = {
        "email": "test@gmail.com",
        "password": "123456789",
        "returnSecureToken": True
    }
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload, timeout=10)
        if response.status_code != 200:
            return None
        return response.json().get("idToken")
    except requests.RequestException as e:
        print(f"Error obtaining token: {e}")
        return None


def make_request(endpoint: str, token, method: str, data=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=30)
        else:
            raise ValueError("Unsupported HTTP method")
        return {
            "status": response.status_code,
            "endpoint": endpoint,
            "response_time": response.elapsed.total_seconds(),
        }
    except requests.RequestException as e:
        return {
            "status": "error",
            "endpoint": endpoint,
            "error": str(e)
        }


def continuous_load_worker(token, worker_id, stop_time):
    """Безперервно відправляє запити до stop_time"""
    local_stats = {'success': 0, 'failed': 0, 'times': []}
    
    endpoints = [
        ("/users", "GET", None),
        ("/users/33", "GET", None),
    ]
    
    while time.time() < stop_time:
        # Вибираємо випадковий endpoint
        endpoint, method, data = random.choice(endpoints)
        result = make_request(endpoint, token, method, data)
        
        if result['status'] in [200, 201, 204]:
            local_stats['success'] += 1
            if 'response_time' in result:
                local_stats['times'].append(result['response_time'])
        else:
            local_stats['failed'] += 1
        
        # Мала пауза між запитами від ОДНОГО воркера
        time.sleep(random.uniform(0.05, 0.15))
    
    # Оновлюємо глобальну статистику
    with stats_lock:
        stats['total'] += local_stats['success'] + local_stats['failed']
        stats['success'] += local_stats['success']
        stats['failed'] += local_stats['failed']
        stats['times'].extend(local_stats['times'])


def run_load_test(num_users=15, duration_seconds=60):
    """
    Постійне навантаження з num_users одночасних користувачів
    
    Args:
        num_users: Кількість одночасних користувачів (>10 для масштабування)
        duration_seconds: Тривалість тесту в секундах
    """
    print(f"🚀 Starting CONTINUOUS load test")
    print(f"Target: {BASE_URL}")
    print(f"Concurrent users: {num_users}")
    print(f"Duration: {duration_seconds}s")
    print(f"Expected: Should trigger 2nd instance (concurrency limit: 10)\n")
    
    # Отримати токен
    token = get_token()
    if not token:
        print("⚠️  No token - testing public endpoints only")
    
    start_time = time.time()
    stop_time = start_time + duration_seconds
    
    # Скидаємо статистику
    with stats_lock:
        stats['total'] = 0
        stats['success'] = 0
        stats['failed'] = 0
        stats['times'] = []
    
    # Запускаємо workers які ПОСТІЙНО відправляють запити
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        futures = [
            executor.submit(continuous_load_worker, token, i, stop_time)
            for i in range(num_users)
        ]
        
        # Моніторинг прогресу
        last_print = start_time
        while time.time() < stop_time:
            time.sleep(2)
            if time.time() - last_print >= 5:
                elapsed = time.time() - start_time
                with stats_lock:
                    rps = stats['total'] / elapsed if elapsed > 0 else 0
                    print(f"⏱️  {elapsed:.0f}s | Total: {stats['total']} | "
                          f"Success: {stats['success']} | Failed: {stats['failed']} | "
                          f"RPS: {rps:.1f}")
                last_print = time.time()
        
        # Чекаємо завершення всіх workers
        for future in futures:
            future.result()
    
    # Результати
    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print("📊 LOAD TEST RESULTS")
    print("="*60)
    print(f"Total Duration: {elapsed:.1f}s")
    print(f"Total Requests: {stats['total']}")
    print(f"Successful: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    print(f"Requests/second: {stats['total']/elapsed:.2f}")
    
    if stats['times']:
        avg_response = sum(stats['times']) / len(stats['times'])
        min_response = min(stats['times'])
        max_response = max(stats['times'])
        print(f"\nResponse Times:")
        print(f"  Average: {avg_response:.3f}s")
        print(f"  Min: {min_response:.3f}s")
        print(f"  Max: {max_response:.3f}s")
    
    print(f"\n💡 Check Cloud Run metrics to see scaling events!")
    print(f"   https://console.cloud.google.com/run/detail/europe-west1/flask-app/metrics")


if __name__ == "__main__":
    # Тест з 15 користувачами протягом 60 секунд
    # 15 > 10 (concurrency) → має створитися 2-й контейнер
    run_load_test(num_users=15, duration_seconds=60)
