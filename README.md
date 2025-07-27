# TuneSpace - LLM Fine-tuning Platform

A web-based platform for fine-tuning Large Language Models with an intuitive interface and robust backend.

## Features

- **Easy Model Fine-tuning**: Support for popular models (GPT-2, DialoGPT, OPT, etc.)
- **LoRA Fine-tuning**: Efficient parameter-efficient fine-tuning using LoRA
- **Web Interface**: Clean, responsive dashboard for managing training jobs
- **Real-time Monitoring**: Track training progress and metrics
- **Dataset Management**: Upload and manage training datasets
- **Job Queue**: Manage multiple concurrent training jobs

## Quick Start

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (recommended)
- 8GB+ RAM

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ikarakas/TuneSpace.git
cd TuneSpace
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:9090`.

## Usage

### Uploading Datasets

1. Navigate to the Dashboard
2. Use the "Upload Dataset" form to upload your training data
3. Supported formats: JSON, CSV, JSONL

### Starting Training

1. Select a pre-trained model from the dropdown
2. Choose your uploaded dataset
3. Configure training parameters (learning rate, epochs, etc.)
4. Click "Start Training"

### Monitoring Jobs

- View all training jobs in the jobs table
- Click the eye icon to view detailed job information
- Monitor real-time progress and metrics

## Configuration

Key configuration options in `.env`:

- `DATABASE_URL`: Database connection string
- `HF_TOKEN`: HuggingFace API token for model access
- `DEFAULT_OUTPUT_DIR`: Where to save trained models
- `MAX_CONCURRENT_JOBS`: Maximum number of concurrent training jobs

## API Endpoints

### Training Jobs
- `POST /api/tuning/start` - Start a new training job
- `GET /api/tuning/jobs` - List all jobs
- `GET /api/tuning/jobs/{job_id}` - Get job details
- `DELETE /api/tuning/jobs/{job_id}` - Cancel a job

### Data Management
- `POST /api/data/upload` - Upload a dataset
- `GET /api/data/datasets` - List uploaded datasets

## Development

### Project Structure

```
TuneSpace/
├── app.py                 # Main FastAPI application
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── api/                  # API routes
│   ├── __init__.py
│   └── routes.py
├── core/                 # Core business logic
│   ├── __init__.py
│   ├── models.py        # Data models
│   └── training.py      # Training logic
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
├── static/             # Static assets
│   ├── css/
│   └── js/
├── data/               # Uploaded datasets
├── logs/               # Application logs
└── tests/              # Test files
```

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black .
flake8 .
```

## License

This project is licensed under the MIT License.
