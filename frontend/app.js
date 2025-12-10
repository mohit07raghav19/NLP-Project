// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// State Management
const state = {
    currentPage: 1,
    limit: 20,
    filters: {
        severities: [],
        minCvss: '',
        maxCvss: '',
        startDate: '',
        endDate: '',
        searchQuery: ''
    },
    sortBy: 'published_desc',
    totalResults: 0,
    allCVEs: [],
    statistics: null,
    charts: {}
};

// Cache Management
const cache = {
    data: new Map(),
    ttl: 5 * 60 * 1000, // 5 minutes

    set(key, value) {
        this.data.set(key, {
            value,
            timestamp: Date.now()
        });
    },

    get(key) {
        const item = this.data.get(key);
        if (!item) return null;

        if (Date.now() - item.timestamp > this.ttl) {
            this.data.delete(key);
            return null;
        }

        return item.value;
    },

    clear() {
        this.data.clear();
    }
};

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    const icons = {
        success: '✓',
        error: '✗',
        info: 'ℹ'
    };

    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${icons[type]}</span>
            <span class="toast-message">${message}</span>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Utility Functions
function showLoading() {
    document.getElementById('loadingIndicator').classList.add('active');
    document.getElementById('cveList').style.display = 'none';
    hideError();
}

function hideLoading() {
    document.getElementById('loadingIndicator').classList.remove('active');
    document.getElementById('cveList').style.display = 'flex';
}

function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    errorEl.textContent = message;
    errorEl.classList.add('active');
    hideLoading();
}

