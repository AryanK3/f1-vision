// Main JavaScript for F1 Dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Initialize
    initDashboard();

    // Update every 1 second
    setInterval(updateDashboard, 1000);
});

// Global storage for data
let dashboardData = {
    track: null,
    timing: null,
    events: []
};

// Race timer
let raceStartTime = new Date();
let raceTimer = document.getElementById('race-time');

// Initialize the dashboard
function initDashboard() {
    // Initialize SVG for track map
    const trackMap = d3.select('#track-map')
        .append('svg')
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('viewBox', '0 0 1000 800')
        .attr('preserveAspectRatio', 'xMidYMid meet');

    // Add group for track path
    trackMap.append('g')
        .attr('class', 'track-group');

    // Add group for driver markers
    trackMap.append('g')
        .attr('class', 'drivers-group');

    // Initial data load
    fetchAllData();

    // Start the race timer
    updateRaceTimer();
    setInterval(updateRaceTimer, 100);
}

// Update race timer
function updateRaceTimer() {
    const now = new Date();
    const elapsed = now - raceStartTime;

    // Format as 00:00:00.000
    let hours = Math.floor(elapsed / 3600000).toString().padStart(2, '0');
    let minutes = Math.floor((elapsed % 3600000) / 60000).toString().padStart(2, '0');
    let seconds = Math.floor((elapsed % 60000) / 1000).toString().padStart(2, '0');
    let milliseconds = Math.floor(elapsed % 1000).toString().padStart(3, '0');

    raceTimer.textContent = `${hours}:${minutes}:${seconds}.${milliseconds}`;
}

// Fetch all dashboard data
function fetchAllData() {
    fetch('/api/data')
        .then(response => response.json())
        .then(data => {
            dashboardData = data;
            renderDashboard();
        })
        .catch(error => console.error('Error fetching data:', error));
}

// Update dashboard with latest data
function updateDashboard() {
    // Update position data
    fetch('/api/position')
        .then(response => response.json())
        .then(data => {
            dashboardData.track = data;
            updateTrackMap();
        })
        .catch(error => console.error('Error fetching position data:', error));

    // Update timing data
    fetch('/api/timing')
        .then(response => response.json())
        .then(data => {
            dashboardData.timing = data;
            updateTimingBoard();
        })
        .catch(error => console.error('Error fetching timing data:', error));
}

// Render the entire dashboard
function renderDashboard() {
    renderTrackMap();
    renderTimingBoard();
    renderEventFeed();
}

// Render track map
function renderTrackMap() {
    if (!dashboardData.track) return;

    const trackData = dashboardData.track;
    const svgContainer = d3.select('#track-map svg');
    const width = 1000;
    const height = 800;
    const padding = 50;

    // Scale functions to map data coordinates to SVG coordinates
    const xScale = d3.scaleLinear()
        .domain([trackData.min_x, trackData.max_x])
        .range([padding, width - padding]);

    const yScale = d3.scaleLinear()
        .domain([trackData.min_y, trackData.max_y])
        .range([padding, height - padding]);

    // Add driver markers
    const driversGroup = svgContainer.select('.drivers-group');

    // Clear existing markers
    driversGroup.selectAll('*').remove();

    // Add driver markers
    Object.keys(trackData.drivers).forEach(driverId => {
        const driver = trackData.drivers[driverId];
        const driverGroup = driversGroup.append('g')
            .attr('class', 'driver-marker')
            .attr('id', `driver-${driverId}`)
            .attr('transform', `translate(${xScale(driver.x)}, ${yScale(driver.y)})`);

        // Add circle for driver
        driverGroup.append('circle')
            .attr('r', 10)
            .attr('fill', driver.info.color || '#FFFFFF');

        // Add driver code label
        driverGroup.append('text')
            .attr('class', 'driver-code-label')
            .attr('fill', getContrastColor(driver.info.color || '#FFFFFF'))
            .text(driver.info.code);

        // Add tooltip on hover
        driverGroup.append('title')
            .text(driver.info.name);
    });
}

