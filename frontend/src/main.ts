/**
 * Main entry — imports all view modules and initializes the app.
 */
import './base.css';
import './style.css';
import './views/assure/assure.css';
import './views/auth/auth.css';
import './views/landing/landing.css';
import './views/clients/clients.css';
// Material Web Components
import '@material/web/iconbutton/icon-button.js';
import '@material/web/icon/icon.js';
import '@material/web/elevation/elevation.js';
import '@material/web/slider/slider.js';
import '@material/web/progress/linear-progress.js';
import '@material/web/ripple/ripple.js';

// Core router
import {
  initRouter,
  setupSidebarToggle,
  setupSidebarNavigation,
  setupHeaderActions,
  setupCrossNavigation,
  setupModals,
} from './router.js';

// View modules
import { initClients } from './views/clients/clients.js';
import { initOverview } from './views/overview/overview.js';
import { initAuth } from './views/auth/auth.js';
import { initAssure } from './views/assure/assure.js';
import { initLanding } from './views/landing/landing.js';


document.addEventListener('DOMContentLoaded', async () => {
  // ── AUTH DISABLED for frontend development ──
  // Don't force any role — let the router parse the URL
  const { navigateTo, setRole } = await import('./router.js');
  setRole('assureur');

  // Core app infrastructure
  setupSidebarToggle();
  setupSidebarNavigation();
  setupHeaderActions();
  setupCrossNavigation();
  setupModals();
  initLanding();
  initRouter();

  // Landing page is visible at '/' — CTA buttons navigate to dashboards

  // View-specific interactions
  initClients();
  initOverview();
  initAuth();

  // Refresh sidebar badge (pending submissions count)
  import('./api/data-service.js').then(({ refreshSidebarBadge }) => {
    refreshSidebarBadge();
  });
});