function hideError() {
    document.getElementById('errorMessage').classList.remove('active');
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function getSeverityClass(severity) {
    if (!severity) return '';
    return severity.toLowerCase();
}

// API Functions
async function fetchAPI(endpoint, useCache = true) {
    try {
        // Check cache first
        if (useCache) {
            const cached = cache.get(endpoint);
            if (cached) return cached;
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        const data = await response.json();

        // Cache the result
        cache.set(endpoint, data);

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);

    showToast(`Switched to ${newTheme} mode`, 'success');

    // Redraw charts with new theme
    if (state.statistics) {
        renderCharts(state.statistics);
    }
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('.theme-icon');
    icon.textContent = theme === 'light' ? '🌙' : '☀️';
}

// Tab Management
function switchTab(tabName) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

    // Add active class to selected tab
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');

    // Load data for analytics tab
    if (tabName === 'analytics') {
        // Load CVEs if not already loaded
        if (state.allCVEs.length === 0) {
            loadCVEs().then(() => {
                if (state.statistics) {
                    renderCharts(state.statistics);
                }
            });
        } else if (state.statistics) {
            renderCharts(state.statistics);
        }
    }
}

// Make switchTab global
window.switchTab = switchTab;

// Health Check
async function checkHealth() {
    try {
        const data = await fetchAPI('/health', false);
        const statusEl = document.getElementById('healthStatus');

        if (data.status === 'healthy') {
            statusEl.classList.add('healthy');
            statusEl.querySelector('.status-text').textContent =
                `Connected (${data.cve_count} CVEs)`;
        } else {
            statusEl.querySelector('.status-text').textContent = 'Disconnected';
        }
    } catch (error) {
        document.getElementById('healthStatus').querySelector('.status-text').textContent = 'Error';
    }
}

// Statistics
async function loadStatistics() {
    try {
        const data = await fetchAPI('/api/v1/statistics');
        state.statistics = data;

        document.getElementById('totalCves').textContent = data.total_cves.toLocaleString();
        document.getElementById('criticalCount').textContent = data.critical.toLocaleString();
        document.getElementById('highCount').textContent = data.high.toLocaleString();
        document.getElementById('mediumCount').textContent = data.medium.toLocaleString();
        document.getElementById('lowCount').textContent = data.low.toLocaleString();
        document.getElementById('avgScore').textContent = data.average_cvss_score.toFixed(1);
    } catch (error) {
        console.error('Failed to load statistics:', error);
    }
}

// Load and sort CVEs
async function loadCVEs() {
    showLoading();
    hideError();

    try {
        const offset = (state.currentPage - 1) * state.limit;
        let endpoint = `/api/v1/cves?limit=3000&offset=0`; // Get all CVEs for complete analytics

        const data = await fetchAPI(endpoint);
        state.allCVEs = data.results;

        // Apply client-side filtering and sorting
        let filtered = filterCVEs(state.allCVEs);
        filtered = sortCVEs(filtered);

        state.totalResults = filtered.length;

        // Paginate
        const start = offset;
        const end = start + state.limit;
        const paginated = filtered.slice(start, end);

        displayCVEs(paginated);
        updatePagination();
        updateActiveFilters();

    } catch (error) {
        showError('Failed to load CVEs. Please check if the API is running.');
    }
}

// Filter CVEs
function filterCVEs(cves) {
    return cves.filter(cve => {
        // Severity filter
        if (state.filters.severities.length > 0) {
            if (!state.filters.severities.includes(cve.cvss_severity)) return false;
        }

        // CVSS range
        if (state.filters.minCvss && cve.cvss_score < parseFloat(state.filters.minCvss)) return false;
        if (state.filters.maxCvss && cve.cvss_score > parseFloat(state.filters.maxCvss)) return false;

        // Date range
        if (state.filters.startDate && new Date(cve.published_date) < new Date(state.filters.startDate)) return false;
        if (state.filters.endDate && new Date(cve.published_date) > new Date(state.filters.endDate)) return false;

        return true;
    });
}

// Sort CVEs
function sortCVEs(cves) {
    const sorted = [...cves];

    switch (state.sortBy) {
        case 'published_desc':
            return sorted.sort((a, b) => new Date(b.published_date) - new Date(a.published_date));
        case 'published_asc':
            return sorted.sort((a, b) => new Date(a.published_date) - new Date(b.published_date));
        case 'cvss_desc':
            return sorted.sort((a, b) => (b.cvss_score || 0) - (a.cvss_score || 0));
        case 'cvss_asc':
            return sorted.sort((a, b) => (a.cvss_score || 0) - (b.cvss_score || 0));
        case 'cve_id_asc':
            return sorted.sort((a, b) => a.cve_id.localeCompare(b.cve_id));
        case 'cve_id_desc':
            return sorted.sort((a, b) => b.cve_id.localeCompare(a.cve_id));
        default:
            return sorted;
    }
}

// Search CVEs with debounce
const searchCVEs = debounce(async function() {
    const query = document.getElementById('searchInput').value.trim();

    if (query.length < 3) {
        if (query.length > 0) {
            showError('Please enter at least 3 characters to search');
        } else {
            loadCVEs(); // Load all if search is cleared
        }
        return;
    }

    showLoading();
    hideError();

    try {
        const endpoint = `/api/v1/search?q=${encodeURIComponent(query)}&limit=500`;
        const data = await fetchAPI(endpoint, false);

        state.allCVEs = data.results;
        state.filters.searchQuery = query;

        // Apply filters and sorting
        let filtered = filterCVEs(state.allCVEs);
        filtered = sortCVEs(filtered);

        state.totalResults = filtered.length;
        state.currentPage = 1;

        const paginated = filtered.slice(0, state.limit);
        displayCVEs(paginated, query);
        updatePagination();

        showToast(`Found ${data.total} CVEs`, 'success');

    } catch (error) {
        showError('Search failed. Please try again.');
    }
}, 500);

// Display CVEs
function displayCVEs(cves, highlightTerm = '') {
    hideLoading();

    if (cves.length === 0) {
        document.getElementById('cveList').innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: var(--color-text-secondary);">
                <p style="font-size: 18px; margin-bottom: 10px;">No CVEs found</p>
                <p style="font-size: 14px;">Try adjusting your filters or search query</p>
            </div>
        `;
        document.getElementById('resultsCount').textContent = '0 results';
        return;
    }

    document.getElementById('resultsCount').textContent = `${state.totalResults.toLocaleString()} results`;

    document.getElementById('cveList').innerHTML = cves.map((cve, index) => {
        let description = cve.description || 'No description available';

        // Highlight search terms
        if (highlightTerm) {
            const regex = new RegExp(`(${highlightTerm})`, 'gi');
            description = description.replace(regex, '<mark>$1</mark>');
        }

        // Generate vendor tags
        const vendorTags = cve.affected_vendors && cve.affected_vendors.length > 0
            ? cve.affected_vendors.slice(0, 3).map(v => `<span class="cve-tag">${v}</span>`).join('')
            : '';

        return `
        <div class="cve-card ${getSeverityClass(cve.cvss_severity)}" style="animation-delay: ${index * 0.05}s">
            <div class="cve-header">
                <div class="cve-id">${cve.cve_id}</div>
                <div class="cve-actions">
                    <button class="cve-action-btn" onclick="copyCVEId('${cve.cve_id}')" title="Copy CVE ID">
                        📋
                    </button>
                    ${cve.cvss_severity ? `
                        <span class="cve-badge ${getSeverityClass(cve.cvss_severity)}">
                            ${cve.cvss_severity}
                        </span>
                    ` : ''}
                </div>
            </div>
            ${vendorTags ? `<div class="cve-tags">${vendorTags}</div>` : ''}
            <div class="cve-description" onclick="showCVEDetail('${cve.cve_id}')">
                ${description}
            </div>
            <div class="cve-meta" onclick="showCVEDetail('${cve.cve_id}')">
                ${cve.cvss_score ? `
                    <div class="cve-meta-item">
                        <span>CVSS:</span>
                        <span class="cvss-score">${cve.cvss_score.toFixed(1)}</span>
                    </div>
                ` : ''}
                ${cve.published_date ? `
                    <div class="cve-meta-item">
                        <span>Published:</span>
                        <span>${formatDate(cve.published_date)}</span>
                    </div>
                ` : ''}
            </div>
        </div>
    `}).join('');
}

// Copy CVE ID
function copyCVEId(cveId) {
    navigator.clipboard.writeText(cveId).then(() => {
        showToast(`Copied ${cveId} to clipboard`, 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

window.copyCVEId = copyCVEId;

// Show CVE Detail
async function showCVEDetail(cveId) {
    try {
        const cve = await fetchAPI(`/api/v1/cves/${cveId}`);

        document.getElementById('cveDetail').innerHTML = `
            <h2>${cve.cve_id}</h2>
            ${cve.cvss_severity ? `
                <span class="cve-badge ${getSeverityClass(cve.cvss_severity)}">
                    ${cve.cvss_severity}
                </span>
            ` : ''}

            <div class="cve-detail-actions">
                <button class="btn-secondary" onclick="copyCVEId('${cve.cve_id}')">
                    📋 Copy ID
                </button>
                <button class="btn-secondary" onclick="exportSingleCVE('${cve.cve_id}')">
                    📥 Export
                </button>
            </div>

            <div class="cve-detail-section">
                <h3>Description</h3>
                <p>${cve.description || 'No description available'}</p>
            </div>

            ${cve.cvss_score ? `
                <div class="cve-detail-section">
                    <h3>CVSS Score</h3>
                    <p style="font-size: 24px; font-weight: 600; color: var(--color-text);">
                        ${cve.cvss_score.toFixed(1)} / 10.0
                    </p>
                </div>
            ` : ''}

            ${cve.published_date ? `
                <div class="cve-detail-section">
                    <h3>Published Date</h3>
                    <p>${formatDate(cve.published_date)}</p>
                </div>
            ` : ''}

            ${cve.affected_vendors && cve.affected_vendors.length > 0 ? `
                <div class="cve-detail-section">
                    <h3>Affected Vendors</h3>
                    <ul class="cve-detail-list">
                        ${cve.affected_vendors.map(vendor => `<li>${vendor}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}

            ${cve.affected_products && cve.affected_products.length > 0 ? `
                <div class="cve-detail-section">
                    <h3>Affected Products</h3>
                    <ul class="cve-detail-list">
                        ${cve.affected_products.map(product => `<li>${product}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        `;

        document.getElementById('cveModal').classList.add('active');
    } catch (error) {
        showError('Failed to load CVE details');
    }
}

window.showCVEDetail = showCVEDetail;

// Export Functions
function exportToCSV(data) {
    const headers = ['CVE ID', 'Severity', 'CVSS Score', 'Published Date', 'Description', 'Affected Vendors', 'Affected Products'];
    const rows = data.map(cve => [
        cve.cve_id,
        cve.cvss_severity || '',
        cve.cvss_score || '',
        cve.published_date || '',
        `"${(cve.description || '').replace(/"/g, '""')}"`,
        `"${(cve.affected_vendors || []).join(', ')}"`,
        `"${(cve.affected_products || []).join(', ')}"`,
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    downloadFile(csv, 'cve_export.csv', 'text/csv');
    showToast('CSV exported successfully', 'success');
}

function exportToJSON(data) {
    const json = JSON.stringify(data, null, 2);
    downloadFile(json, 'cve_export.json', 'application/json');
    showToast('JSON exported successfully', 'success');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
}

function exportSingleCVE(cveId) {
    const cve = state.allCVEs.find(c => c.cve_id === cveId);
    if (cve) {
        exportToJSON([cve]);
    }
}

window.exportSingleCVE = exportSingleCVE;

// Multi-select dropdown
function initMultiSelect() {
    const btn = document.getElementById('severityBtn');
    const dropdown = document.getElementById('severityDropdown');

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('active');
    });

    document.addEventListener('click', () => {
        dropdown.classList.remove('active');
    });

    dropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    // Handle checkbox changes
    dropdown.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            state.filters.severities = Array.from(
                dropdown.querySelectorAll('input[type="checkbox"]:checked')
            ).map(cb => cb.value);

            updateMultiSelectButton();
            state.currentPage = 1;
            loadCVEs();
        });
    });
}

