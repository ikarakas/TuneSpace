class Dashboard {
    constructor() {
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.refreshJobs();
        this.startAutoRefresh();
    }

    async refreshJobs() {
        try {
            const response = await fetch('/api/tuning/jobs');
            const result = await response.json();
            
            this.renderJobsTable(result.jobs);
        } catch (error) {
            console.error('Failed to refresh jobs:', error);
            this.showError('Failed to load jobs');
        }
    }

    renderJobsTable(jobs) {
        const container = document.getElementById('jobsTable');
        
        if (!jobs || jobs.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted py-4">
                    <i class="fas fa-inbox fa-3x mb-3"></i>
                    <p>No training jobs yet. Start your first training job above!</p>
                </div>
            `;
            return;
        }

        const table = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Job ID</th>
                            <th>Model</th>
                            <th>Status</th>
                            <th>Progress</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${jobs.map(job => this.renderJobRow(job)).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        container.innerHTML = table;
    }

    renderJobRow(job) {
        const statusClass = this.getStatusClass(job.status);
        const progress = job.progress || 0;
        const createdAt = new Date(job.created_at).toLocaleString();
        
        return `
            <tr>
                <td>
                    <code class="text-muted">${job.job_id.substring(0, 8)}...</code>
                </td>
                <td>${job.config.model_name}</td>
                <td>
                    <span class="job-status ${statusClass}">${job.status}</span>
                </td>
                <td>
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar ${this.getProgressBarClass(job.status)}" 
                             role="progressbar" 
                             style="width: ${progress}%" 
                             aria-valuenow="${progress}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                            ${progress.toFixed(1)}%
                        </div>
                    </div>
                    ${job.current_step ? `<small class="text-muted">Step ${job.current_step}/${job.total_steps}</small>` : ''}
                </td>
                <td>${createdAt}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="dashboard.viewJob('${job.job_id}')" title="View Details">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${job.status === 'running' ? 
                            `<button class="btn btn-outline-danger" onclick="dashboard.cancelJob('${job.job_id}')" title="Cancel">
                                <i class="fas fa-stop"></i>
                            </button>` : ''
                        }
                    </div>
                </td>
            </tr>
        `;
    }

    getStatusClass(status) {
        const statusMap = {
            'pending': 'status-pending',
            'running': 'status-running',
            'completed': 'status-completed',
            'failed': 'status-failed',
            'cancelled': 'status-cancelled'
        };
        return statusMap[status] || 'status-pending';
    }

    getProgressBarClass(status) {
        const classMap = {
            'running': 'bg-primary',
            'completed': 'bg-success',
            'failed': 'bg-danger',
            'cancelled': 'bg-warning'
        };
        return classMap[status] || 'bg-secondary';
    }

    async viewJob(jobId) {
        try {
            const response = await fetch(`/api/tuning/jobs/${jobId}`);
            const job = await response.json();
            
            this.showJobModal(job);
        } catch (error) {
            console.error('Failed to load job details:', error);
            this.showError('Failed to load job details');
        }
    }

    showJobModal(job) {
        const modalHtml = `
            <div class="modal fade" id="jobModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Job Details: ${job.job_id.substring(0, 8)}...</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Configuration</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Model:</strong> ${job.config.model_name}</li>
                                        <li><strong>Dataset:</strong> ${job.config.dataset_path}</li>
                                        <li><strong>Learning Rate:</strong> ${job.config.learning_rate}</li>
                                        <li><strong>Epochs:</strong> ${job.config.num_epochs}</li>
                                        <li><strong>Batch Size:</strong> ${job.config.batch_size}</li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <h6>Status</h6>
                                    <ul class="list-unstyled">
                                        <li><strong>Status:</strong> <span class="job-status ${this.getStatusClass(job.status)}">${job.status}</span></li>
                                        <li><strong>Progress:</strong> ${(job.progress || 0).toFixed(1)}%</li>
                                        <li><strong>Created:</strong> ${new Date(job.created_at).toLocaleString()}</li>
                                        ${job.started_at ? `<li><strong>Started:</strong> ${new Date(job.started_at).toLocaleString()}</li>` : ''}
                                        ${job.completed_at ? `<li><strong>Completed:</strong> ${new Date(job.completed_at).toLocaleString()}</li>` : ''}
                                    </ul>
                                </div>
                            </div>
                            ${job.error_message ? `
                                <div class="mt-3">
                                    <h6>Error Message</h6>
                                    <div class="alert alert-danger">
                                        <pre class="mb-0">${job.error_message}</pre>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('jobModal'));
        modal.show();
        
        document.getElementById('jobModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    async cancelJob(jobId) {
        if (!confirm('Are you sure you want to cancel this job?')) {
            return;
        }

        try {
            const response = await fetch(`/api/tuning/jobs/${jobId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.showSuccess('Job cancelled successfully');
                this.refreshJobs();
            } else {
                const result = await response.json();
                this.showError(`Failed to cancel job: ${result.detail}`);
            }
        } catch (error) {
            console.error('Failed to cancel job:', error);
            this.showError('Failed to cancel job');
        }
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.refreshJobs();
        }, 5000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showSuccess(message) {
        this.showAlert(message, 'success');
    }

    showError(message) {
        this.showAlert(message, 'danger');
    }

    showAlert(message, type) {
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
}

const dashboard = new Dashboard();

function refreshJobs() {
    dashboard.refreshJobs();
}

window.addEventListener('beforeunload', () => {
    dashboard.stopAutoRefresh();
});