from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from datetime import datetime
from typing import Optional
from src.api.emulator.shema import SensorConfig, EmulatorStatus, SensorData
from src.services.emulator import emulator
from src.services.database import DatabaseService
from src.services.gcp_pubsub import gcp_pubsub_service
from src.db.conn import get_db
from settings import get_settings

router = APIRouter(prefix="/emulator", tags=["Emulator"])


@router.post("/sensors", status_code=status.HTTP_201_CREATED)
async def add_sensor(config: SensorConfig, db: AsyncSession = Depends(get_db)):
    """Add a new sensor to the emulator and save to database"""
    db_sensor = await DatabaseService.save_sensor_config(db, config)
    emulator.add_sensor(config)
    
    return {
        "message": f"Sensor {config.sensor_id} added successfully",
        "config": config,
        "db_id": db_sensor.id
    }


@router.delete("/sensors/{sensor_id}")
async def remove_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
    """Remove a sensor from the emulator and database"""
    deleted = await DatabaseService.delete_sensor_config(db, sensor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor {sensor_id} not found"
        )
    
    emulator.remove_sensor(sensor_id)
    return {"message": f"Sensor {sensor_id} removed successfully"}


@router.get("/sensors")
async def list_sensors(db: AsyncSession = Depends(get_db)):
    """List all configured sensors"""
    sensors = await DatabaseService.get_all_sensor_configs(db)
    return {
        "total": len(sensors),
        "sensors": [sensor.to_dict() for sensor in sensors]
    }