function updateMultiSelectButton() {
    const btn = document.getElementById('severityBtn');
    const selected = state.filters.severities;

    if (selected.length === 0) {
        btn.textContent = 'All Severities ▾';
    } else {
        btn.textContent = `${selected.length} selected ▾`;
    }
}

// Active Filters Display
function updateActiveFilters() {
    const container = document.getElementById('activeFilters');
    const filters = [];

    if (state.filters.severities.length > 0) {
        state.filters.severities.forEach(sev => {
            filters.push({ type: 'severity', value: sev, label: `Severity: ${sev}` });
        });
    }

    if (state.filters.minCvss) {
        filters.push({ type: 'minCvss', value: state.filters.minCvss, label: `Min CVSS: ${state.filters.minCvss}` });
    }

    if (state.filters.maxCvss) {
        filters.push({ type: 'maxCvss', value: state.filters.maxCvss, label: `Max CVSS: ${state.filters.maxCvss}` });
    }

    if (state.filters.startDate) {
        filters.push({ type: 'startDate', value: state.filters.startDate, label: `From: ${formatDate(state.filters.startDate)}` });
    }

    if (state.filters.endDate) {
        filters.push({ type: 'endDate', value: state.filters.endDate, label: `To: ${formatDate(state.filters.endDate)}` });
    }

    if (state.filters.searchQuery) {
        filters.push({ type: 'search', value: state.filters.searchQuery, label: `Search: "${state.filters.searchQuery}"` });
    }

    container.innerHTML = filters.map(f => `
        <div class="filter-tag">
            ${f.label}
            <span class="filter-tag-close" onclick="removeFilter('${f.type}', '${f.value}')">×</span>
        </div>
    `).join('');
}

