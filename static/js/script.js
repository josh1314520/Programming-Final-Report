document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('simulateForm');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const chartPlaceholder = document.getElementById('chartPlaceholder');
    const summaryCard = document.getElementById('summaryCard');
    
    let growthChart = null;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Reset UI
        errorMessage.classList.add('d-none');
        submitBtn.disabled = true;
        loadingSpinner.classList.remove('d-none');
        
        const payload = {
            ticker: document.getElementById('ticker').value,
            monthly_investment: document.getElementById('monthlyInvestment').value,
            years: document.getElementById('years').value
        };

        try {
            const response = await fetch('/api/simulate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '發生未知錯誤');
            }

            // Success, render chart and summary
            renderSummary(data.summary);
            renderChart(data.labels, data.investment, data.value);
            
            chartPlaceholder.classList.add('d-none');
            summaryCard.classList.remove('d-none');

        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.classList.remove('d-none');
            summaryCard.classList.add('d-none');
        } finally {
            submitBtn.disabled = false;
            loadingSpinner.classList.add('d-none');
        }
    });

    function renderSummary(summary) {
        document.getElementById('sumInvested').textContent = summary.total_invested.toLocaleString();
        document.getElementById('sumValue').textContent = summary.final_value.toLocaleString();
        
        const returnEl = document.getElementById('sumReturn');
        returnEl.textContent = `${summary.total_return_pct}%`;
        
        if (summary.total_return_pct >= 0) {
            returnEl.className = 'text-success mb-0';
            returnEl.textContent = '+' + returnEl.textContent;
        } else {
            returnEl.className = 'text-danger mb-0';
        }
    }

    function renderChart(labels, investment, value) {
        const ctx = document.getElementById('growthChart').getContext('2d');
        
        if (growthChart) {
            growthChart.destroy();
        }

        growthChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '累積資產市值',
                        data: value,
                        borderColor: '#10b981', // Emerald 500
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        fill: true,
                        tension: 0.1
                    },
                    {
                        label: '累積投入成本',
                        data: investment,
                        borderColor: '#3b82f6', // Blue 500
                        borderWidth: 2,
                        borderDash: [5, 5],
                        pointRadius: 0,
                        pointHoverRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        labels: {
                            color: '#f8fafc'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(15, 23, 42, 0.9)',
                        titleColor: '#f8fafc',
                        bodyColor: '#e2e8f0',
                        borderColor: 'rgba(255,255,255,0.1)',
                        borderWidth: 1,
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.parsed.y !== null) {
                                    label += context.parsed.y.toLocaleString();
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            maxTicksLimit: 12
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                if (value >= 1000000) {
                                    return (value / 1000000).toFixed(1) + 'M';
                                } else if (value >= 1000) {
                                    return (value / 1000).toFixed(1) + 'k';
                                }
                                return value;
                            }
                        }
                    }
                }
            }
        });
    }
});
