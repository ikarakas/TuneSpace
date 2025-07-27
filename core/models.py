from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TrainingConfig(BaseModel):
    model_name: str
    dataset_path: str
    output_dir: str
    learning_rate: float = 2e-5
    batch_size: int = 4
    num_epochs: int = 3
    max_length: int = 512
    warmup_steps: int = 500
    logging_steps: int = 50
    save_steps: int = 1000
    evaluation_strategy: str = "steps"
    eval_steps: int = 500
    use_lora: bool = True
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.1

class FineTuningJob(BaseModel):
    job_id: str
    status: JobStatus
    config: TrainingConfig
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    progress: float = 0.0
    current_step: int = 0
    total_steps: int = 0

class ModelInfo(BaseModel):
    name: str
    type: str
    size: str
    description: str
    supported_tasks: list

class DatasetInfo(BaseModel):
    name: str
    path: str
    size: int
    format: str
    num_samples: Optional[int] = None
    columns: Optional[list] = None