// Dashboard Application Controller

// Animated count-up helper
function animateCount(elementId, targetValue, isDecimal = false) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const duration = 500; // ms
    const startTime = performance.now();
    const startValue = parseFloat(el.textContent.replace(/,/g, '')) || 0;
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = progress * (2 - progress); // Ease-out quad
        const currentVal = startValue + (targetValue - startValue) * ease;
        
        if (isDecimal) {
            el.textContent = currentVal.toFixed(1);
        } else {
            el.textContent = Math.round(currentVal).toLocaleString();
        }
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            if (isDecimal) {
                el.textContent = targetValue.toFixed(1);
            } else {
                el.textContent = Math.round(targetValue).toLocaleString();
            }
        }
    }
    requestAnimationFrame(update);
}

// State variables
let currentCountry = 'All';
let selectedCategories = [];
let minAqi = 0;
let maxAqi = 500;
let globalMeta = {};

// Map & Network instances
let aqiMap = null;
let networkInstance = null;

// Chart.js instances to track and destroy when updating
let charts = {
    category: null,
    topCountries: null,
    histogram: null,
    pollutants: null,
    hazardous: null,
    pie: null,
    scatter: null
};

// UI Elements
const countrySelect = document.getElementById('countrySelect');
const categoryContainer = document.getElementById('categoryContainer');
const aqiMinSlider = document.getElementById('aqiMinSlider');
const aqiMaxSlider = document.getElementById('aqiMaxSlider');
const aqiRangeValue = document.getElementById('aqiRangeValue');

// Initialize App
document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    initSliders();
    initPredictor();
    await fetchMetadata();
    triggerQuery();
});

// Tab Navigation logic
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(pane => pane.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(targetTab).classList.add('active');

            // Force refresh map & network when showing their tab
            if (targetTab === 'tab-map' && aqiMap) {
                setTimeout(() => aqiMap.invalidateSize(), 200);
            }
        });
    });
}

// Slider double-handle range simulation
function initSliders() {
    const updateRangeLabel = () => {
        aqiRangeValue.textContent = `${aqiMinSlider.value} - ${aqiMaxSlider.value}`;
    };

    const handleSliderChange = () => {
        let val1 = parseInt(aqiMinSlider.value);
        let val2 = parseInt(aqiMaxSlider.value);
        
        if (val1 > val2) {
            // Swap if min is higher than max
            aqiMinSlider.value = val2;
            aqiMaxSlider.value = val1;
        }
        
        minAqi = parseInt(aqiMinSlider.value);
        maxAqi = parseInt(aqiMaxSlider.value);
        updateRangeLabel();
        triggerQuery();
    };

    aqiMinSlider.addEventListener('input', updateRangeLabel);
    aqiMaxSlider.addEventListener('input', updateRangeLabel);

    aqiMinSlider.addEventListener('change', handleSliderChange);
    aqiMaxSlider.addEventListener('change', handleSliderChange);
}

// Fetch general info
async function fetchMetadata() {
    try {
        const res = await fetch('/api/meta');
        const data = await res.json();
        globalMeta = data;

        // Set Slider Limits
        aqiMinSlider.min = data.min_aqi;
        aqiMinSlider.max = data.max_aqi;
        aqiMinSlider.value = data.min_aqi;

        aqiMaxSlider.min = data.min_aqi;
        aqiMaxSlider.max = data.max_aqi;
        aqiMaxSlider.value = data.max_aqi;

        minAqi = data.min_aqi;
        maxAqi = data.max_aqi;
        aqiRangeValue.textContent = `${data.min_aqi} - ${data.max_aqi}`;

        // Fill countries dropdown
        data.countries.forEach(country => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countrySelect.appendChild(option);
        });

        // Set up filters listener
        countrySelect.addEventListener('change', (e) => {
            currentCountry = e.target.value;
            triggerQuery();
        });

        // Fill categories checkboxes
        selectedCategories = [...data.categories];
        data.categories.forEach(cat => {
            const label = document.createElement('label');
            label.className = 'checkbox-item';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = cat;
            checkbox.checked = true;
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    selectedCategories.push(cat);
                } else {
                    selectedCategories = selectedCategories.filter(c => c !== cat);
                }
                triggerQuery();
            });

            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(cat));
            categoryContainer.appendChild(label);
        });

        // Sidebar stats
        animateCount('sideTotalRecords', data.total_records);
        animateCount('sideTotalCountries', data.total_countries);
        animateCount('sideAvgAqi', data.global_avg_aqi, true);

    } catch (err) {
        console.error("Error loading metadata:", err);
    }
}

