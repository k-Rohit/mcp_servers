// js/table.js
let allExpenses = [];

async function loadExpenses() {
  const data = await API.expenses();
  if (!data) return;
  allExpenses = data;
  renderTable(allExpenses);
}

function renderTable(data) {
  const ICONS = { Food:'🍽️', Travel:'✈️', Shopping:'🛍️', Bills:'⚡', Health:'💊', Entertainment:'🎬', Other:'📦' };
  const tbody = document.getElementById('expense-tbody');

  if (!data.length) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;color:var(--text3);font-family:var(--ff-mono);font-size:11px;padding:24px">No expenses found</td></tr>`;
    return;
  }

  tbody.innerHTML = data.slice(0, 100).map(e => `
    <tr>
      <td class="td-mono">${e.date}</td>
      <td class="td-desc">
        <span style="margin-right:8px">${ICONS[e.category] || '📦'}</span>${e.description}
      </td>
      <td><span class="badge badge-${(e.category || 'other').toLowerCase()}">${e.category || 'Other'}</span></td>
      <td><span class="badge badge-${(e.payment_method || 'cash').toLowerCase()}">${e.payment_method || 'cash'}</span></td>
      <td class="td-amount">₹${Number(e.amount).toLocaleString('en-IN')}</td>
    </tr>
  `).join('');
}

function initTableFilters() {
  const search   = document.getElementById('search-input');
  const catSel   = document.getElementById('cat-filter');
  const paySel   = document.getElementById('pay-filter');

  function applyFilters() {
    const s = search.value.toLowerCase();
    const c = catSel.value;
    const p = paySel.value;

    const filtered = allExpenses.filter(e => {
      const matchSearch = !s || e.description.toLowerCase().includes(s);
      const matchCat    = !c || e.category === c;
      const matchPay    = !p || e.payment_method === p;
      return matchSearch && matchCat && matchPay;
    });

    renderTable(filtered);
  }

  search.addEventListener('input', applyFilters);
  catSel.addEventListener('change', applyFilters);
  paySel.addEventListener('change', applyFilters);
}