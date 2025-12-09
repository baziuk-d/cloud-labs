from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.models.emulator import SensorConfigDB, SensorReadingDB
from src.api.emulator.shema import SensorConfig, SensorData, Location, SensorType


class DatabaseService:
    """Service for database operations"""
    
    @staticmethod
    async def save_sensor_config(db: AsyncSession, config: SensorConfig) -> SensorConfigDB:
        """Save or update sensor configuration"""
        # Check if sensor already exists
        result = await db.execute(
            select(SensorConfigDB).where(SensorConfigDB.sensor_id == config.sensor_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update existing sensor
            existing.sensor_type = config.sensor_type.value
            existing.interval_ms = config.interval_ms
            existing.location = config.location.model_dump()
            existing.target_url = config.target_url
            existing.min_value = config.min_value
            existing.max_value = config.max_value
            existing.is_active = 1
            db_sensor = existing
        else:
            # Create new sensor
            db_sensor = SensorConfigDB(
                sensor_id=config.sensor_id,
                sensor_type=config.sensor_type.value,
                interval_ms=config.interval_ms,
                location=config.location.model_dump(),
                target_url=config.target_url,
                min_value=config.min_value,
                max_value=config.max_value,
                is_active=1
            )
            db.add(db_sensor)
        
        await db.flush()
        await db.refresh(db_sensor)
        return db_sensor
    
    @staticmethod
    async def get_sensor_config(db: AsyncSession, sensor_id: str) -> Optional[SensorConfigDB]:
        """Get sensor configuration by ID"""
        result = await db.execute(
            select(SensorConfigDB).where(SensorConfigDB.sensor_id == sensor_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_sensor_configs(db: AsyncSession, active_only: bool = True) -> List[SensorConfigDB]:
        """Get all sensor configurations"""
        query = select(SensorConfigDB)
        if active_only:
            query = query.where(SensorConfigDB.is_active == 1)
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def delete_sensor_config(db: AsyncSession, sensor_id: str) -> bool:
        """Delete sensor configuration"""
        result = await db.execute(
            delete(SensorConfigDB).where(SensorConfigDB.sensor_id == sensor_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def deactivate_sensor_config(db: AsyncSession, sensor_id: str) -> bool:
        """Deactivate sensor configuration (soft delete)"""
        result = await db.execute(
            select(SensorConfigDB).where(SensorConfigDB.sensor_id == sensor_id)
        )
        sensor = result.scalar_one_or_none()
        if sensor:
            sensor.is_active = 0
            await db.flush()
            return True
        return False
    
    @staticmethod
    async def save_sensor_reading(db: AsyncSession, data: SensorData) -> SensorReadingDB:
        """Save sensor reading"""
        db_reading = SensorReadingDB(
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type.value,
            value=data.value,
            unit=data.unit,
            latitude=data.location.latitude,
            longitude=data.location.longitude,
            timestamp=data.timestamp
        )
        db.add(db_reading)
        await db.flush()
        await db.refresh(db_reading)
        return db_reading
    
    @staticmethod
    async def get_sensor_readings(
        db: AsyncSession, 
        sensor_id: Optional[str] = None,
        limit: int = 100
    ) -> List[SensorReadingDB]:
        """Get sensor readings with optional filtering"""
        query = select(SensorReadingDB).order_by(SensorReadingDB.timestamp.desc())
        if sensor_id:
            query = query.where(SensorReadingDB.sensor_id == sensor_id)
        query = query.limit(limit)
        result = await db.execute(query)
        return result.scalars().all()