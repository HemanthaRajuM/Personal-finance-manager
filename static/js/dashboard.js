const monthInput = document.querySelector('#monthInput');
const expenseForm = document.querySelector('#expenseForm');
const message = document.querySelector('#message');
const rows = document.querySelector('#expenseRows');
const loading = document.querySelector('#loading');

const today = new Date();
const monthValue = today.toISOString().slice(0, 7);
monthInput.value = monthValue;
document.querySelector('#expenseDate').value = today.toISOString().slice(0, 10);

function money(value) {
  return `₹${Number(value || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function showMessage(text, type = 'success') {
  message.textContent = text;
  message.className = `alert alert-${type}`;
}

async function loadDashboard() {
  loading.textContent = 'Loading...';
  const month = monthInput.value;
  const [summaryResponse, expensesResponse] = await Promise.all([
    fetch(`/api/summary?month=${encodeURIComponent(month)}`),
    fetch('/api/expenses')
  ]);
  if (!summaryResponse.ok || !expensesResponse.ok) throw new Error('Please log in to view your dashboard.');
  const summary = await summaryResponse.json();
  const expenses = await expensesResponse.json();
  const values = summary.data || {};
  document.querySelector('#incomeValue').textContent = money(values.income);
  document.querySelector('#expenseValue').textContent = money(values.expenses);
  document.querySelector('#savingsValue').textContent = money(values.savings);
  const data = expenses.data || [];
  document.querySelector('#transactionCount').textContent = data.length;
  rows.innerHTML = data.length ? data.map(item => `<tr><td>${item.date}</td><td>${item.description}</td><td><span class="badge text-bg-light">${item.category}</span></td><td class="text-end amount">${money(item.amount)}</td></tr>`).join('') : '<tr><td colspan="4" class="text-center text-secondary py-5">No expenses recorded.</td></tr>';
  loading.textContent = `${data.length} transaction${data.length === 1 ? '' : 's'}`;
}

expenseForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(expenseForm));
  const response = await fetch('/api/expenses', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
  const result = await response.json();
  if (!response.ok) return showMessage(result.message || 'Unable to add expense.', 'danger');
  showMessage('Expense added successfully.');
  expenseForm.reset();
  document.querySelector('#expenseDate').value = new Date().toISOString().slice(0, 10);
  await loadDashboard();
});

monthInput.addEventListener('change', loadDashboard);
document.querySelector('#logoutButton').addEventListener('click', async () => { await fetch('/api/auth/logout', { method: 'POST' }); window.location.href = '/'; });
loadDashboard().catch(error => showMessage(error.message, 'warning'));
