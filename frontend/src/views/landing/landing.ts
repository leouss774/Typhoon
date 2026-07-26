import { navigateTo, setRole } from '../../router.js';

export function showLandingPage(): void {
  document.querySelectorAll('.auth-view').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.view-panel').forEach(el => el.classList.remove('active'));

  const landing = document.getElementById('view-landing');
  if (landing) landing.classList.add('active');

  const dashboard = document.querySelector('.dashboard-container') as HTMLElement | null;
  if (dashboard) dashboard.style.display = 'none';
}

export function hideLandingPage(): void {
  const landing = document.getElementById('view-landing');
  if (landing) {
    landing.style.opacity = '0';
    landing.style.transform = 'scale(0.98)';
    setTimeout(() => {
      landing.classList.remove('active');
      landing.style.opacity = '';
      landing.style.transform = '';
    }, 250);
  }

  const dashboard = document.querySelector('.dashboard-container') as HTMLElement | null;
  if (dashboard) {
    dashboard.style.display = '';
    dashboard.style.opacity = '0';
    dashboard.style.transform = 'translateY(8px)';
    requestAnimationFrame(() => {
      dashboard.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      dashboard.style.opacity = '1';
      dashboard.style.transform = 'translateY(0)';
      setTimeout(() => {
        dashboard.style.transition = '';
      }, 350);
    });
  }
}

export function initLanding(): void {
  wireLandingCtas();
}

function wireLandingCtas(): void {
  document.getElementById('view-landing')?.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const btn = target.closest('.landing-cta-assureur');
    if (btn) {
      e.preventDefault();
      hideLandingPage();
      setRole('assureur');
      navigateTo('overview');
      return;
    }
    const btn2 = target.closest('.landing-cta-assure');
    if (btn2) {
      e.preventDefault();
      hideLandingPage();
      setRole('assure');
      navigateTo('assure-bien');
    }
  });
}
