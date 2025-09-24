// toggle show/hide password (ถ้าคุณมีปุ่มตาอยู่แล้วคงไว้ได้)
document.querySelectorAll('.eye').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetId = btn.getAttribute('data-target');
    const input = document.getElementById(targetId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    btn.textContent = input.type === 'password' ? '👁' : '🙈';
  });
});

// submit form -> POST /api/register
document.getElementById('signup-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const err = document.getElementById('err');
  const msg = document.getElementById('msg');

  const body = {
    full_name: document.getElementById('full_name').value.trim(),
    age: Number(document.getElementById('age').value),
    phone: document.getElementById('phone').value.trim(),
    email: document.getElementById('email').value.trim(),
    password: document.getElementById('password').value,
    confirm_password: document.getElementById('confirm_password').value,
    agree: document.getElementById('agree').checked
  };

  err.textContent = '';
  msg.textContent = '⏳ Submitting...';

  try {
    const res = await fetch('/api/register', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body)
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || 'Register failed');
    }

    msg.textContent = `✅ Registered: ${data.full_name} (${data.email})`;
  } catch (ex) {
    msg.textContent = '';
    err.textContent = `❌ ${ex.message}`;
  }
});