// Update the track map with new positions
function updateTrackMap() {
    if (!dashboardData.track) return;

    const trackData = dashboardData.track;
    const svgContainer = d3.select('#track-map svg');
    const width = 1000;
    const height = 800;
    const padding = 50;

    // Scale functions to map data coordinates to SVG coordinates
    const xScale = d3.scaleLinear()
        .domain([trackData.min_x, trackData.max_x])
        .range([padding, width - padding]);

    const yScale = d3.scaleLinear()
        .domain([trackData.min_y, trackData.max_y])
        .range([padding, height - padding]);

    // Update driver positions
    Object.keys(trackData.drivers).forEach(driverId => {
        const driver = trackData.drivers[driverId];
        const driverGroup = d3.select(`#driver-${driverId}`);

        if (!driverGroup.empty()) {
            driverGroup.transition()
                .duration(500)
                .attr('transform', `translate(${xScale(driver.x)}, ${yScale(driver.y)})`);
        }
    });
}

// Render timing board
function renderTimingBoard() {
    if (!dashboardData.timing) return;

    const driverRows = document.getElementById('driver-rows');
    driverRows.innerHTML = '';

    // Sort drivers by position
    const sortedDrivers = Object.entries(dashboardData.timing)
        .sort((a, b) => a[1].position - b[1].position);

    // Create rows for each driver
    sortedDrivers.forEach(([driverId, data]) => {
        const row = document.createElement('div');
        row.className = 'timing-row';
        row.id = `driver-row-${driverId}`;

        // Position
        const position = document.createElement('div');
        position.className = 'position';
        position.textContent = data.position;

        // Driver
        const driver = document.createElement('div');
        driver.className = 'driver';

        const driverCode = document.createElement('div');
        driverCode.className = 'driver-code';
        driverCode.textContent = data.info.code;
        driverCode.style.backgroundColor = data.info.color || '#777777';
        driverCode.style.color = getContrastColor(data.info.color || '#777777');

        driver.appendChild(driverCode);

        // DRS status
        const drs = document.createElement('div');
        drs.className = 'drs-status';
        if (data.drs === 'DRS') {
            drs.classList.add('drs-on');
            drs.textContent = 'DRS';
        } else {
            drs.classList.add('drs-off');
            drs.textContent = 'OFF';
        }

        // Tire type
        const tire = document.createElement('div');
        tire.className = 'tire-type';

        const tireIndicator = document.createElement('div');
        tireIndicator.className = 'tire-indicator';

        // Determine tire type
        let tireClass = 'medium'; // Default
        if (data.tire === 'S') tireClass = 'soft';
        if (data.tire === 'H') tireClass = 'hard';
        if (data.tire === 'I') tireClass = 'intermediate';
        if (data.tire === 'W') tireClass = 'wet';

        tireIndicator.classList.add(tireClass);
        tireIndicator.textContent = data.tire;

        tire.appendChild(tireIndicator);

        // Gap
        const gap = document.createElement('div');
        gap.className = 'gap';
        gap.textContent = data.gap;

        // Lap time
        const lapTime = document.createElement('div');
        lapTime.className = 'lap-time';
        lapTime.textContent = formatTime(data.lap_time);

        // Sectors
        const sectors = document.createElement('div');
        sectors.className = 'sectors';

        const sector1 = document.createElement('div');
        sector1.className = 'sector';
        sector1.textContent = formatTime(data.sector1);

        const sector2 = document.createElement('div');
        sector2.className = 'sector';
        sector2.textContent = formatTime(data.sector2);

        const sector3 = document.createElement('div');
        sector3.className = 'sector';
        sector3.textContent = formatTime(data.sector3);

        sectors.appendChild(sector1);
        sectors.appendChild(sector2);
        sectors.appendChild(sector3);

        // Add all elements to the row
        row.appendChild(position);
        row.appendChild(driver);
        row.appendChild(drs);
        row.appendChild(tire);
        row.appendChild(gap);
        row.appendChild(lapTime);
        row.appendChild(sectors);

        // Add the row to the timing board
        driverRows.appendChild(row);
    });
}

