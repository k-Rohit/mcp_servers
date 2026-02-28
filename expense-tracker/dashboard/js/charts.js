// js/charts.js

// shared Chart.js defaults
Chart.defaults.color = '#8888a8';
Chart.defaults.font.family = "'JetBrains Mono', monospace";
Chart.defaults.font.size = 10;

const COLORS = ['#c9f135','#8b5cf6','#ff6b6b','#00d4aa','#f59e0b','#60a5fa','#f472b6'];

const chartDefaults = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false }, tooltip: { ...tooltipStyle() } },
};

function tooltipStyle() {
  return {
    backgroundColor: '#1e1e30',
    borderColor: 'rgba(255,255,255,0.1)',
    borderWidth: 1,
    titleColor: '#e8e8f0',
    bodyColor: '#8888a8',
    padding: 10,
    cornerRadius: 8,
    titleFont: { family: "'Outfit', sans-serif", weight: '600', size: 12 },
    bodyFont:  { family: "'JetBrains Mono', monospace", size: 10 },
  };
}

const instances = {};

function destroyChart(id) {
  if (instances[id]) { instances[id].destroy(); delete instances[id]; }
}

/* ── Daily Bar Chart ── */
async function renderDailyChart() {
  const data = await API.daily(30);
  if (!data) return document.getElementById('daily-chart').closest('.loading-wrap').innerHTML = '<div class="error-state">Failed to load</div>';

  destroyChart('daily');
  const ctx = document.getElementById('daily-chart').getContext('2d');

  instances['daily'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => {
        const dt = new Date(d.date);
        return dt.getDate() + ' ' + dt.toLocaleString('default', { month: 'short' });
      }),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: data.map((d, i) => i === data.length - 1 ? '#c9f135' : 'rgba(201,241,53,0.25)'),
        borderRadius: 4,
        borderSkipped: false,
        hoverBackgroundColor: '#c9f135',
      }]
    },
    options: {
      ...chartDefaults,
      scales: {
        x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(1)+'k' : v) }
        },
      },
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          ...chartDefaults.plugins.tooltip,
          callbacks: { label: ctx => ' ₹' + Number(ctx.raw).toLocaleString('en-IN') }
        }
      }
    }
  });
}

/* ── Category Donut ── */
async function renderCategoryChart(month = '') {
  const data = await API.category(month);
  if (!data || !data.length) return;

  destroyChart('category');
  const ctx = document.getElementById('category-chart').getContext('2d');
  const total = data.reduce((s, d) => s + d.amount, 0);

  instances['category'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: COLORS,
        borderWidth: 0,
        hoverOffset: 6,
      }]
    },
    options: {
      ...chartDefaults,
      cutout: '68%',
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          ...chartDefaults.plugins.tooltip,
          callbacks: {
            label: ctx => ` ₹${Number(ctx.raw).toLocaleString('en-IN')} (${((ctx.raw/total)*100).toFixed(1)}%)`
          }
        }
      }
    }
  });

  // center label
  document.getElementById('category-total').textContent = '₹' + Number(total).toLocaleString('en-IN', { maximumFractionDigits: 0 });

  // legend
  const legend = document.getElementById('category-legend');
  legend.innerHTML = data.map((d, i) => `
    <div class="legend-row">
      <div class="legend-dot" style="background:${COLORS[i % COLORS.length]}"></div>
      <span class="legend-name">${d.category}</span>
      <span class="legend-val">₹${Number(d.amount).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
      <span class="legend-pct">${((d.amount/total)*100).toFixed(0)}%</span>
    </div>
  `).join('');
}

/* ── Monthly Trend Line ── */
async function renderMonthlyChart() {
  const data = await API.monthly(6);
  if (!data) return;

  destroyChart('monthly');
  const ctx = document.getElementById('monthly-chart').getContext('2d');

  const gradient = ctx.createLinearGradient(0, 0, 0, 180);
  gradient.addColorStop(0, 'rgba(139,92,246,0.3)');
  gradient.addColorStop(1, 'rgba(139,92,246,0)');

  instances['monthly'] = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map(d => d.month),
      datasets: [{
        data: data.map(d => d.amount),
        borderColor: '#8b5cf6',
        backgroundColor: gradient,
        borderWidth: 2.5,
        pointBackgroundColor: '#8b5cf6',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.4,
        fill: true,
      }]
    },
    options: {
      ...chartDefaults,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) }
        }
      },
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          ...chartDefaults.plugins.tooltip,
          callbacks: { label: ctx => ' ₹' + Number(ctx.raw).toLocaleString('en-IN') }
        }
      }
    }
  });
}

/* ── Payment Method Donut ── */
async function renderPaymentChart() {
  const data = await API.paymentMethod();
  if (!data || !data.length) return;

  destroyChart('payment');
  const ctx = document.getElementById('payment-chart').getContext('2d');
  const total = data.reduce((s, d) => s + d.amount, 0);

  const PAY_COLORS = { upi: '#8b5cf6', card: '#c9f135', cash: '#00d4aa', netbanking: '#60a5fa', other: '#444460' };

  instances['payment'] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.method),
      datasets: [{
        data: data.map(d => d.amount),
        backgroundColor: data.map(d => PAY_COLORS[d.method] || '#444460'),
        borderWidth: 0,
        hoverOffset: 6,
      }]
    },
    options: {
      ...chartDefaults,
      cutout: '65%',
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          ...chartDefaults.plugins.tooltip,
          callbacks: {
            label: ctx => ` ₹${Number(ctx.raw).toLocaleString('en-IN')} (${((ctx.raw/total)*100).toFixed(1)}%)`
          }
        }
      }
    }
  });

  document.getElementById('payment-legend').innerHTML = data.map(d => `
    <div class="legend-row">
      <div class="legend-dot" style="background:${PAY_COLORS[d.method] || '#444460'}"></div>
      <span class="legend-name">${d.method}</span>
      <span class="legend-val">₹${Number(d.amount).toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
      <span class="legend-pct">${((d.amount/total)*100).toFixed(0)}%</span>
    </div>
  `).join('');
}

