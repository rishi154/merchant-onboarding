/**
 * Human Review Panel JavaScript
 */

class ReviewPanel {
    constructor(applicationId) {
        this.applicationId = applicationId;
        this.reviewData = null;
        this.init();
    }

    init() {
        this.createReviewPanel();
        this.bindEvents();
    }

    createReviewPanel() {
        const container = document.getElementById('review-panel-container');
        if (!container) {
            console.error('Review panel container not found');
            return;
        }

        const existingPanel = document.getElementById('review-panel');
        if (existingPanel) {
            existingPanel.remove();
        }

        const panel = document.createElement('div');
        panel.id = 'review-panel';
        panel.className = 'review-panel hidden';
        panel.innerHTML = `
            <div class="review-header">
                <h3>👤 Human Review Required</h3>
                <span class="agent-name" id="review-agent-name"></span>
            </div>
            
            <div class="agent-result-summary" id="agent-result-summary">
                <!-- Agent result will be displayed here -->
            </div>
            
            <div class="review-actions">
                <button class="btn btn-success" id="approve-btn">
                    ✅ Approve & Continue
                </button>
                <button class="btn btn-danger" id="reject-btn">
                    ❌ Reject & Stop
                </button>
                <button class="btn btn-warning" id="changes-btn">
                    🔄 Request Changes
                </button>
            </div>
            
            <div class="review-notes">
                <label for="reviewer-notes">Review Notes:</label>
                <textarea id="reviewer-notes" placeholder="Add your review comments..."></textarea>
            </div>
            
            <div class="review-submit">
                <button class="btn btn-primary" id="submit-decision">
                    Submit Decision
                </button>
            </div>
        `;

        container.appendChild(panel);
        console.log('Review panel created and added to container');
    }

    bindEvents() {
        document.getElementById('approve-btn').addEventListener('click', () => {
            this.selectDecision('approved');
        });

        document.getElementById('reject-btn').addEventListener('click', () => {
            this.selectDecision('rejected');
        });

        document.getElementById('changes-btn').addEventListener('click', () => {
            this.selectDecision('changes_requested');
        });

        document.getElementById('submit-decision').addEventListener('click', () => {
            this.submitDecision();
        });
    }

    selectDecision(decision) {
        document.querySelectorAll('.review-actions .btn').forEach(btn => {
            btn.classList.remove('selected');
        });

        const buttonMap = {
            'approved': 'approve-btn',
            'rejected': 'reject-btn',
            'changes_requested': 'changes-btn'
        };

        document.getElementById(buttonMap[decision]).classList.add('selected');
        this.selectedDecision = decision;
    }

    async submitDecision() {
        if (!this.selectedDecision) {
            alert('Please select a decision first');
            return;
        }

        const notes = document.getElementById('reviewer-notes').value;

        try {
            const response = await fetch(`/api/applications/${this.applicationId}/review-decision`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    decision: this.selectedDecision,
                    notes: notes,
                    reviewer: 'current_user'
                })
            });

            const result = await response.json();

            if (result.success) {
                this.hidePanel();
                if (this.selectedDecision === 'approved') {
                    this.updateStatus('Resuming workflow...');
                } else if (this.selectedDecision === 'rejected') {
                    this.updateStatus('Application declined');
                }
            } else {
                alert('Error submitting decision: ' + result.error);
            }
        } catch (error) {
            console.error('Error submitting decision:', error);
            alert('Error submitting decision');
        }
    }

    showReview(reviewData) {
        console.log('showReview called with:', reviewData);
        this.reviewData = reviewData;
        
        const panel = document.getElementById('review-panel');
        if (!panel) {
            console.error('Review panel not found when trying to show');
            return;
        }
        
        const agentNameElement = document.getElementById('review-agent-name');
        if (agentNameElement) {
            agentNameElement.textContent = reviewData.review_agent || 'Unknown Agent';
        }
        
        const resultSummary = this.formatAgentResult(reviewData.review_data);
        const summaryElement = document.getElementById('agent-result-summary');
        if (summaryElement) {
            summaryElement.innerHTML = resultSummary;
        }
        
        panel.classList.remove('hidden');
        console.log('Review panel should now be visible');
    }

    hidePanel() {
        document.getElementById('review-panel').classList.add('hidden');
    }

    formatAgentResult(agentResult) {
        if (!agentResult) return '<p>No result data available</p>';

        const container = document.createElement('div');
        container.className = 'agent-result-details';
        
        if (agentResult.confidence) {
            const metricDiv = document.createElement('div');
            metricDiv.className = 'metric';
            
            const label = document.createElement('label');
            label.textContent = 'Confidence:';
            
            const span = document.createElement('span');
            span.textContent = agentResult.confidence + '%';
            
            metricDiv.appendChild(label);
            metricDiv.appendChild(span);
            container.appendChild(metricDiv);
        }

        if (agentResult.risk_score) {
            const metricDiv = document.createElement('div');
            metricDiv.className = 'metric';
            
            const label = document.createElement('label');
            label.textContent = 'Risk Score:';
            
            const span = document.createElement('span');
            span.textContent = String(agentResult.risk_score);
            
            metricDiv.appendChild(label);
            metricDiv.appendChild(span);
            container.appendChild(metricDiv);
        }

        const details = document.createElement('details');
        details.className = 'raw-data';
        
        const summary = document.createElement('summary');
        summary.textContent = 'View Details';
        
        const pre = document.createElement('pre');
        pre.textContent = JSON.stringify(agentResult, null, 2);
        
        details.appendChild(summary);
        details.appendChild(pre);
        container.appendChild(details);

        return container.outerHTML;
    }

    updateStatus(status) {
        const statusElement = document.querySelector('.status-text');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
}

window.ReviewPanel = ReviewPanel;