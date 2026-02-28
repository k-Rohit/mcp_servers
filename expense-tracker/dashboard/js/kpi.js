// js/kpi.js
async function renderKPI() {
  const data = await API.kpi();
  if (!data) return;

  const fmt = n => '₹' + Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 });
  const momColor = data.mom_change > 0 ? 'coral' : 'teal';
  const momSign  = data.mom_change > 0 ? '+' : '';

  const cards = [
    { label: 'Today',         value: fmt(data.today),         sub: 'Spent today',            color: 'lime'   },
    { label: 'This Week',     value: fmt(data.this_week),      sub: 'Current week total',     color: 'violet' },
    { label: 'This Month',    value: fmt(data.this_month),     sub: 'Month to date',          color: 'teal'   },
    { label: 'Avg / Day',     value: fmt(data.avg_per_day),    sub: 'This month average',     color: 'amber'  },
    { label: 'vs Last Month', value: `${momSign}${data.mom_change}%`, sub: `Last: ${fmt(data.last_month)}`, color: momColor },
  ];

  const container = document.getElementById('kpi-grid');
  container.innerHTML = cards.map((c, i) => `
    <div class="kpi-card" data-color="${c.color}" style="animation-delay:${i * 0.07}s">
      <div class="kpi-label">${c.label}</div>
      <div class="kpi-value">${c.value}</div>
      <div class="kpi-sub">${c.sub}</div>
    </div>
  `).join('');
}