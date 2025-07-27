from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from core.training import TrainingManager
from core.models import FineTuningJob, TrainingConfig

tuning_router = APIRouter()
data_router = APIRouter()

class TrainingRequest(BaseModel):
    model_name: str
    dataset_path: str
    output_dir: str
    learning_rate: float = 2e-5
    batch_size: int = 4
    num_epochs: int = 3
    max_length: int = 512

@tuning_router.post("/start")
async def start_training(request: TrainingRequest):
    try:
        training_manager = TrainingManager()
        job_id = await training_manager.start_training(
            model_name=request.model_name,
            dataset_path=request.dataset_path,
            config=TrainingConfig(**request.dict())
        )
        return {"job_id": job_id, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@tuning_router.get("/jobs")
async def list_jobs():
    training_manager = TrainingManager()
    jobs = await training_manager.get_all_jobs()
    return {"jobs": jobs}

@tuning_router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    training_manager = TrainingManager()
    job = await training_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@tuning_router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    training_manager = TrainingManager()
    success = await training_manager.cancel_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"status": "cancelled"}

@data_router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(('.json', '.csv', '.jsonl')):
        raise HTTPException(status_code=400, detail="Only JSON, CSV, and JSONL files are supported")
    
    file_path = f"data/{file.filename}"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"filename": file.filename, "path": file_path}

@data_router.get("/datasets")
async def list_datasets():
    import os
    datasets = []
    if os.path.exists("data"):
        for file in os.listdir("data"):
            if file.endswith(('.json', '.csv', '.jsonl')):
                datasets.append({
                    "name": file,
                    "path": f"data/{file}",
                    "size": os.path.getsize(f"data/{file}")
                })
    return {"datasets": datasets}