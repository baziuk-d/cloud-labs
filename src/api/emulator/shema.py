
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class SensorType(str, Enum):
    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    LIGHT = "light"


class Location(BaseModel):
    latitude: float
    longitude: float


class SensorData(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    value: float
    unit: str
    location: Location
    timestamp: datetime


class SensorConfig(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    interval_ms: int  # 20-100 ms
    location: Location
    target_url: str
    min_value: float
    max_value: float


class EmulatorStatus(BaseModel):
    is_running: bool
    active_sensors: int
    sensors: list[SensorConfig]