// Financial Analysis Dashboard JavaScript

// DOM Elements
let symbolSelector;
let timeHorizonSelector;
let analysisReportContainer;
let chartContainer;
let loadingSpinner;
let feedbackForm;
let feedbackTextarea;
let visualizationContainer;

// Current state
let currentSymbols = [];
let currentTimeHorizon = '6mo';
let predictions = [];
let chartInstances = [];

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize DOM elements
    symbolSelector = document.getElementById('symbol-selector');
    timeHorizonSelector = document.getElementById('time-horizon');
    analysisReportContainer = document.getElementById('analysis-report');
    chartContainer = document.getElementById('chart-container');
    loadingSpinner = document.getElementById('loading-spinner');
    feedbackForm = document.getElementById('feedback-form');
    feedbackTextarea = document.getElementById('feedback-content');
    visualizationContainer = document.getElementById('visualization-container');

    // Event listeners
    if (timeHorizonSelector) {
        timeHorizonSelector.addEventListener('change', (e) => {
            currentTimeHorizon = e.target.value;
            loadDashboardData();
        });
    }

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', submitAnalystFeedback);
    }

    // Initialize available assets
    loadAvailableAssets();
    
    // Load initial dashboard data
    loadDashboardData();
});

// Load available assets for selection
async function loadAvailableAssets() {
    try {
        showLoading(true);
        const response = await fetch('/api/available-assets');
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const assets = await response.json();
        
        if (symbolSelector) {
            // Clear existing options
            symbolSelector.innerHTML = '';
            
            // Add assets as checkboxes
            assets.forEach(asset => {
                const checkbox = document.createElement('div');
                checkbox.className = 'form-check form-check-inline';
                checkbox.innerHTML = `
                    <input class="form-check-input symbol-checkbox" type="checkbox" 
                           id="symbol-${asset}" value="${asset}">
                    <label class="form-check-label" for="symbol-${asset}">
                        ${asset}
                    </label>
                `;
                symbolSelector.appendChild(checkbox);
            });
            
            // Start with no assets selected
            currentSymbols = [];
            
            // Add event listeners to checkboxes
            document.querySelectorAll('.symbol-checkbox').forEach(checkbox => {
                checkbox.addEventListener('change', updateSelectedSymbols);
            });
        }
    } catch (error) {
        console.error('Error loading available assets:', error);
        showErrorMessage('Failed to load available assets. Please try again later.');
    } finally {
        showLoading(false);
    }
}

// Update the selected symbols based on checkbox changes
function updateSelectedSymbols() {
    const checkboxes = document.querySelectorAll('.symbol-checkbox:checked');
    currentSymbols = Array.from(checkboxes).map(cb => cb.value);
    
    // Reload dashboard data with new symbol selection
    if (currentSymbols.length > 0) {
        loadDashboardData();
    } else {
        showErrorMessage('Please select at least one asset to analyze.');
    }
}

