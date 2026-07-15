// Common Chart Defaults
Chart.defaults.color = document.documentElement.getAttribute('data-theme') === 'dark' ? '#e0e0e0' : '#212529';
Chart.defaults.font.family = "'Inter', sans-serif";

let ec2StatusChart, storageUsageChart, costChart, rdsChart, dynamoChart;

function updateChartsTheme() {
    const textColor = document.documentElement.getAttribute('data-theme') === 'dark' ? '#e0e0e0' : '#212529';
    Chart.defaults.color = textColor;
    
    if(ec2StatusChart) { ec2StatusChart.options.plugins.legend.labels.color = textColor; ec2StatusChart.update(); }
    if(rdsChart) { rdsChart.options.plugins.legend.labels.color = textColor; rdsChart.update(); }
    if(storageUsageChart) { storageUsageChart.options.plugins.legend.labels.color = textColor; storageUsageChart.update(); }
    if(dynamoChart) {
        dynamoChart.options.scales.x.ticks.color = textColor;
        dynamoChart.options.scales.y.ticks.color = textColor;
        dynamoChart.update();
    }
    if(costChart) {
        costChart.options.scales.x.ticks.color = textColor;
        costChart.options.scales.y.ticks.color = textColor;
        costChart.update();
    }
}

async function renderDashboardCharts() {
    const ctxEC2 = document.getElementById('ec2Chart');
    const ctxStorage = document.getElementById('storageChart');
    
    if(ctxEC2 && ctxStorage) {
        try {
            const metrics = await apiGet(`/api/monitoring/metrics?t=${new Date().getTime()}`);
            
            // EC2 Doughnut Chart
            ec2StatusChart = new Chart(ctxEC2, {
                type: 'doughnut',
                data: {
                    labels: ['Running', 'Stopped'],
                    datasets: [{
                        data: [metrics.running_ec2, metrics.stopped_ec2],
                        backgroundColor: ['#198754', '#dc3545'],
                        borderWidth: 0
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
            
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
            
            // RDS Status Distribution Chart
            const ctxRDS = document.getElementById('rdsChart');
            if (ctxRDS) {
                try {
                    const rdsMetrics = await apiGet(`/api/monitoring/rds_stats?t=${new Date().getTime()}`);
                    rdsChart = new Chart(ctxRDS, {
                        type: 'doughnut',
                        data: {
                            labels: ['Available', 'Stopped', 'Other'],
                            datasets: [{
                                data: [rdsMetrics.available || 0, rdsMetrics.stopped || 0, rdsMetrics.other || 0],
                                backgroundColor: ['#198754', '#dc3545', '#ffc107'],
                                borderWidth: 0
                            }]
                        },
                        options: { responsive: true, maintainAspectRatio: false }
                    });
                } catch (e) {
                    console.error("Failed to load RDS stats:", e);
                }
            }
            
            // DynamoDB Item Counts Chart
            const ctxDynamo = document.getElementById('dynamoChart');
            if (ctxDynamo) {
                try {
                    const dynamoMetrics = await apiGet(`/api/monitoring/dynamo_stats?t=${new Date().getTime()}`);
                    let dLabels = dynamoMetrics.labels && dynamoMetrics.labels.length > 0 ? dynamoMetrics.labels : ['No Data'];
                    let dData = dynamoMetrics.data && dynamoMetrics.data.length > 0 ? dynamoMetrics.data : [0];
                    
                    dynamoChart = new Chart(ctxDynamo, {
                        type: 'bar',
                        data: {
                            labels: dLabels,
                            datasets: [{
                                label: 'Item Count',
                                data: dData,
                                backgroundColor: '#6f42c1',
                                borderRadius: 4
                            }]
                        },
                        options: { 
                            responsive: true, 
                            maintainAspectRatio: false,
                            indexAxis: 'y' // Horizontal bar chart
                        }
                    });
                } catch (e) {
                    console.error("Failed to load DynamoDB stats:", e);
                }
            }
            
        } catch (e) {
            console.log("Error loading dashboard charts:", e);
        }
    }
}