function removeFilter(type, value) {
    switch (type) {
        case 'severity':
            state.filters.severities = state.filters.severities.filter(s => s !== value);
            // Uncheck the checkbox
            document.querySelector(`#severityDropdown input[value="${value}"]`).checked = false;
            updateMultiSelectButton();
            break;
        case 'minCvss':
            state.filters.minCvss = '';
            document.getElementById('minCvssInput').value = '';
            break;
        case 'maxCvss':
            state.filters.maxCvss = '';
            document.getElementById('maxCvssInput').value = '';
            break;
        case 'startDate':
            state.filters.startDate = '';
            document.getElementById('startDate').value = '';
            break;
        case 'endDate':
            state.filters.endDate = '';
            document.getElementById('endDate').value = '';
            break;
        case 'search':
            state.filters.searchQuery = '';
            document.getElementById('searchInput').value = '';
            break;
    }

    state.currentPage = 1;
    loadCVEs();
}

window.removeFilter = removeFilter;

// Pagination
function updatePagination() {
    const totalPages = Math.ceil(state.totalResults / state.limit);

    document.getElementById('pageInfo').textContent = `Page ${state.currentPage} of ${totalPages}`;
    document.getElementById('prevBtn').disabled = state.currentPage === 1;
    document.getElementById('nextBtn').disabled = state.currentPage >= totalPages;
}

function clearFilters() {
    state.filters = {
        severities: [],
        minCvss: '',
        maxCvss: '',
        startDate: '',
        endDate: '',
        searchQuery: ''
    };
    state.currentPage = 1;

    document.getElementById('searchInput').value = '';
    document.querySelectorAll('#severityDropdown input[type="checkbox"]').forEach(cb => cb.checked = false);
    updateMultiSelectButton();
    document.getElementById('minCvssInput').value = '';
    document.getElementById('maxCvssInput').value = '';
    document.getElementById('startDate').value = '';
    document.getElementById('endDate').value = '';

    loadCVEs();
    showToast('Filters cleared', 'info');
}