// Run query and refresh widgets
async function triggerQuery() {
    const loader = document.getElementById('globalLoadingOverlay');
    if (loader) loader.classList.add('active');

    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                country: currentCountry,
                categories: selectedCategories,
                min_aqi: minAqi,
                max_aqi: maxAqi
            })
        });

        const data = await response.json();
        updateOverviewTab(data);
        updateAnalyticsTab(data);
        updateHazardousTab(data);
        updateDeepDiveTab(data);
        updateVisualizationsTab(data);
        updateMapTab(data);
        updateNetworkTab(data);

        if (loader) loader.classList.remove('active');
    } catch (err) {
        console.error("Error querying data:", err);
        if (loader) loader.classList.remove('active');
    }
}

// Helper to destroy a chart safely
function destroyChart(name) {
    if (charts[name]) {
        charts[name].destroy();
        charts[name] = null;
    }
}

// Overview rendering
function updateOverviewTab(data) {
    animateCount('statRecords', data.stats.total_records);
    animateCount('statAvgAqi', data.stats.avg_aqi, true);
    animateCount('statHazardous', data.stats.hazardous_count);
    animateCount('statCountries', data.stats.countries_affected);

    // Delta indicators
    const deltaRec = data.stats.total_records - globalMeta.total_records;
    const deltaRecEl = document.getElementById('deltaRecords');
    if (deltaRec === 0) {
        deltaRecEl.textContent = '';
    } else {
        deltaRecEl.textContent = `${deltaRec > 0 ? '+' : ''}${deltaRec.toLocaleString()} vs total`;
        deltaRecEl.className = 'delta ' + (deltaRec > 0 ? 'positive' : 'negative');
    }

    const deltaAqi = data.stats.avg_aqi - globalMeta.global_avg_aqi;
    const deltaAqiEl = document.getElementById('deltaAvgAqi');
    if (deltaAqi === 0) {
        deltaAqiEl.textContent = '';
    } else {
        deltaAqiEl.textContent = `${deltaAqi > 0 ? '+' : ''}${deltaAqi.toFixed(1)} vs global`;
        deltaAqiEl.className = 'delta ' + (deltaAqi > 0 ? 'positive' : 'negative');
    }

    // Category distribution chart
    destroyChart('category');
    const catLabels = Object.keys(data.category_distribution);
    const catValues = Object.values(data.category_distribution);

    charts.category = new Chart(document.getElementById('categoryChart'), {
        type: 'bar',
        data: {
            labels: catLabels,
            datasets: [{
                label: 'Cities Count',
                data: catValues,
                backgroundColor: 'rgba(14, 140, 246, 0.65)',
                borderColor: '#0e8cf6',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } },
                x: { grid: { display: false }, ticks: { color: '#a0b3c6' } }
            }
        }
    });

    // Top affected countries chart
    destroyChart('topCountries');
    const topCountryLabels = data.top_countries.map(x => x.country);
    const topCountryValues = data.top_countries.map(x => x.cities);

    charts.topCountries = new Chart(document.getElementById('topCountriesChart'), {
        type: 'bar',
        data: {
            labels: topCountryLabels,
            datasets: [{
                label: 'Cities Affected',
                data: topCountryValues,
                backgroundColor: 'rgba(255, 107, 107, 0.65)',
                borderColor: '#ff6b6b',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } },
                y: { grid: { display: false }, ticks: { color: '#a0b3c6' } }
            }
        }
    });
}

// Analytics rendering
function updateAnalyticsTab(data) {
    // Histogram
    destroyChart('histogram');
    const histLabels = data.hist_data.map(d => `${d.bin_start.toFixed(0)}-${d.bin_end.toFixed(0)}`);
    const histValues = data.hist_data.map(d => d.count);

    charts.histogram = new Chart(document.getElementById('histogramChart'), {
        type: 'bar',
        data: {
            labels: histLabels,
            datasets: [{
                label: 'Number of Cities',
                data: histValues,
                backgroundColor: 'rgba(14, 140, 246, 0.7)',
                borderColor: '#0e8cf6',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } },
                x: { grid: { display: false }, ticks: { color: '#a0b3c6', maxRotation: 45, minRotation: 45 } }
            }
        }
    });

    // Pollutants comparison
    destroyChart('pollutants');
    const polLabels = Object.keys(data.pollutants);
    const polValues = Object.values(data.pollutants);

    charts.pollutants = new Chart(document.getElementById('pollutantsChart'), {
        type: 'bar',
        data: {
            labels: polLabels,
            datasets: [{
                label: 'Average AQI Index Value',
                data: polValues,
                backgroundColor: 'rgba(255, 152, 0, 0.65)',
                borderColor: '#ff9800',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } },
                x: { grid: { display: false }, ticks: { color: '#a0b3c6' } }
            }
        }
    });
}