@router.get("/sensors/{sensor_id}")
async def get_sensor(sensor_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific sensor configuration"""
    sensor = await DatabaseService.get_sensor_config(db, sensor_id)
    if not sensor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sensor {sensor_id} not found"
        )
    return sensor.to_dict()


@router.post("/start")
async def start_emulator(
    use_pubsub: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """Start the emulator with sensors from database"""
    if emulator.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emulator is already running"
        )
    
    db_sensors = await DatabaseService.get_all_sensor_configs(db, active_only=True)
    
    if not db_sensors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active sensors found in database"
        )
    
    emulator.use_pubsub = use_pubsub
    emulator.sensors.clear()
    
    for db_sensor in db_sensors:
        config = SensorConfig(
            sensor_id=db_sensor.sensor_id,
            sensor_type=db_sensor.sensor_type.value,
            interval_ms=db_sensor.interval_ms,
            location=db_sensor.location,
            target_url=db_sensor.target_url,
            min_value=db_sensor.min_value,
            max_value=db_sensor.max_value
        )
        emulator.add_sensor(config)
    
    await emulator.start()
    return {
        "message": "Emulator started",
        "active_sensors": len(emulator.sensors),
        "mode": "Pub/Sub" if use_pubsub else "HTTP"
    }


@router.post("/stop")
async def stop_emulator():
    """Stop the emulator"""
    if not emulator.is_running:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emulator is not running"
        )
    
    await emulator.stop()
    return {"message": "Emulator stopped"}


@router.get("/status", response_model=EmulatorStatus)
async def get_status():
    """Get emulator status"""
    status_data = emulator.get_status()
    return EmulatorStatus(**status_data)


@router.post("/data/receive")
async def receive_sensor_data(data: SensorData, db: AsyncSession = Depends(get_db)):
    """Endpoint to receive sensor data and save to database"""
    db_reading = await DatabaseService.save_sensor_reading(db, data)
    
    print(f"Received data from {data.sensor_id}: {data.value} {data.unit}")
    return {
        "message": "Data received and saved",
        "data": data,
        "db_id": db_reading.id
    }


@router.post("/pubsub/test")
async def test_pubsub(data: SensorData):
    """Test publishing to Pub/Sub"""
    message_id = await gcp_pubsub_service.publish_sensor_data(data)
    
    if message_id:
        return {
            "message": "Successfully published to Pub/Sub",
            "message_id": message_id,
            "topic": gcp_pubsub_service.topic_paths.get(data.sensor_type)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish to Pub/Sub"
        )


@router.get("/readings")
async def get_readings(
    sensor_id: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get sensor readings from local PostgreSQL database"""
    readings = await DatabaseService.get_sensor_readings(db, sensor_id, limit)
    return {
        "source": "PostgreSQL",
        "total": len(readings),
        "readings": [reading.to_dict() for reading in readings]
    }


@router.get("/readings/cloud")
async def get_readings_from_cloud(
    sensor_id: Optional[str] = None,
    sensor_type: str = "temperature",
    limit: int = 100,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get sensor readings from Cloud Firestore via Cloud Function
    
    Параметри:
    - sensor_id: ID датчика (опціонально)
    - sensor_type: тип датчика (temperature, humidity, light)
    - limit: максимальна кількість записів (default: 100)
    - start_date: початкова дата у форматі ISO (опціонально)
    - end_date: кінцева дата у форматі ISO (опціонально)
    """
    settings = get_settings()
    
    if not settings.CLOUD_FUNCTION_HISTORY_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cloud Function URL is not configured. Please set CLOUD_FUNCTION_HISTORY_URL in .env"
        )
    
    # Валідація типу сенсора
    valid_types = ["temperature", "humidity", "light"]
    if sensor_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sensor_type. Must be one of: {', '.join(valid_types)}"
        )
    
    # Підготовка параметрів запиту
    params = {
        "sensor_type": sensor_type,
        "limit": limit
    }
    
    if sensor_id:
        params["sensor_id"] = sensor_id
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                settings.CLOUD_FUNCTION_HISTORY_URL,
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "source": "Cloud Firestore (via Cloud Function)",
                    "cloud_function_url": settings.CLOUD_FUNCTION_HISTORY_URL,
                    **data
                }
            else:
                error_detail = response.text
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Cloud Function error: {error_detail}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to Cloud Function timed out"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Cloud Function: {str(e)}"
        )


@router.get("/readings/compare")
async def compare_readings(
    sensor_id: Optional[str] = None,
    sensor_type: str = "temperature",
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """
    Порівняння даних з PostgreSQL та Firestore
    
    Корисно для перевірки синхронізації даних між локальною БД та Firestore
    """
    settings = get_settings()
    
    # Отримуємо дані з PostgreSQL
    pg_readings = await DatabaseService.get_sensor_readings(db, sensor_id, limit)
    
    # Отримуємо дані з Firestore
    firestore_data = None
    if settings.CLOUD_FUNCTION_HISTORY_URL:
        try:
            params = {
                "sensor_type": sensor_type,
                "limit": limit
            }
            if sensor_id:
                params["sensor_id"] = sensor_id
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    settings.CLOUD_FUNCTION_HISTORY_URL,
                    params=params
                )
                if response.status_code == 200:
                    firestore_data = response.json()
        except Exception as e:
            print(f"Failed to fetch Firestore data: {e}")
    
    return {
        "comparison": {
            "postgresql": {
                "count": len(pg_readings),
                "latest": pg_readings[0].to_dict() if pg_readings else None
            },
            "firestore": {
                "count": firestore_data.get("total_records") if firestore_data else 0,
                "latest": firestore_data.get("readings")[0] if firestore_data and firestore_data.get("readings") else None,
                "available": firestore_data is not None
            }
        },
        "postgresql_readings": [r.to_dict() for r in pg_readings[:10]],  # Перші 10
        "firestore_readings": firestore_data.get("readings")[:10] if firestore_data else []  # Перші 10
    }


@router.post("/pubsub/init")
async def initialize_pubsub():
    """Initialize Pub/Sub topics"""
    try:
        gcp_pubsub_service.create_topics_if_not_exist()
        return {
            "message": "Pub/Sub topics initialized",
            "topics": {
                sensor_type.value: topic_path
                for sensor_type, topic_path in gcp_pubsub_service.topic_paths.items()
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize topics: {str(e)}"
        )