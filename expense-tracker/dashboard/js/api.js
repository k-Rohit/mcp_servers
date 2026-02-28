// js/api.js
const BASE = 'http://localhost:8000';

async function apiFetch(path) {
  try {
    const res = await fetch(BASE + path);
    if (!res.ok) throw new Error(res.statusText);
    return await res.json();
  } catch(e) {
    console.error('API error:', path, e);
    return null;
  }
}

const API = {
  kpi:            ()           => apiFetch('/api/stats/kpi'),
  daily:          (days=30)    => apiFetch(`/api/stats/daily?days=${days}`),
  category:       (month='')   => apiFetch(`/api/stats/category${month ? '?month='+month : ''}`),
  monthly:        (months=6)   => apiFetch(`/api/stats/monthly?months=${months}`),
  categoryTrend:  (months=6)   => apiFetch(`/api/stats/category-trend?months=${months}`),
  paymentMethod:  (month='')   => apiFetch(`/api/stats/payment-method${month ? '?month='+month : ''}`),
  topExpenses:    (limit=5)    => apiFetch(`/api/stats/top-expenses?limit=${limit}`),
  weekday:        ()           => apiFetch('/api/stats/weekday-pattern'),
  budgetVsActual: (m,y)        => apiFetch(`/api/budgets/vs-actual?month=${m}&year=${y}`),
  expenses:       (p={})       => {
    const q = new URLSearchParams(p).toString();
    return apiFetch(`/api/expenses/${q ? '?'+q : ''}`);
  },
};