/* ── Weekday Bar Chart ── */
async function renderWeekdayChart() {
  const data = await API.weekday();
  if (!data) return;

  destroyChart('weekday');
  const ctx = document.getElementById('weekday-chart').getContext('2d');

  instances['weekday'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.day.slice(0,3).toUpperCase()),
      datasets: [{
        data: data.map(d => d.avg_amount),
        backgroundColor: data.map(d =>
          ['Friday','Saturday'].includes(d.day) ? 'rgba(255,107,107,0.7)' : 'rgba(96,165,250,0.4)'
        ),
        borderRadius: 5,
        hoverBackgroundColor: '#60a5fa',
      }]
    },
    options: {
      ...chartDefaults,
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { callback: v => '₹' + v }
        }
      },
      plugins: {
        ...chartDefaults.plugins,
        tooltip: {
          ...chartDefaults.plugins.tooltip,
          callbacks: { label: ctx => ' Avg ₹' + Number(ctx.raw).toLocaleString('en-IN') }
        }
      }
    }
  });
}

/* ── Stacked Category Trend ── */
async function renderCategoryTrendChart() {
  const data = await API.categoryTrend(6);
  if (!data || !data.length) return;

  destroyChart('cattrend');
  const ctx = document.getElementById('cattrend-chart').getContext('2d');
  const categories = Object.keys(data[0]).filter(k => k !== 'month');

  instances['cattrend'] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: data.map(d => d.month),
      datasets: categories.map((cat, i) => ({
        label: cat,
        data: data.map(d => d[cat] || 0),
        backgroundColor: COLORS[i % COLORS.length] + 'cc',
        borderRadius: i === categories.length - 1 ? { topLeft: 4, topRight: 4 } : 0,
        stack: 'stack',
      }))
    },
    options: {
      ...chartDefaults,
      scales: {
        x: { grid: { display: false }, stacked: true },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          stacked: true,
          ticks: { callback: v => '₹' + (v >= 1000 ? (v/1000).toFixed(0)+'k' : v) }
        }
      },
      plugins: {
        ...chartDefaults.plugins,
        legend: {
          display: true,
          position: 'bottom',
          labels: { boxWidth: 10, boxHeight: 10, padding: 14, borderRadius: 3, useBorderRadius: true }
        },
        tooltip: {
          ...chartDefaults.plugins.tooltip,
          callbacks: { label: ctx => ` ${ctx.dataset.label}: ₹${Number(ctx.raw).toLocaleString('en-IN')}` }
        }
      }
    }
  });
}

/* ── Budget vs Actual ── */
async function renderBudgetChart() {
  const today = new Date();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const year  = String(today.getFullYear());
  const data  = await API.budgetVsActual(month, year);
  if (!data) return;

  const el = document.getElementById('budget-section');

  el.innerHTML = `
    <div class="budget-item">
      <div class="budget-row">
        <span class="budget-name">Overall — ${data.month}</span>
        <span class="budget-nums">₹${Number(data.actual).toLocaleString('en-IN')} / ₹${Number(data.budget).toLocaleString('en-IN')}</span>
      </div>
      <div class="budget-track">
        <div class="budget-fill" style="
          width: ${Math.min(data.percent_used, 100)}%;
          background: ${data.actual > data.budget ? 'var(--coral)' : 'var(--teal)'}
        "></div>
      </div>
    </div>
    <div style="margin-top:12px;font-family:var(--ff-mono);font-size:11px;color:${data.actual > data.budget ? 'var(--coral)' : 'var(--teal)'}">
      ${data.status} &nbsp;·&nbsp; ${data.percent_used}% used
    </div>
    <div style="margin-top:6px;font-family:var(--ff-mono);font-size:10px;color:var(--text3)">
      Remaining: ₹${Number(data.remaining).toLocaleString('en-IN')}
    </div>
  `;
}

/* ── Top Expenses ── */
async function renderTopExpenses() {
  const data = await API.topExpenses(5);
  if (!data || !data.length) return;

  const ICONS = { Food:'🍽️', Travel:'✈️', Shopping:'🛍️', Bills:'⚡', Health:'💊', Entertainment:'🎬', Other:'📦' };

  document.getElementById('top-list').innerHTML = data.map((e, i) => `
    <div class="top-row">
      <div class="top-rank">${i + 1}</div>
      <div class="top-icon">${ICONS[e.category] || '📦'}</div>
      <div class="top-info">
        <div class="top-name">${e.description}</div>
        <div class="top-cat">${e.category || 'Uncategorized'} · ${e.date}</div>
      </div>
      <div class="top-amt">₹${Number(e.amount).toLocaleString('en-IN')}</div>
    </div>
  `).join('');
}