// Hazardous rendering
function updateHazardousTab(data) {
    const alertBox = document.getElementById('hazAlert');
    if (data.stats.hazardous_count > 0) {
        alertBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> <strong>Warning!</strong> Found ${data.stats.hazardous_count} hazardous locations with AQI exceeding 300. Urgent air quality advisory recommended.`;
        alertBox.style.display = 'block';
    } else {
        alertBox.innerHTML = `<i class="fa-solid fa-circle-check"></i> <strong>Good news!</strong> No hazardous locations (AQI > 300) found in your filtered dataset.`;
        alertBox.style.display = 'block';
    }

    // Critical cities table
    const tbody = document.querySelector('#criticalCitiesTable tbody');
    tbody.innerHTML = '';
    
    if (data.critical_cities.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" style="text-align: center;">No critical cities found.</td></tr>`;
    } else {
        data.critical_cities.forEach(city => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${city.city_name}</strong></td>
                <td>${city.country_name}</td>
                <td><span style="color: #ff6b6b; font-weight: 700;">${city.aqi_value}</span></td>
                <td><span class="badge hazardous">${city.aqi_category}</span></td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Hazardous by country chart
    destroyChart('hazardous');
    const hazCountryLabels = data.haz_by_country.map(x => x.country);
    const hazCountryValues = data.haz_by_country.map(x => x.cities);

    charts.hazardous = new Chart(document.getElementById('hazardousByCountryChart'), {
        type: 'bar',
        data: {
            labels: hazCountryLabels,
            datasets: [{
                label: 'Hazardous Cities Count',
                data: hazCountryValues,
                backgroundColor: 'rgba(139, 0, 0, 0.7)',
                borderColor: '#8b0000',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } },
                y: { grid: { display: false }, ticks: { color: '#a0b3c6' } }
            }
        }
    });
}

// Deep Dive rendering
function updateDeepDiveTab(data) {
    const placeholder = document.getElementById('deepdivePlaceholder');
    const content = document.getElementById('deepdiveContent');
    
    if (currentCountry === 'All') {
        placeholder.style.display = 'block';
        content.style.display = 'none';
        return;
    }

    placeholder.style.display = 'none';
    content.style.display = 'block';

    const detail = data.country_detail;
    document.getElementById('ddCountryTitle').textContent = currentCountry;
    animateCount('ddCities', detail.cities_count);
    animateCount('ddAvgAqi', detail.avg_aqi, true);
    animateCount('ddHazardous', detail.hazard_count);
    animateCount('ddMaxAqi', detail.max_aqi);

    const tbody = document.querySelector('#deepdiveTable tbody');
    tbody.innerHTML = '';
    
    detail.cities_list.forEach(city => {
        const catClass = city.aqi_category.toLowerCase().replace(/[^a-z]/g, '');
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${city.city_name}</strong></td>
            <td>${city.aqi_value}</td>
            <td><span class="badge ${catClass}">${city.aqi_category}</span></td>
            <td>${city.co_aqi_value}</td>
            <td>${city.ozone_aqi_value}</td>
        `;
        tbody.appendChild(tr);
    });
}

// Visualizations rendering
function updateVisualizationsTab(data) {
    // Pie Chart
    destroyChart('pie');
    const catLabels = Object.keys(data.category_distribution);
    const catValues = Object.values(data.category_distribution);
    const backgroundColors = [
        'rgba(0, 176, 80, 0.7)',
        'rgba(255, 235, 59, 0.7)',
        'rgba(255, 152, 0, 0.7)',
        'rgba(255, 87, 34, 0.7)',
        'rgba(139, 0, 0, 0.7)',
        'rgba(139, 0, 0, 0.9)'
    ];

    charts.pie = new Chart(document.getElementById('pieChart'), {
        type: 'pie',
        data: {
            labels: catLabels,
            datasets: [{
                data: catValues,
                backgroundColor: backgroundColors.slice(0, catLabels.length),
                borderWidth: 1,
                borderColor: 'rgba(10, 20, 40, 0.5)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#a0b3c6' }
                }
            }
        }
    });

    // Scatter Chart (AQI vs CO)
    destroyChart('scatter');
    const scatterPoints = data.scatter_data.map(d => ({
        x: d.co_aqi_value,
        y: d.aqi_value,
        city: d.city_name,
        category: d.aqi_category
    }));

    charts.scatter = new Chart(document.getElementById('scatterChart'), {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Cities',
                data: scatterPoints,
                backgroundColor: 'rgba(14, 140, 246, 0.6)',
                borderColor: '#0e8cf6',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const pt = ctx.raw;
                            return `${pt.city} (CO: ${pt.x}, AQI: ${pt.y}) - ${pt.category}`;
                        }
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: 'CO AQI Value', color: '#a0b3c6' }, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } },
                y: { title: { display: true, text: 'Overall AQI Value', color: '#a0b3c6' }, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0b3c6' } }
            }
        }
    });
}

// Leaflet Map Rendering
function updateMapTab(data) {
    if (!aqiMap) {
        // Initialize Map
        aqiMap = L.map('aqiMap').setView([20, 0], 2);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }).addTo(aqiMap);
    }

    // Clear existing markers
    aqiMap.eachLayer((layer) => {
        if (layer instanceof L.CircleMarker) {
            aqiMap.removeLayer(layer);
        }
    });

    // Add markers
    data.map_data.forEach(item => {
        let color = '#8b0000';
        if (item.avg_aqi <= 50) color = '#00b050';
        else if (item.avg_aqi <= 100) color = '#ffeb3b';
        else if (item.avg_aqi <= 150) color = '#ff9800';
        else if (item.avg_aqi <= 200) color = '#ff6b6b';

        const size = Math.min(25, Math.max(8, item.avg_aqi / 15));
        const popupText = `<strong>${item.country}</strong><br>Avg AQI: ${item.avg_aqi.toFixed(1)}<br>Cities Count: ${item.cities}`;
        
        L.circleMarker(item.coords, {
            radius: size,
            color: color,
            fillColor: color,
            fillOpacity: 0.65,
            weight: 1.5
        })
        .bindPopup(popupText)
        .addTo(aqiMap);
    });
}

// Network Graph rendering via Vis.js
function updateNetworkTab(data) {
    const container = document.getElementById('networkGraph');
    
    // Transform nodes and edges for Vis.js
    const visNodes = data.network.nodes.map(n => {
        const isCountry = n.group === 'country';
        return {
            id: n.id,
            label: n.label,
            color: {
                background: isCountry ? '#0e8cf6' : '#ff6b6b',
                border: '#101e38',
                highlight: {
                    background: isCountry ? '#3ca2f8' : '#ff8f8f',
                    border: '#ffffff'
                }
            },
            font: { color: '#e8eef5', size: isCountry ? 14 : 11, face: 'Inter' },
            shape: 'dot',
            size: isCountry ? 20 : 12,
            title: `${n.label}<br>Avg AQI: ${n.value.toFixed(1)}`
        };
    });

    const visEdges = data.network.edges.map(e => ({
        from: e.from,
        to: e.to,
        width: Math.max(1, e.weight / 60),
        color: { color: '#2a5a9f', opacity: 0.5, highlight: '#0e8cf6' }
    }));

    const graphData = {
        nodes: new vis.DataSet(visNodes),
        edges: new vis.DataSet(visEdges)
    };

    const options = {
        physics: {
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.3,
                springLength: 95,
                springConstant: 0.04
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200
        }
    };

    if (networkInstance) {
        networkInstance.destroy();
    }
    
    networkInstance = new vis.Network(container, graphData, options);

    // Calculate density
    const nodeCount = visNodes.length;
    const edgeCount = visEdges.length;
    const maxEdges = (nodeCount * (nodeCount - 1)) / 2;
    const density = maxEdges > 0 ? (edgeCount / maxEdges) : 0;

    document.getElementById('netNodesCount').textContent = nodeCount;
    document.getElementById('netEdgesCount').textContent = edgeCount;
    document.getElementById('netDensityVal').textContent = density.toFixed(3);
}

// Predictor Submissions
function initPredictor() {
    const form = document.getElementById('predictionForm');
    const resultCard = document.getElementById('predResultCard');
    const badge = document.getElementById('predBadge');
    const desc = document.getElementById('predDesc');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const co = document.getElementById('inputCO').value;
        const ozone = document.getElementById('inputOzone').value;
        const no2 = document.getElementById('inputNO2').value;
        const pm25 = document.getElementById('inputPM25').value;

        try {
            const res = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    co: parseFloat(co),
                    ozone: parseFloat(ozone),
                    no2: parseFloat(no2),
                    'pm2.5': parseFloat(pm25)
                })
            });

            const data = await res.json();
            if (data.error) {
                alert(data.error);
                return;
            }

            badge.textContent = data.category;
            badge.className = 'result-badge ' + data.category.toLowerCase().replace(/[^a-z]/g, '');
            desc.textContent = data.description;
            
            resultCard.style.display = 'block';

        } catch (err) {
            console.error("Error making prediction request:", err);
        }
    });
}
