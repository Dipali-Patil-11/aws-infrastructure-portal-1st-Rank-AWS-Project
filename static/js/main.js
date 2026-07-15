// Theme toggling logic
const themeToggleBtn = document.getElementById('theme-toggle');
const currentTheme = localStorage.getItem('theme') || 'light';

document.documentElement.setAttribute('data-theme', currentTheme);

if(themeToggleBtn) {
    if(currentTheme === 'dark') {
        themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    themeToggleBtn.addEventListener('click', () => {
        let theme = document.documentElement.getAttribute('data-theme');
        if (theme === 'dark') {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
        } else {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
        }
        
        // Re-render charts if they exist on the page
        if (typeof updateChartsTheme === 'function') {
            updateChartsTheme();
        }
    });
}

async function loadDashboardMetrics() {
    try {
        const metrics = await apiGet(`/api/monitoring/metrics?t=${new Date().getTime()}`);
        
        const ec2El = document.getElementById('dash-ec2');
        const s3El = document.getElementById('dash-s3');
        const regionEl = document.getElementById('dash-region');
        const apiEl = document.getElementById('dash-api');
        const lambdaEl = document.getElementById('dash-lambda');
        
        if (s3El) s3El.innerText = metrics.s3_buckets;
        if (regionEl) regionEl.innerText = metrics.region;
        if (apiEl) apiEl.innerText = metrics.api_gateways !== undefined ? metrics.api_gateways : '--';
        if (lambdaEl) lambdaEl.innerText = metrics.lambda_functions !== undefined ? metrics.lambda_functions : '--';
        
    } catch (e) {
        console.error('Error loading dashboard metrics', e);
    }
}

// Toast notification function
function showToast(title, message, type='success') {
    const toastContainer = document.getElementById('toast-container');
    if(!toastContainer) return;

    const icon = type === 'success' ? 'fa-check-circle text-success' : 'fa-exclamation-circle text-danger';
    
    const toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center mb-2';
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    
    toastEl.innerHTML = `
        <div class="toast-header" style="background-color: var(--card-bg); color: var(--text-color); border-bottom: 1px solid var(--border-color);">
            <i class="fas ${icon} me-2"></i>
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    toastContainer.appendChild(toastEl);
    const bsToast = new bootstrap.Toast(toastEl, { delay: 5000 });
    bsToast.show();
    
    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    });
}

// Sidebar Active Link
document.addEventListener("DOMContentLoaded", function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link');
    navLinks.forEach(link => {
        if(link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});
