import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import load_dataset
from .models import FineTuningJob, TrainingConfig, JobStatus

class TrainingManager:
    def __init__(self):
        self.jobs: Dict[str, FineTuningJob] = {}
        self.active_processes: Dict[str, asyncio.Task] = {}

    async def start_training(self, model_name: str, dataset_path: str, config: TrainingConfig) -> str:
        job_id = str(uuid.uuid4())
        
        job = FineTuningJob(
            job_id=job_id,
            status=JobStatus.PENDING,
            config=config,
            created_at=datetime.now()
        )
        
        self.jobs[job_id] = job
        
        task = asyncio.create_task(self._run_training(job_id))
        self.active_processes[job_id] = task
        
        return job_id

    async def _run_training(self, job_id: str):
        job = self.jobs[job_id]
        
        try:
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now()
            
            await self._execute_training(job)
            
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.progress = 100.0
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
        
        finally:
            if job_id in self.active_processes:
                del self.active_processes[job_id]

    async def _execute_training(self, job: FineTuningJob):
        config = job.config
        
        tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        model = AutoModelForCausalLM.from_pretrained(
            config.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        if config.use_lora:
            peft_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=config.lora_r,
                lora_alpha=config.lora_alpha,
                lora_dropout=config.lora_dropout,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]
            )
            model = get_peft_model(model, peft_config)
        
        dataset = load_dataset('json', data_files=config.dataset_path, split='train')
        
        def tokenize_function(examples):
            return tokenizer(
                examples['text'],
                truncation=True,
                padding=True,
                max_length=config.max_length,
                return_tensors="pt"
            )
        
        tokenized_dataset = dataset.map(tokenize_function, batched=True)
        
        training_args = TrainingArguments(
            output_dir=config.output_dir,
            num_train_epochs=config.num_epochs,
            per_device_train_batch_size=config.batch_size,
            learning_rate=config.learning_rate,
            warmup_steps=config.warmup_steps,
            logging_steps=config.logging_steps,
            save_steps=config.save_steps,
            evaluation_strategy=config.evaluation_strategy,
            eval_steps=config.eval_steps,
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
            dataloader_pin_memory=False,
        )
        
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=tokenizer,
            mlm=False,
        )
        
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        job.total_steps = len(tokenized_dataset) // config.batch_size * config.num_epochs
        
        class ProgressCallback:
            def __init__(self, job_ref):
                self.job = job_ref
            
            def on_step_end(self, args, state, control, **kwargs):
                self.job.current_step = state.global_step
                self.job.progress = (state.global_step / self.job.total_steps) * 100
        
        trainer.add_callback(ProgressCallback(job))
        
        await asyncio.get_event_loop().run_in_executor(None, trainer.train)
        
        model.save_pretrained(config.output_dir)
        tokenizer.save_pretrained(config.output_dir)

    async def get_job(self, job_id: str) -> Optional[FineTuningJob]:
        return self.jobs.get(job_id)

    async def get_all_jobs(self) -> List[FineTuningJob]:
        return list(self.jobs.values())

    async def cancel_job(self, job_id: str) -> bool:
        if job_id in self.active_processes:
            self.active_processes[job_id].cancel()
            del self.active_processes[job_id]
            
            if job_id in self.jobs:
                self.jobs[job_id].status = JobStatus.CANCELLED
                self.jobs[job_id].completed_at = datetime.now()
            
            return True
        return False