// Update timing board
function updateTimingBoard() {
    if (!dashboardData.timing) return;

    // Sort drivers by position
    const sortedDrivers = Object.entries(dashboardData.timing)
        .sort((a, b) => a[1].position - b[1].position);

    // Update data for each driver
    sortedDrivers.forEach(([driverId, data]) => {
        const row = document.getElementById(`driver-row-${driverId}`);

        if (row) {
            // Update position
            row.querySelector('.position').textContent = data.position;

            // Update DRS status
            const drs = row.querySelector('.drs-status');
            drs.textContent = data.drs === 'DRS' ? 'DRS' : 'OFF';
            drs.className = data.drs === 'DRS' ? 'drs-status drs-on' : 'drs-status drs-off';

            // Update gap
            row.querySelector('.gap').textContent = data.gap;

            // Update lap time
            row.querySelector('.lap-time').textContent = formatTime(data.lap_time);

            // Update sectors
            const sectors = row.querySelectorAll('.sector');
            sectors[0].textContent = formatTime(data.sector1);
            sectors[1].textContent = formatTime(data.sector2);
            sectors[2].textContent = formatTime(data.sector3);
        }
    });
}

// Render event feed
function renderEventFeed() {
    if (!dashboardData.events || dashboardData.events.length === 0) return;

    const eventList = document.getElementById('event-list');
    eventList.innerHTML = '';

    // Add the most recent events (limited to 10)
    dashboardData.events.slice(0, 10).forEach(event => {
        const li = document.createElement('li');

        const timeSpan = document.createElement('span');
        timeSpan.className = 'event-time';
        timeSpan.textContent = formatEventTime(event.time);

        const messageSpan = document.createElement('span');
        messageSpan.className = 'event-message';
        messageSpan.textContent = event.message;

        // Add class for event type
        li.classList.add(`event-${event.type.toLowerCase()}`);

        li.appendChild(timeSpan);
        li.appendChild(messageSpan);

        eventList.appendChild(li);
    });
}

// Helper function to format time in MM:SS.mmm
function formatTime(timeInSeconds) {
    if (!timeInSeconds || timeInSeconds <= 0) {
        return '00:00.000';
    }

    const minutes = Math.floor(timeInSeconds / 60).toString().padStart(2, '0');
    const seconds = Math.floor(timeInSeconds % 60).toString().padStart(2, '0');
    const milliseconds = Math.floor((timeInSeconds % 1) * 1000).toString().padStart(3, '0');

    return `${minutes}:${seconds}.${milliseconds}`;
}

// Helper function to format event time in HH:MM:SS
function formatEventTime(timeInSeconds) {
    if (!timeInSeconds || timeInSeconds < 0) {
        return '00:00:00';
    }

    const hours = Math.floor(timeInSeconds / 3600).toString().padStart(2, '0');
    const minutes = Math.floor((timeInSeconds % 3600) / 60).toString().padStart(2, '0');
    const seconds = Math.floor(timeInSeconds % 60).toString().padStart(2, '0');

    return `${hours}:${minutes}:${seconds}`;
}

// Helper function to determine text color based on background
function getContrastColor(hexColor) {
    // If no color or invalid format, return white
    if (!hexColor || !hexColor.match(/^#[0-9A-F]{6}$/i)) {
        return '#FFFFFF';
    }

    // Convert hex to RGB
    const r = parseInt(hexColor.slice(1, 3), 16);
    const g = parseInt(hexColor.slice(3, 5), 16);
    const b = parseInt(hexColor.slice(5, 7), 16);

    // Calculate luminance
    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;

    // Return black for light colors, white for dark
    return luminance > 0.5 ? '#000000' : '#FFFFFF';
}