const form = document.querySelector('form');
const message = document.querySelector('#authMessage');

function showMessage(text, type = 'danger') {
  message.textContent = text;
  message.className = `alert alert-${type}`;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(form));
  const isRegister = form.id === 'registerForm';
  if (isRegister && values.password !== document.querySelector('#confirmPassword').value) {
    showMessage('Passwords do not match.');
    return;
  }
  const response = await fetch(isRegister ? '/api/auth/register' : '/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: values.username, password: values.password })
  });
  const result = await response.json();
  if (!response.ok) {
    showMessage(result.message || 'Unable to complete request.');
    return;
  }
  if (isRegister) {
    window.location.href = '/login?created=1';
  } else {
    window.location.href = '/';
  }
});
