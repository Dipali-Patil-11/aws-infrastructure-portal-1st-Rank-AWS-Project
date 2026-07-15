// Common Chart Defaults
Chart.defaults.color = document.documentElement.getAttribute('data-theme') === 'dark' ? '#e0e0e0' : '#212529';
Chart.defaults.font.family = "'Inter', sans-serif";

let lambdaChart, storageUsageChart, costChart, apiChart;

function updateChartsTheme() {
    const textColor = document.documentElement.getAttribute('data-theme') === 'dark' ? '#e0e0e0' : '#212529';
    Chart.defaults.color = textColor;
    
    if(lambdaChart) { lambdaChart.options.plugins.legend.labels.color = textColor; lambdaChart.update(); }
    if(apiChart) { apiChart.options.plugins.legend.labels.color = textColor; apiChart.update(); }
    if(storageUsageChart) { storageUsageChart.options.plugins.legend.labels.color = textColor; storageUsageChart.update(); }
    if(costChart) {
        costChart.options.scales.x.ticks.color = textColor;
        costChart.options.scales.y.ticks.color = textColor;
        costChart.update();
    }
}

async function renderDashboardCharts() {
    const ctxLambda = document.getElementById('lambdaChart');
    const ctxStorage = document.getElementById('storageChart');
    
    if(ctxLambda && ctxStorage) {
        try {
            // Lambda Runtime Doughnut Chart
            try {
                const lambdaMetrics = await apiGet(`/api/monitoring/lambda_stats?t=${new Date().getTime()}`);
                lambdaChart = new Chart(ctxLambda, {
                    type: 'doughnut',
                    data: {
                        labels: lambdaMetrics.labels && lambdaMetrics.labels.length > 0 ? lambdaMetrics.labels : ['No Data'],
                        datasets: [{
                            data: lambdaMetrics.data && lambdaMetrics.data.length > 0 ? lambdaMetrics.data : [1],
                            backgroundColor: ['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#fd7e14', '#198754', '#20c997', '#0dcaf0'],
                            borderWidth: 0
                        }]
                    },
                    options: { responsive: true, maintainAspectRatio: false }
                });
            } catch (err) {
                console.error("Failed to load Lambda metrics:", err);
            }

            
            // Storage Bar Chart (Real data)
            let storageLabels = ['No Data'];
            let storageData = [0];
            try {
                const storageMetrics = await apiGet(`/api/monitoring/storage_usage?t=${new Date().getTime()}`);
                if (storageMetrics.labels && storageMetrics.labels.length > 0) {
                    storageLabels = storageMetrics.labels;
                    storageData = storageMetrics.data;
                }
            } catch (err) {
                console.error("Failed to load storage metrics:", err);
            }
            
            storageUsageChart = new Chart(ctxStorage, {
                type: 'bar',
                data: {
                    labels: storageLabels,
                    datasets: [{
                        label: 'Storage (GB)',
                        data: storageData,
                        backgroundColor: '#0d6efd',
                        borderRadius: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
            // API Gateway Endpoint Types Chart
            const ctxApi = document.getElementById('apiChart');
            if (ctxApi) {
                try {
                    const apiMetrics = await apiGet(`/api/monitoring/api_stats?t=${new Date().getTime()}`);
                    apiChart = new Chart(ctxApi, {
                        type: 'doughnut',
                        data: {
                            labels: apiMetrics.labels && apiMetrics.labels.length > 0 ? apiMetrics.labels : ['No Data'],
                            datasets: [{
                                data: apiMetrics.data && apiMetrics.data.length > 0 ? apiMetrics.data : [1],
                                backgroundColor: ['#ffc107', '#17a2b8', '#dc3545'],
                                borderWidth: 0
                            }]
                        },
                        options: { responsive: true, maintainAspectRatio: false }
                    });
                } catch (e) {
                    console.error("Failed to load API Gateway stats:", e);
                }
            }
            
        } catch (e) {
            console.log("Error loading dashboard charts:", e);
        }
    }
}