// Load dashboard data based on selected parameters
async function loadDashboardData() {
    // Show message if no assets are selected
    if (currentSymbols.length === 0) {
        const containers = [chartContainer, analysisReportContainer, visualizationContainer];
        containers.forEach(container => {
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-info">
                        <h5>No Assets Selected</h5>
                        <p>Please select one or more assets from the list above to view analysis data.</p>
                    </div>
                `;
            }
        });
        return;
    }
    
    showLoading(true);
    
    try {
        // Clear existing content
        clearCharts();
        
        // Load market data
        await loadMarketData().catch(error => {
            console.error('Error loading market data:', error);
            showErrorMessage('Failed to load market data. Please try again later.');
        });
        
        // Load predictions with ARIMA model
        await loadPredictions().catch(error => {
            console.error('Error loading predictions:', error);
            // The error message is now handled in the loadPredictions function
        });
        
        // Load analysis report and visualizations
        await loadAnalysisReport().catch(error => {
            console.error('Error loading analysis report:', error);
            showErrorMessage('Failed to load analysis report. Please try again later.');
        });
        
        await loadVisualizations().catch(error => {
            console.error('Error loading visualizations:', error);
            showErrorMessage('Failed to load visualizations. Please try again later.');
        });
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showErrorMessage('Failed to load dashboard data. Please try again later.');
    } finally {
        showLoading(false);
    }
}

// Load market data from the API
async function loadMarketData() {
    try {
        const symbolsParam = currentSymbols.map(s => `symbols=${s}`).join('&');
        const response = await fetch(`/api/market-data?${symbolsParam}&time_horizon=${currentTimeHorizon}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const marketData = await response.json();
        
        // Display basic market data in the chart container
        if (chartContainer) {
            chartContainer.innerHTML = '<h4>Market Data</h4>';
            
            marketData.forEach(stock => {
                const stockDiv = document.createElement('div');
                stockDiv.className = 'card mb-4';
                
                // Get the latest data point
                const latestDataPoint = stock.data_points && stock.data_points.length > 0 ? 
                    stock.data_points[stock.data_points.length - 1] : null;
                
                if (latestDataPoint) {
                    stockDiv.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${stock.symbol} - ${stock.name}</h5>
                            <p class="text-muted">Sector: ${stock.sector}</p>
                            <div class="row">
                                <div class="col-md-6">
                                    <ul class="list-group">
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Date
                                            <span class="badge bg-primary">${latestDataPoint.date}</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Close
                                            <span class="badge bg-primary">$${latestDataPoint.close.toFixed(2)}</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Open
                                            <span class="badge bg-primary">$${latestDataPoint.open.toFixed(2)}</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            High
                                            <span class="badge bg-primary">$${latestDataPoint.high.toFixed(2)}</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Low
                                            <span class="badge bg-primary">$${latestDataPoint.low.toFixed(2)}</span>
                                        </li>
                                        <li class="list-group-item d-flex justify-content-between align-items-center">
                                            Volume
                                            <span class="badge bg-primary">${latestDataPoint.volume.toLocaleString()}</span>
                                        </li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <p>ARIMA model predictions are displayed in the "Price Predictions" tab.</p>
                                    <p class="text-muted">Click the "Price Predictions" tab to view 5-day forecasts with confidence intervals.</p>
                                </div>
                            </div>
                        </div>
                    `;
                } else {
                    stockDiv.innerHTML = `
                        <div class="card-body">
                            <h5 class="card-title">${stock.symbol}</h5>
                            <p class="text-danger">No data available for this stock.</p>
                        </div>
                    `;
                }
                
                chartContainer.appendChild(stockDiv);
            });
        }
        
        return marketData;
    } catch (error) {
        console.error('Error loading market data:', error);
        
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="alert alert-info">
                    Market data is currently being fetched. This feature is still under development.
                </div>
            `;
        }
        
        throw error;
    }
}

// Load predictions from the API
async function loadPredictions() {
    try {
        const symbolsParam = currentSymbols.map(s => `symbols=${s}`).join('&');
        const response = await fetch(`/api/predictions?${symbolsParam}&time_horizon=${currentTimeHorizon}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        predictions = await response.json();
        console.log("Predictions loaded:", predictions);
        
        // Render prediction charts
        renderPredictionCharts(predictions);
    } catch (error) {
        console.error('Error loading predictions:', error);
        
        // Show error message in the charts container
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error Loading Predictions</h5>
                    <p>There was a problem loading the price predictions. Please try again later.</p>
                    <p class="text-muted">Error details: ${error.message || 'Unknown error'}</p>
                </div>
            `;
        }
    }
}

// Load analysis report from the API
async function loadAnalysisReport() {
    try {
        const symbolsParam = currentSymbols.map(s => `symbols=${s}`).join('&');
        const response = await fetch(`/api/analysis-report?${symbolsParam}&time_horizon=${currentTimeHorizon}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const report = await response.json();
        
        // Render analysis report
        if (analysisReportContainer) {
            analysisReportContainer.innerHTML = `
                <div class="report-content">
                    <h4>Market Analysis Report</h4>
                    <p class="text-muted">Generated on: ${new Date(report.timestamp).toLocaleString()}</p>
                    <div class="assets-analyzed mb-3">
                        ${report.assets_analyzed.map(symbol => 
                            `<span class="badge bg-secondary stock-badge">${symbol}</span>`
                        ).join('')}
                    </div>
                    <div class="report-text markdown-content">
                        ${formatMarkdown(report.report)}
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading analysis report:', error);
        throw error;
    }
}

// Load visualizations from the API
async function loadVisualizations() {
    try {
        const symbolsParam = currentSymbols.map(s => `symbols=${s}`).join('&');
        const response = await fetch(`/api/visualizations?${symbolsParam}&time_horizon=${currentTimeHorizon}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const visualizationPaths = await response.json();
        
        // Render visualizations
        if (visualizationContainer) {
            visualizationContainer.innerHTML = '';
            
            if (visualizationPaths.length > 0) {
                visualizationPaths.forEach(vizInfo => {
                    const iframe = document.createElement('iframe');
                    iframe.className = 'visualization-frame';
                    iframe.src = `/static/${vizInfo.path}`;
                    iframe.title = vizInfo.title || vizInfo.symbol;
                    visualizationContainer.appendChild(iframe);
                });
            } else {
                visualizationContainer.innerHTML = '<div class="alert alert-info">No visualizations available</div>';
            }
        }
    } catch (error) {
        console.error('Error loading visualizations:', error);
        // Don't throw error here, as visualizations are optional
    }
}

// Render prediction charts
function renderPredictionCharts(predictions) {
    if (!chartContainer) return;
    
    // Clear existing charts
    chartContainer.innerHTML = '';
    
    if (!predictions || predictions.length === 0) {
        chartContainer.innerHTML = `
            <div class="alert alert-info">
                <h5>No Predictions Available</h5>
                <p>No prediction data is available for the selected assets and time horizon.</p>
                <p>Please try different assets or a different time period.</p>
            </div>
        `;
        return;
    }
    
    // Create a chart for each prediction
    predictions.forEach(prediction => {
        // Create chart container
        const chartDiv = document.createElement('div');
        chartDiv.className = 'chart-container mb-4';
        chartDiv.id = `chart-${prediction.symbol}`;
        chartContainer.appendChild(chartDiv);
        
        // Prepare data for the chart - ensure no NaN values
        const days = prediction.forecast.map(point => `Day ${point.day + 1}`);
        const forecastValues = prediction.forecast.map(point => isNaN(point.forecast) ? 0 : point.forecast);
        const lowerCI = prediction.forecast.map(point => isNaN(point.lower_ci) ? (isNaN(point.forecast) ? 0 : point.forecast * 0.9) : point.lower_ci);
        const upperCI = prediction.forecast.map(point => isNaN(point.upper_ci) ? (isNaN(point.forecast) ? 0 : point.forecast * 1.1) : point.upper_ci);
        
        // Create the chart
        const ctx = document.createElement('canvas');
        chartDiv.appendChild(ctx);
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: days,
                datasets: [
                    {
                        label: `${prediction.symbol} Forecast`,
                        data: forecastValues,
                        borderColor: '#36A2EB',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1
                    },
                    {
                        label: 'Lower CI',
                        data: lowerCI,
                        borderColor: 'rgba(255, 99, 132, 0.7)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    },
                    {
                        label: 'Upper CI',
                        data: upperCI,
                        borderColor: 'rgba(75, 192, 192, 0.7)',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: `${prediction.symbol} 5-Day Price Forecast`,
                        font: {
                            size: 16
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.dataset.label || '';
                                const value = context.raw.toFixed(2);
                                return `${label}: $${value}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'Price ($)'
                        }
                    }
                }
            }
        });
        
        chartInstances.push(chart);
        
        // Add text summary
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'chart-summary mt-2';
        
        // Calculate percent change from current price to average forecast
        const validValues = forecastValues.filter(value => !isNaN(value) && value > 0);
        const avgForecast = validValues.length > 0 ? 
            validValues.reduce((a, b) => a + b, 0) / validValues.length : 
            prediction.last_price; // Fallback to last price if no valid forecast
        
        const percentChange = prediction.last_price > 0 ? 
            ((avgForecast - prediction.last_price) / prediction.last_price) * 100 : 0;
        
        const trendClass = percentChange > 0 ? 'trend-up' : (percentChange < 0 ? 'trend-down' : 'trend-neutral');
        const trendIcon = percentChange > 0 ? '↑' : (percentChange < 0 ? '↓' : '→');
        
        summaryDiv.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">${prediction.symbol} Forecast Summary</h5>
                    <p>Current price: <strong>$${prediction.last_price.toFixed(2)}</strong></p>
                    <p>Average 5-day forecast: <strong class="${trendClass}">$${avgForecast.toFixed(2)} ${trendIcon} (${Math.abs(percentChange).toFixed(2)}%)</strong></p>
                    <p>Forecast range: <strong>${getRangeDisplay(lowerCI, upperCI)}</strong></p>
                </div>
            </div>
        `;
        
        chartDiv.appendChild(summaryDiv);
    });
}

// Submit analyst feedback
async function submitAnalystFeedback(event) {
    event.preventDefault();
    
    const feedbackContent = feedbackTextarea.value.trim();
    
    if (!feedbackContent) {
        showErrorMessage('Please provide feedback content.');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch('/api/analyst-feedback', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                feedback_content: feedbackContent,
                symbols: currentSymbols,
                time_horizon: currentTimeHorizon
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const updatedReport = await response.json();
        
        // Update analysis report
        if (analysisReportContainer) {
            analysisReportContainer.innerHTML = `
                <div class="report-content">
                    <h4>Market Analysis Report (Updated with Feedback)</h4>
                    <p class="text-muted">Generated on: ${new Date(updatedReport.timestamp).toLocaleString()}</p>
                    <div class="assets-analyzed mb-3">
                        ${updatedReport.assets_analyzed.map(symbol => 
                            `<span class="badge bg-secondary stock-badge">${symbol}</span>`
                        ).join('')}
                    </div>
                    <div class="report-text markdown-content">
                        ${formatMarkdown(updatedReport.report)}
                    </div>
                </div>
            `;
        }
        
        // Clear feedback textarea
        feedbackTextarea.value = '';
        
        // Show success message
        showSuccessMessage('Feedback submitted successfully and report updated.');
        
        // Reload visualizations
        await loadVisualizations();
    } catch (error) {
        console.error('Error submitting analyst feedback:', error);
        showErrorMessage('Failed to submit feedback. Please try again later.');
    } finally {
        showLoading(false);
    }
}

// Clear all charts
function clearCharts() {
    // Destroy chart instances
    chartInstances.forEach(chart => chart.destroy());
    chartInstances = [];
    
    if (chartContainer) {
        chartContainer.innerHTML = '';
    }
}

// Show/hide loading spinner
function showLoading(show) {
    if (loadingSpinner) {
        loadingSpinner.style.display = show ? 'flex' : 'none';
    }
}

// Show error message
function showErrorMessage(message) {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }
}

// Show success message
function showSuccessMessage(message) {
    const alertContainer = document.getElementById('alert-container');
    if (alertContainer) {
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.role = 'alert';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        alertContainer.appendChild(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 150);
        }, 5000);
    }
}

// Helper function to get a formatted range display from arrays
function getRangeDisplay(lowerArray, upperArray) {
    // Filter out NaN values
    const validLower = lowerArray.filter(val => !isNaN(val));
    const validUpper = upperArray.filter(val => !isNaN(val));
    
    if (validLower.length === 0 || validUpper.length === 0) {
        return "Range not available";
    }
    
    // Find min and max from valid values
    const minValue = Math.min(...validLower);
    const maxValue = Math.max(...validUpper);
    
    return `$${minValue.toFixed(2)} - $${maxValue.toFixed(2)}`;
}

// Format markdown text to HTML
function formatMarkdown(text) {
    if (!text) return '';
    
    // Basic Markdown formatting
    let html = text
        // Headers
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^#### (.*$)/gm, '<h4>$1</h4>')
        .replace(/^##### (.*$)/gm, '<h5>$1</h5>')
        
        // Bold and Italic
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/__(.*?)__/g, '<strong>$1</strong>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        
        // Lists
        .replace(/^\s*\d+\.\s+(.*$)/gm, '<li>$1</li>')
        .replace(/^\s*[\-\*]\s+(.*$)/gm, '<li>$1</li>')
        
        // Links
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        
        // Code
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        
        // Blockquotes
        .replace(/^\> (.*$)/gm, '<blockquote>$1</blockquote>')
        
        // Paragraphs and line breaks
        .replace(/\n\s*\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Wrap the HTML in a paragraph tag
    html = '<p>' + html + '</p>';
    
    // Fix list items (wrap in ul)
    if (html.includes('<li>')) {
        html = html.replace(/<p>(\s*<li>)/g, '<p><ul>$1')
                   .replace(/(<\/li>\s*)<\/p>/g, '$1</ul></p>');
    }
    
    return html;
}
