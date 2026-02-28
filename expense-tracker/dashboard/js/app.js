// js/app.js

async function renderAll() {
  await Promise.all([
    renderKPI(),
    renderDailyChart(),
    renderCategoryChart(),
    renderMonthlyChart(),
    renderPaymentChart(),
    renderWeekdayChart(),
    renderCategoryTrendChart(),
    renderBudgetChart(),
    renderTopExpenses(),
    loadExpenses(),
  ]);

  // update timestamp
  document.getElementById('last-updated').textContent =
    'Updated ' + new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
}

function init() {
  initTableFilters();
  renderAll();

  // auto refresh every 30s
  setInterval(renderAll, 30_000);
}

document.addEventListener('DOMContentLoaded', init);