class TuneSpaceApp {
    constructor() {
        this.baseUrl = window.location.origin;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDatasets();
    }

    setupEventListeners() {
        document.addEventListener('DOMContentLoaded', () => {
            const uploadForm = document.getElementById('uploadForm');
            if (uploadForm) {
                uploadForm.addEventListener('submit', this.handleUpload.bind(this));
            }

            const trainingForm = document.getElementById('trainingForm');
            if (trainingForm) {
                trainingForm.addEventListener('submit', this.handleTraining.bind(this));
            }
        });
    }

    async handleUpload(event) {
        event.preventDefault();
        
        const formData = new FormData();
        const fileInput = document.getElementById('datasetFile');
        const file = fileInput.files[0];
        
        if (!file) {
            this.showAlert('Please select a file', 'warning');
            return;
        }

        formData.append('file', file);

        try {
            this.showSpinner(event.target);
            
            const response = await fetch(`${this.baseUrl}/api/data/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(`File uploaded successfully: ${result.filename}`, 'success');
                fileInput.value = '';
                this.loadDatasets();
            } else {
                this.showAlert(`Upload failed: ${result.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Upload error: ${error.message}`, 'danger');
        } finally {
            this.hideSpinner(event.target);
        }
    }

    async handleTraining(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const trainingData = {
            model_name: formData.get('modelName') || document.getElementById('modelName').value,
            dataset_path: formData.get('datasetPath') || document.getElementById('datasetPath').value,
            output_dir: `./models/${Date.now()}`,
            learning_rate: parseFloat(formData.get('learningRate') || document.getElementById('learningRate').value),
            num_epochs: parseInt(formData.get('numEpochs') || document.getElementById('numEpochs').value),
            batch_size: 4,
            max_length: 512
        };

        if (!trainingData.model_name || !trainingData.dataset_path) {
            this.showAlert('Please select both model and dataset', 'warning');
            return;
        }

        try {
            this.showSpinner(event.target);
            
            const response = await fetch(`${this.baseUrl}/api/tuning/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(trainingData)
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(`Training started! Job ID: ${result.job_id}`, 'success');
                event.target.reset();
                
                if (typeof refreshJobs === 'function') {
                    refreshJobs();
                }
            } else {
                this.showAlert(`Training failed: ${result.detail}`, 'danger');
            }
        } catch (error) {
            this.showAlert(`Training error: ${error.message}`, 'danger');
        } finally {
            this.hideSpinner(event.target);
        }
    }

    async loadDatasets() {
        try {
            const response = await fetch(`${this.baseUrl}/api/data/datasets`);
            const result = await response.json();
            
            const select = document.getElementById('datasetPath');
            if (select) {
                select.innerHTML = '<option value="">Select dataset...</option>';
                
                result.datasets.forEach(dataset => {
                    const option = document.createElement('option');
                    option.value = dataset.path;
                    option.textContent = `${dataset.name} (${this.formatFileSize(dataset.size)})`;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Failed to load datasets:', error);
        }
    }

    showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.insertBefore(alertDiv, container.firstChild);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    showSpinner(element) {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = '<div class="spinner-border text-primary" role="status"></div>';
        
        element.style.position = 'relative';
        element.appendChild(spinner);
    }

    hideSpinner(element) {
        const spinner = element.querySelector('.spinner-overlay');
        if (spinner) {
            spinner.remove();
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

const app = new TuneSpaceApp();