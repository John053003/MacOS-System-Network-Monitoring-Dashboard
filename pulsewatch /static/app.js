let utilChart;
let speedChart;

function formatMetric(value, suffix = '') {
  if (value === null || value === undefined) return '--';
  return `${value}${suffix}`;
}

function renderCurrent(current) {
  document.getElementById('cpu_percent').textContent = formatMetric(current.cpu_percent, '%');
  document.getElementById('memory_percent').textContent = formatMetric(current.memory_percent, '%');
  document.getElementById('disk_percent').textContent = formatMetric(current.disk_percent, '%');
  document.getElementById('health_score').textContent = formatMetric(current.health_score, '/100');
  document.getElementById('download_mbps').textContent = formatMetric(current.download_mbps, ' Mbps');
  document.getElementById('upload_mbps').textContent = formatMetric(current.upload_mbps, ' Mbps');
  document.getElementById('latency_ms').textContent = formatMetric(current.latency_ms, ' ms');
  document.getElementById('packet_loss_percent').textContent = formatMetric(current.packet_loss_percent, '%');
  document.getElementById('last-updated').textContent = `Last updated: ${current.created_at}`;

  const processes = current.top_processes || [];
  const rows = processes.map(p => `
    <tr>
      <td>${p.name}</td>
      <td>${p.cpu_percent}%</td>
      <td>${p.memory_percent}%</td>
    </tr>
  `).join('');

  document.getElementById('process-table').innerHTML = `
    <table class="table">
      <thead><tr><th>Process</th><th>CPU</th><th>Memory</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderAlerts(alerts) {
  if (!alerts.length) {
    document.getElementById('alerts').innerHTML = '<p class="small">No alerts recorded.</p>';
    return;
  }

  document.getElementById('alerts').innerHTML = alerts.map(alert => `
    <div class="alert ${alert.severity}">
      <strong>${alert.metric_name}</strong>
      <p>${alert.message}</p>
      <div class="small">${alert.created_at}</div>
    </div>
  `).join('');
}

function renderCharts(history) {
  const labels = history.map(item => item.created_at.split('T')[1]);
  const cpu = history.map(item => item.cpu_percent);
  const memory = history.map(item => item.memory_percent);
  const disk = history.map(item => item.disk_percent);
  const download = history.map(item => item.download_mbps);
  const upload = history.map(item => item.upload_mbps);

  if (utilChart) utilChart.destroy();
  if (speedChart) speedChart.destroy();

  utilChart = new Chart(document.getElementById('utilChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'CPU %', data: cpu },
        { label: 'Memory %', data: memory },
        { label: 'Disk %', data: disk }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#ebf2ff' } } },
      scales: {
        x: { ticks: { color: '#94a6c7' }, grid: { color: '#24364f' } },
        y: { ticks: { color: '#94a6c7' }, grid: { color: '#24364f' } }
      }
    }
  });

  speedChart = new Chart(document.getElementById('speedChart'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Download Mbps', data: download },
        { label: 'Upload Mbps', data: upload }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { labels: { color: '#ebf2ff' } } },
      scales: {
        x: { ticks: { color: '#94a6c7' }, grid: { color: '#24364f' } },
        y: { ticks: { color: '#94a6c7' }, grid: { color: '#24364f' } }
      }
    }
  });
}

async function refresh() {
  const [currentRes, historyRes, alertsRes] = await Promise.all([
    fetch('/api/current'),
    fetch('/api/history'),
    fetch('/api/alerts')
  ]);

  const current = await currentRes.json();
  if (current.status === 'warming_up') {
    return;
  }

  const history = await historyRes.json();
  const alerts = await alertsRes.json();

  renderCurrent(current);
  renderCharts(history);
  renderAlerts(alerts);
}

refresh();
setInterval(refresh, 15000);