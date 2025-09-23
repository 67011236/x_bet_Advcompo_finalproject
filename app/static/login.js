const form = document.getElementById('loginForm');
const emailEl = document.getElementById('email');
const passEl = document.getElementById('password');
const statusEl = document.getElementById('status');
const eyeBtn = document.querySelector('.eye');
const adminLinks = document.querySelectorAll('[data-admin]');
const ADMIN_EMAIL = 'TestH2W@gmail.com';

// toggle password
eyeBtn?.addEventListener('click', () => {
  passEl.type = passEl.type === 'password' ? 'text' : 'password';
});

// hide admin by default
adminLinks.forEach(a => a.style.display = 'none');

form.addEventListener('submit', e => {
  e.preventDefault();
  const email = emailEl.value.trim();

  if(!email){ statusEl.textContent="Please enter email"; statusEl.style.color="var(--error)"; return; }
  if(!passEl.value){ statusEl.textContent="Please enter password"; statusEl.style.color="var(--error)"; return; }

  statusEl.textContent = "Logged in"; statusEl.style.color="lightgreen";

  if(email.toLowerCase() === ADMIN_EMAIL.toLowerCase()){
    adminLinks.forEach(a => a.style.display = 'inline');
  }
});