// Charts
function renderCharts(stats) {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const textColor = isDark ? '#c9d1d9' : '#24292e';
    const gridColor = isDark ? '#30363d' : '#e1e4e8';

    // Destroy existing charts
    Object.values(state.charts).forEach(chart => {
        if (chart) chart.destroy();
    });

    // Calculate analytics data
    const criticalRisk = state.allCVEs.filter(c => c.cvss_score >= 9.0).length;
    const highRisk = state.allCVEs.filter(c => c.cvss_score >= 7.0 && c.cvss_score < 9.0).length;
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
    const recentCVEs = state.allCVEs.filter(c => new Date(c.published_date) > thirtyDaysAgo).length;

    // Update summary stats
    document.getElementById('criticalRiskCount').textContent = criticalRisk.toLocaleString();
    document.getElementById('highRiskCount').textContent = highRisk.toLocaleString();
    document.getElementById('recentCount').textContent = recentCVEs.toLocaleString();

    // Vendor/Product counts
    const vendorCounts = {};
    const productCounts = {};

    state.allCVEs.forEach(cve => {
        if (cve.affected_vendors) {
            cve.affected_vendors.forEach(vendor => {
                vendorCounts[vendor] = (vendorCounts[vendor] || 0) + 1;
            });
        }
        if (cve.affected_products) {
            cve.affected_products.forEach(product => {
                productCounts[product] = (productCounts[product] || 0) + 1;
            });
        }
    });

    const topVendors = Object.entries(vendorCounts).sort((a, b) => b[1] - a[1]);
    const topProducts = Object.entries(productCounts).sort((a, b) => b[1] - a[1]);

    if (topVendors.length > 0) {
        document.getElementById('topVendor').textContent = topVendors[0][0];
    }

    // 1. Severity Distribution Pie Chart
    const severityCtx = document.getElementById('severityChart');
    if (severityCtx) {
        state.charts.severity = new Chart(severityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    data: [stats.critical, stats.high, stats.medium, stats.low],
                    backgroundColor: [
                        isDark ? '#f85149' : '#d73a49',
                        isDark ? '#fb8500' : '#e36209',
                        isDark ? '#ffcf40' : '#ffd33d',
                        isDark ? '#3fb950' : '#28a745'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor }
                    }
                }
            }
        });
    }

    // 2. CVSS Score Distribution
    const cvssRanges = {
        '0-2': 0, '2-4': 0, '4-6': 0, '6-8': 0, '8-10': 0
    };

    state.allCVEs.forEach(cve => {
        if (cve.cvss_score) {
            const score = cve.cvss_score;
            if (score < 2) cvssRanges['0-2']++;
            else if (score < 4) cvssRanges['2-4']++;
            else if (score < 6) cvssRanges['4-6']++;
            else if (score < 8) cvssRanges['6-8']++;
            else cvssRanges['8-10']++;
        }
    });

    const cvssCtx = document.getElementById('cvssChart');
    if (cvssCtx) {
        state.charts.cvss = new Chart(cvssCtx, {
            type: 'bar',
            data: {
                labels: Object.keys(cvssRanges),
                datasets: [{
                    label: 'Number of CVEs',
                    data: Object.values(cvssRanges),
                    backgroundColor: isDark ? '#58a6ff' : '#0366d6'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 3. CVEs Over Time (Timeline) - Full November 2025 (Nov 1-30)
    const dailyData = {};

    // Create all days in November 2025
    for (let day = 1; day <= 30; day++) {
        const key = `Nov ${day}`;
        dailyData[key] = 0;
    }

    // Count CVEs per day
    state.allCVEs.forEach(cve => {
        if (cve.published_date) {
            const date = new Date(cve.published_date);
            // Only count if it's November 2025
            if (date.getFullYear() === 2025 && date.getMonth() === 10) { // Month is 0-indexed, 10 = November
                const day = date.getDate();
                const key = `Nov ${day}`;
                if (dailyData.hasOwnProperty(key)) {
                    dailyData[key]++;
                }
            }
        }
    });

    const timelineCtx = document.getElementById('timelineChart');
    if (timelineCtx) {
        state.charts.timeline = new Chart(timelineCtx, {
            type: 'line',
            data: {
                labels: Object.keys(dailyData),
                datasets: [{
                    label: 'CVEs Published',
                    data: Object.values(dailyData),
                    borderColor: isDark ? '#58a6ff' : '#0366d6',
                    backgroundColor: isDark ? 'rgba(88, 166, 255, 0.1)' : 'rgba(3, 102, 214, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 4. Top 10 Vendors
    const vendorCtx = document.getElementById('vendorChart');
    if (vendorCtx && topVendors.length > 0) {
        state.charts.vendor = new Chart(vendorCtx, {
            type: 'bar',
            data: {
                labels: topVendors.slice(0, 10).map(v => v[0]),
                datasets: [{
                    label: 'Number of CVEs',
                    data: topVendors.slice(0, 10).map(v => v[1]),
                    backgroundColor: isDark ? '#58a6ff' : '#0366d6'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 5. Top 10 Products
    const productCtx = document.getElementById('productChart');
    if (productCtx && topProducts.length > 0) {
        state.charts.product = new Chart(productCtx, {
            type: 'bar',
            data: {
                labels: topProducts.slice(0, 10).map(p => p[0]),
                datasets: [{
                    label: 'Number of CVEs',
                    data: topProducts.slice(0, 10).map(p => p[1]),
                    backgroundColor: isDark ? '#fb8500' : '#e36209'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 6. Severity Trend (Monthly)
    const severityTrend = {
        'Nov 2025': { critical: 0, high: 0, medium: 0, low: 0 }
    };

    state.allCVEs.forEach(cve => {
        if (cve.published_date && cve.cvss_severity) {
            const date = new Date(cve.published_date);
            // Only count November 2025 data
            if (date.getFullYear() === 2025 && date.getMonth() === 10) {
                const key = 'Nov 2025';
                const severity = cve.cvss_severity.toLowerCase();
                if (severityTrend[key][severity] !== undefined) {
                    severityTrend[key][severity]++;
                }
            }
        }
    });

    const severityTrendCtx = document.getElementById('severityTrendChart');
    if (severityTrendCtx) {
        state.charts.severityTrend = new Chart(severityTrendCtx, {
            type: 'line',
            data: {
                labels: Object.keys(severityTrend),
                datasets: [
                    {
                        label: 'Critical',
                        data: Object.values(severityTrend).map(v => v.critical),
                        borderColor: isDark ? '#f85149' : '#d73a49',
                        tension: 0.4
                    },
                    {
                        label: 'High',
                        data: Object.values(severityTrend).map(v => v.high),
                        borderColor: isDark ? '#fb8500' : '#e36209',
                        tension: 0.4
                    },
                    {
                        label: 'Medium',
                        data: Object.values(severityTrend).map(v => v.medium),
                        borderColor: isDark ? '#ffcf40' : '#ffd33d',
                        tension: 0.4
                    },
                    {
                        label: 'Low',
                        data: Object.values(severityTrend).map(v => v.low),
                        borderColor: isDark ? '#3fb950' : '#28a745',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        stacked: false,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 7. Average CVSS by Severity
    const avgCvssBySeverity = {
        'CRITICAL': [],
        'HIGH': [],
        'MEDIUM': [],
        'LOW': []
    };

    state.allCVEs.forEach(cve => {
        if (cve.cvss_score && cve.cvss_severity && avgCvssBySeverity[cve.cvss_severity]) {
            avgCvssBySeverity[cve.cvss_severity].push(cve.cvss_score);
        }
    });

    const avgScores = Object.keys(avgCvssBySeverity).map(severity => {
        const scores = avgCvssBySeverity[severity];
        return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    });

    const avgCvssCtx = document.getElementById('avgCvssChart');
    if (avgCvssCtx) {
        state.charts.avgCvss = new Chart(avgCvssCtx, {
            type: 'bar',
            data: {
                labels: ['Critical', 'High', 'Medium', 'Low'],
                datasets: [{
                    label: 'Average CVSS Score',
                    data: avgScores,
                    backgroundColor: [
                        isDark ? '#f85149' : '#d73a49',
                        isDark ? '#fb8500' : '#e36209',
                        isDark ? '#ffcf40' : '#ffd33d',
                        isDark ? '#3fb950' : '#28a745'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    x: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 8. Top 10 Vulnerability Types
    const vulnTypeCounts = {};
    state.allCVEs.forEach(cve => {
        if (cve.vulnerability_types && Array.isArray(cve.vulnerability_types)) {
            cve.vulnerability_types.forEach(type => {
                vulnTypeCounts[type] = (vulnTypeCounts[type] || 0) + 1;
            });
        }
    });

    const topVulnTypes = Object.entries(vulnTypeCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const vulnTypesCtx = document.getElementById('vulnTypesChart');
    if (vulnTypesCtx && topVulnTypes.length > 0) {
        state.charts.vulnTypes = new Chart(vulnTypesCtx, {
            type: 'bar',
            data: {
                labels: topVulnTypes.map(v => v[0]),
                datasets: [{
                    label: 'Number of CVEs',
                    data: topVulnTypes.map(v => v[1]),
                    backgroundColor: isDark ? '#d73a49' : '#f85149'
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: textColor } }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    },
                    y: {
                        ticks: { color: textColor },
                        grid: { color: gridColor }
                    }
                }
            }
        });
    }

    // 9. Attack Vector Distribution
    const attackVectorCounts = {};
    state.allCVEs.forEach(cve => {
        if (cve.attack_vector) {
            attackVectorCounts[cve.attack_vector] = (attackVectorCounts[cve.attack_vector] || 0) + 1;
        }
    });

    const attackVectorCtx = document.getElementById('attackVectorChart');
    if (attackVectorCtx && Object.keys(attackVectorCounts).length > 0) {
        state.charts.attackVector = new Chart(attackVectorCtx, {
            type: 'pie',
            data: {
                labels: Object.keys(attackVectorCounts),
                datasets: [{
                    data: Object.values(attackVectorCounts),
                    backgroundColor: [
                        isDark ? '#f85149' : '#d73a49',
                        isDark ? '#fb8500' : '#e36209',
                        isDark ? '#58a6ff' : '#0366d6',
                        isDark ? '#3fb950' : '#28a745',
                        isDark ? '#ffcf40' : '#ffd33d'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor }
                    }
                }
            }
        });
    }

    // 10. Attack Complexity Distribution
    const attackComplexityCounts = {};
    state.allCVEs.forEach(cve => {
        if (cve.attack_complexity) {
            attackComplexityCounts[cve.attack_complexity] = (attackComplexityCounts[cve.attack_complexity] || 0) + 1;
        }
    });

    const attackComplexityCtx = document.getElementById('attackComplexityChart');
    if (attackComplexityCtx && Object.keys(attackComplexityCounts).length > 0) {
        state.charts.attackComplexity = new Chart(attackComplexityCtx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(attackComplexityCounts),
                datasets: [{
                    data: Object.values(attackComplexityCounts),
                    backgroundColor: [
                        isDark ? '#f85149' : '#d73a49',
                        isDark ? '#fb8500' : '#e36209',
                        isDark ? '#3fb950' : '#28a745'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor }
                    }
                }
            }
        });
    }

    // Generate Insights
    generateInsights(stats, criticalRisk, highRisk, recentCVEs, topVendors, topProducts);
}

// Generate Key Insights
function generateInsights(stats, criticalRisk, highRisk, recentCVEs, topVendors, topProducts) {
    const insights = [];

    // Critical Risk Alert
    if (criticalRisk > 0) {
        insights.push({
            type: 'critical',
            icon: '⚠️',
            title: `${criticalRisk} Critical Risk CVEs`,
            description: `There are ${criticalRisk} CVEs with CVSS scores of 9.0 or higher requiring immediate attention.`
        });
    }

    // Recent Activity
    if (recentCVEs > 0) {
        const percentage = ((recentCVEs / stats.total_cves) * 100).toFixed(1);
        insights.push({
            type: 'warning',
            icon: '📈',
            title: `${recentCVEs} Recent CVEs`,
            description: `${percentage}% of all CVEs were published in the last 30 days, indicating active threat landscape.`
        });
    }

    // Top Vendor Alert
    if (topVendors.length > 0) {
        const topVendor = topVendors[0];
        insights.push({
            type: 'info',
            icon: '🎯',
            title: `Most Targeted: ${topVendor[0]}`,
            description: `${topVendor[0]} has ${topVendor[1]} CVEs, making it the most affected vendor in the database.`
        });
    }

    // Severity Distribution Insight
    const criticalPercentage = ((stats.critical / stats.total_cves) * 100).toFixed(1);
    if (criticalPercentage > 10) {
        insights.push({
            type: 'critical',
            icon: '📊',
            title: 'High Critical CVE Ratio',
            description: `${criticalPercentage}% of all CVEs are classified as Critical severity.`
        });
    }

    // Average CVSS Insight
    if (stats.average_cvss_score > 7.0) {
        insights.push({
            type: 'warning',
            icon: '📉',
            title: 'High Average CVSS Score',
            description: `The average CVSS score is ${stats.average_cvss_score.toFixed(1)}, indicating generally severe vulnerabilities.`
        });
    }

    // Top Product Alert
    if (topProducts.length > 0) {
        const topProduct = topProducts[0];
        insights.push({
            type: 'info',
            icon: '🔧',
            title: `Most Vulnerable Product: ${topProduct[0]}`,
            description: `${topProduct[0]} has ${topProduct[1]} CVEs, requiring priority patching attention.`
        });
    }

    // Render insights
    const container = document.getElementById('insightsContainer');
    if (container) {
        container.innerHTML = insights.map(insight => `
            <div class="insight-card ${insight.type}">
                <div class="insight-title">
                    <span>${insight.icon}</span>
                    <span>${insight.title}</span>
                </div>
                <div class="insight-description">${insight.description}</div>
            </div>
        `).join('');
    }
}

// Auto-refresh
let autoRefreshInterval;
function startAutoRefresh() {
    autoRefreshInterval = setInterval(() => {
        cache.clear();
        checkHealth();
        loadStatistics();
        if (document.querySelector('.tab-btn[data-tab="list"]').classList.contains('active')) {
            loadCVEs();
        }
        showToast('Data refreshed', 'info');
    }, 60000); // Every minute
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', () => {
        cache.clear();
        checkHealth();
        loadStatistics();
        loadCVEs();
        showToast('Data refreshed', 'success');
    });

    // Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Search
    document.getElementById('searchInput').addEventListener('input', searchCVEs);
    document.getElementById('searchBtn').addEventListener('click', searchCVEs);

    // Filters
    document.getElementById('minCvssInput').addEventListener('change', (e) => {
        state.filters.minCvss = e.target.value;
        state.currentPage = 1;
        loadCVEs();
    });

    document.getElementById('maxCvssInput').addEventListener('change', (e) => {
        state.filters.maxCvss = e.target.value;
        state.currentPage = 1;
        loadCVEs();
    });

    document.getElementById('startDate').addEventListener('change', (e) => {
        state.filters.startDate = e.target.value;
        state.currentPage = 1;
        loadCVEs();
    });

    document.getElementById('endDate').addEventListener('change', (e) => {
        state.filters.endDate = e.target.value;
        state.currentPage = 1;
        loadCVEs();
    });

    document.getElementById('sortBy').addEventListener('change', (e) => {
        state.sortBy = e.target.value;
        loadCVEs();
    });

    document.getElementById('perPage').addEventListener('change', (e) => {
        state.limit = parseInt(e.target.value);
        state.currentPage = 1;
        loadCVEs();
    });

    document.getElementById('clearFiltersBtn').addEventListener('click', clearFilters);

    // Export buttons
    document.getElementById('exportFilteredBtn').addEventListener('click', () => {
        const filtered = filterCVEs(state.allCVEs);
        exportToCSV(filtered);
    });

    document.getElementById('exportAllBtn').addEventListener('click', () => {
        exportToCSV(state.allCVEs);
    });

    // Pagination
    document.getElementById('prevBtn').addEventListener('click', () => {
        if (state.currentPage > 1) {
            state.currentPage--;
            loadCVEs();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    document.getElementById('nextBtn').addEventListener('click', () => {
        const totalPages = Math.ceil(state.totalResults / state.limit);
        if (state.currentPage < totalPages) {
            state.currentPage++;
            loadCVEs();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }
    });

    // Modal
    document.getElementById('modalClose').addEventListener('click', () => {
        document.getElementById('cveModal').classList.remove('active');
    });

    document.getElementById('cveModal').addEventListener('click', (e) => {
        if (e.target.id === 'cveModal') {
            document.getElementById('cveModal').classList.remove('active');
        }
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && document.getElementById('cveModal').classList.contains('active')) {
            document.getElementById('cveModal').classList.remove('active');
        }
    });

    // Initialize
    initTheme();
    initMultiSelect();
    checkHealth();
    loadStatistics();
    loadCVEs();
    startAutoRefresh();
});
