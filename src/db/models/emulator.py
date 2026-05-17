from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from src.db.conn import Base
import enum


class SensorTypeEnum(str, enum.Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"


class SensorConfigDB(Base):
    """Database model for sensor configurations"""
    __tablename__ = "sensor_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(100), unique=True, nullable=False, index=True)
    sensor_type = Column(SQLEnum(SensorTypeEnum), nullable=False)
    interval_ms = Column(Integer, nullable=False)
    location = Column(JSONB, nullable=False)  # {"latitude": float, "longitude": float}
    target_url = Column(String(500), nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    
    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type.value,
            "interval_ms": self.interval_ms,
            "location": self.location,
            "target_url": self.target_url,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": bool(self.is_active)
        }


class SensorReadingDB(Base):
    """Database model for sensor readings"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(100), nullable=False, index=True)
    sensor_type = Column(SQLEnum(SensorTypeEnum), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "sensor_type": self.sensor_type.value,
            "value": self.value,
            "unit": self.unit,
            "location": {
                "latitude": self.latitude,
                "longitude": self.longitude
            },
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }