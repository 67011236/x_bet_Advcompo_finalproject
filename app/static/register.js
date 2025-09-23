// toggle show/hide password
document.querySelectorAll('.eye').forEach(btn => {
  btn.addEventListener('click', () => {
    const targetId = btn.getAttribute('data-target');
    const input = document.getElementById(targetId);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
    // สลับไอคอนเบา ๆ
    btn.textContent = input.type === 'password' ? '👁️' : '🙈';
  });
});

// demo submit (กันหน้า refresh และแสดงข้อความ)
document.getElementById('signup-form').addEventListener('submit', (e) => {
  e.preventDefault();
  const err = document.getElementById('err');
  const msg = document.getElementById('msg');

  const pw = document.getElementById('password').value;
  const pw2 = document.getElementById('confirm_password').value;
  if (pw !== pw2) {
    err.textContent = 'Passwords do not match';
    msg.textContent = '';
    return;
  }
  err.textContent = '';
  msg.textContent = '✅ Ready to submit';
  // ตรงนี้ค่อย fetch ไปหา backend จริง ๆ ของคุณได้
});
