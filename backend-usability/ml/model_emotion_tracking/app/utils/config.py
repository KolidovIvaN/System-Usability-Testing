import os
from enum import Enum
from typing import Optional

import torch
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DeviceType(str, Enum):
    CPU = "cpu"
    CUDA = "cuda"
    AUTO = "auto"


class AppSettings(BaseSettings):
    """Настройки приложения с поддержкой .env и CLI"""
    
    model_config = SettingsConfigDict(
        env_file=os.path.abspath(os.path.join(os.path.dirname(__name__), "..", ".env")),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Сервис
    host: str = Field(default="0.0.0.0", description="Host для uvicorn")
    port: int = Field(default=8000, description="Port для uvicorn")
    workers: int = Field(default=1, description="Количество процессов uvicorn (--workers)")
    
    # Модель
    model_device: DeviceType = Field(
        default=DeviceType.AUTO, 
        description="Устройство для модели: cpu, cuda, auto"
    )
    # Кол-во воркеров модели
    model_workers_cpu: int = Field(
        default=4, 
        ge=1, le=16,
        description="Количество воркеров модели при работе на CPU"
    )
    model_workers_cuda: int = Field(
        default=2, 
        ge=1, le=4,
        description="Количество воркеров модели при работе на GPU"
    )
    
    # Предобработка
    preprocessing_workers: int = Field(
        default=4,
        ge=1, le=16,
        description="Количество потоков для препроцессинга изображений"
    )
    
    # Логи
    log_level: str = Field(default="INFO", description="Уровень логирования")
    log_file: Optional[str] = Field(default="app.log", description="Название файла лога")
    
    @computed_field
    @property
    def resolved_device(self) -> str:
        """Вычисляет финальное устройство для модели"""
        if self.model_device == DeviceType.AUTO:
            return "cuda" if torch.cuda.is_available() else "cpu"
        
        return self.model_device.value
    
    @computed_field
    @property
    def model_pool_size(self) -> int:
        """Возвращает размер пула воркеров в зависимости от устройства"""
        return self.model_workers_cuda if self.resolved_device == "cuda" else self.model_workers_cpu
    
    def print_config(self):
        """Вывод конфигурации при старте"""
        print("\n" + "="*60)
        print("EmotionTracking Service Configuration")
        print("="*60)
        print(f"Device:           {self.resolved_device} ({self.model_device.value})")
        print(f"Model workers:    {self.model_pool_size}")
        print(f"Preproc workers:  {self.preprocessing_workers}")
        print(f"Server:           {self.host}:{self.port} (uvicorn workers: {self.workers})")
        print(f"Log file:         {self.log_file}")
        print(f"CUDA available:   {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"GPU:              {torch.cuda.get_device_name(0)}")
            
        print("="*60 + "\n")


settings = AppSettings()