/**
 * Router — handles view switching, URL routing, header tab management, modals,
 * sidebar navigation, header actions, and cross-view navigation.
 */

import { initPropertyRisk, destroyPropertyRisk, onRiskTabChange } from './views/property-risk/property-risk.js';
import { initPortfolio, destroyPortfolio, onPortfolioTabChange } from './views/portfolio/portfolio.js';
import { initClients, destroyClients } from './views/clients/clients.js';
import { initAssure, destroyAssure } from './views/assure/assure.js';
import { initOverview, destroyOverview } from './views/overview/overview.js';
import { refreshSidebarBadge } from './api/data-service.js';

import { hideLandingPage } from './views/landing/landing.js';
import { showInfo } from './utils/notifications.js';

// Admin & Expert lifecycle imports (simple inline modules — no heavy dependencies)
import { initAdminUsers, destroyAdminUsers } from './views/admin/admin.js';
import { initExpertMissions, destroyExpertMissions } from './views/expert/expert.js';

// ── Role State ────────────────────────────────────────────────
export type UserRole = 'assureur' | 'assure' | 'admin' | 'expert';
let currentRole: UserRole = 'assureur';

// ── View Config ────────────────────────────────────────────────
export const VIEW_TABS: Record<string, string[]> = {
  overview: ['Indicateurs', 'Répartition', 'Activité'],
  portfolio: ['Résumé', 'Carte', 'Tendances'],
  clients: [],
  settings: ['Compte', 'Sécurité', 'Facturation', 'Notifications', 'Connexions'],
  'property-risk': ['Localiser', 'Actuariat', 'Inspecter', 'Évaluer'],
  'assure-bien': [],
  'assure-travaux': [],
  'assure-engagement': [],
  'assure-dossier': [],
  'assureur-settings': ['Compte', 'Sécurité', 'Facturation', 'Notifications', 'Connexions'],
  'assure-settings': ['Compte', 'Sécurité', 'Facturation', 'Notifications', 'Connexions'],
  // Admin views
  'admin-overview': [],
  'admin-clients': [],
  'admin-experts': [],
  'admin-settings': ['Compte', 'Sécurité', 'Facturation', 'Notifications', 'Connexions'],
  // Expert views
  'expert-missions': [],
  'expert-clients': ['Résumé', 'Carte', 'Tendances'],
  'expert-settings': ['Compte', 'Sécurité', 'Facturation', 'Notifications', 'Connexions'],
};

// Map view name → base path
const ROUTES: Record<string, string> = {
  landing: '/',
  overview: '/assureur/dashboard',
  portfolio: '/assureur/portfolio',
  clients: '/assureur/clients',
  settings: '/assureur/settings',
  'property-risk': '/assureur/risk-hub',
  'assure-bien': '/assure/bien',
  'assure-travaux': '/assure/travaux',
  'assure-engagement': '/assure/engagement',
  'assure-dossier': '/assure/dossier',
  'assureur-settings': '/assureur/parametres',
  'assure-settings': '/assure/parametres',
  // Admin routes
  'admin-overview': '/admin/overview',
  'admin-clients': '/admin/clients',
  'admin-experts': '/admin/experts',
  'admin-settings': '/admin/settings',
  // Expert routes — only expert-missions is unique; clients/settings use assureur views
  'expert-missions': '/expert/missions',
  'expert-clients': '/expert/biens',
};

// Sub-tab keys per view that support deep-linking
const SUB_TAB_KEYS: Record<string, string[]> = {
  portfolio: ['summary', 'map', 'trends'],
  clients: [],
  settings: ['account', 'security', 'billing', 'notifications', 'connections'],
  'property-risk': ['locate', 'actuariat', 'inspect', 'evaluate'],
  'assure-bien': ['Vue d\'ensemble', 'Mes Travaux', 'Mon Engagement', 'Mon Dossier'],
  'assure-travaux': ['Vue d\'ensemble', 'Mes Travaux', 'Mon Engagement', 'Mon Dossier'],
  'assure-engagement': ['Vue d\'ensemble', 'Mes Travaux', 'Mon Engagement', 'Mon Dossier'],
  'assure-dossier': ['Vue d\'ensemble', 'Mes Travaux', 'Mon Engagement', 'Mon Dossier'],
  'assureur-settings': ['account', 'security', 'billing', 'notifications', 'connections'],
  'assure-settings': ['account', 'security', 'billing', 'notifications', 'connections'],
  'admin-settings': ['account', 'security', 'billing', 'notifications', 'connections'],
  'expert-settings': ['account', 'security', 'billing', 'notifications', 'connections'],
  'expert-clients': ['summary', 'map', 'trends'],
};

// Maps view+tab-key → content-key for showViewSubTab
const SUB_TAB_CONTENT: Record<string, Record<string, string>> = {
  portfolio: { summary: 'summary', map: 'map', trends: 'trends' },
  clients: {},
  settings: { account: 'account', security: 'security', billing: 'billing', notifications: 'notifications', connections: 'connections' },
  'property-risk': { locate: 'locate', actuariat: 'actuariat', inspect: 'inspect', evaluate: 'evaluate' },
  'assureur-settings': { account: 'account', security: 'security', billing: 'billing', notifications: 'notifications', connections: 'connections' },
  'assure-settings': { account: 'account', security: 'security', billing: 'billing', notifications: 'notifications', connections: 'connections' },
  'admin-settings': { account: 'account', security: 'security', billing: 'billing', notifications: 'notifications', connections: 'connections' },
  'expert-settings': { account: 'account', security: 'security', billing: 'billing', notifications: 'notifications', connections: 'connections' },
  'expert-clients': { summary: 'summary', map: 'map', trends: 'trends' },
};

/* ── Sub-tab helper: activate sub-tab for a view by tab-key ── */
function activateSubTab(viewName: string, tabKey: string): void {
  if (viewName === 'property-risk') {
    showPropertyRiskSubTab(tabKey);
    return;
  }
  if (SUB_TAB_CONTENT[viewName]?.[tabKey]) {
    showViewSubTab(viewName, tabKey);
  }
  if (viewName === 'portfolio' || viewName === 'expert-clients') {
    onPortfolioTabChange(tabKey);
  }
}

/* ── Redirect old routes to new canonical routes ──────────── */
const REDIRECTS: Record<string, { view: string; subTab?: string }> = {
  map: { view: 'property-risk', subTab: 'locate' },
  property: { view: 'property-risk', subTab: 'inspect' },
  assessments: { view: 'portfolio', subTab: 'summary' },
  assure: { view: 'assure-bien' },
  'espace-assure': { view: 'assure-bien' },
  // Backward compat: old flat paths → new /assureur/ prefixed paths
  dashboard: { view: 'overview' },
  portfolio: { view: 'portfolio' },
  clients: { view: 'clients' },
  settings: { view: 'settings' },
  'risk-hub': { view: 'property-risk' },
  assureur: { view: 'property-risk', subTab: 'evaluate' },
};

/* ── Parse URL path into { view, subTab? } ───────────────── */
function parseUrl(path: string): { view: string; subTab?: string } {
  const clean = path.replace(/\/$/, '');
  const parts = clean.split('/').filter(Boolean);

  if (parts.length === 0) return { view: 'landing' };

  if (parts[0] === 'assure' && parts.length > 1) {
    const sub = parts[1];
    const map: Record<string, string> = { bien: 'assure-bien', travaux: 'assure-travaux', engagement: 'assure-engagement', dossier: 'assure-dossier', parametres: 'assure-settings' };
    if (map[sub]) return { view: map[sub] };
  }

  if (parts[0] === 'assureur' && parts.length > 1) {
    const sub = parts[1];
    const map: Record<string, string> = {
      dashboard: 'overview',
      portfolio: 'portfolio',
      clients: 'clients',
      settings: 'settings',
      'risk-hub': 'property-risk',
      parametres: 'assureur-settings',
    };
    if (map[sub]) return { view: map[sub] };
  }

  // Admin routes — clients/settings redirect to shared assureur views
  if (parts[0] === 'admin' && parts.length > 1) {
    const sub = parts[1];
    const map: Record<string, string> = { overview: 'admin-overview', clients: 'admin-clients', experts: 'admin-experts', settings: 'admin-settings' };
    if (map[sub]) return { view: map[sub] };
  }

  // Expert routes — clients/settings redirect to shared assureur views
  if (parts[0] === 'expert' && parts.length > 1) {
    const sub = parts[1];
    const map: Record<string, string> = { missions: 'expert-missions', clients: 'expert-clients', biens: 'expert-clients', settings: 'expert-settings' };
    if (map[sub]) return { view: map[sub] };
  }

  const viewName = parts[0];
  const subTab = parts.length > 1 ? parts[1] : undefined;

  if (viewName === 'auth' && subTab) {
    return { view: 'auth-' + subTab };
  }

  // Handle direct URLs like /auth-sign-in → auth-sign-in view
  if (viewName.startsWith('auth-')) {
    return { view: viewName };
  }

  if (REDIRECTS[viewName]) {
    return REDIRECTS[viewName];
  }

  if (!ROUTES[viewName]) return { view: 'overview' };

  if (subTab && SUB_TAB_KEYS[viewName]?.includes(subTab)) {
    return { view: viewName, subTab };
  }

  return { view: viewName };
}

/* ── Build URL path from view name and optional sub-tab ──── */
function buildPath(viewName: string, subTab?: string): string {
  const base = ROUTES[viewName] || `/${viewName}`;
  if (subTab && SUB_TAB_KEYS[viewName]?.includes(subTab)) {
    return `${base}/${subTab}`;
  }
  return base;
}

/* ── Navigate to a view/sub-tab (updates URL + switches view) ─ */
export function navigateTo(viewName: string, subTab?: string): void {
  const path = buildPath(viewName, subTab);
  window.history.pushState({ view: viewName, subTab: subTab || null }, '', path);
  switchView(viewName, subTab);
}

/* ── Handle browser back/forward ───────────────────────────── */
function setupPopstate(): void {
  window.addEventListener('popstate', (e) => {
    const state = e.state as { view?: string; subTab?: string | null } | null;
    if (state?.view) {
      switchView(state.view, state.subTab || undefined);
    } else {
      const { view, subTab } = parseUrl(window.location.pathname);
      switchView(view, subTab);
    }
  });
}

/* ── Get initial view/sub-tab from URL ────────────────────── */
function getInitialRoute(): { view: string; subTab?: string } {
  return parseUrl(window.location.pathname);
}

/* ── Role Management ───────────────────────────────────────── */
export function setRole(role: UserRole): void {
  currentRole = role;
  updateSidebarVisibility();

  // Refresh badge when role changes
  refreshSidebarBadge();

  // Navigate to default view of selected role if current view does not match
  const activeView = document.querySelector('.sidebar-nav .nav-item.active')?.getAttribute('data-view') || '';
  if (role === 'assure' && !activeView.startsWith('assure-')) {
    navigateTo('assure-bien');
  } else if (role === 'assureur' && (activeView.startsWith('assure-') || activeView.startsWith('admin-') || activeView.startsWith('expert-'))) {
    navigateTo('overview');
  } else if (role === 'admin' && !activeView.startsWith('admin-')) {
    navigateTo('admin-overview');
  } else if (role === 'expert' && !activeView.startsWith('expert-')) {
    navigateTo('expert-missions');
  }
}

export function updateSidebarVisibility(): void {
  const assureurItems = document.querySelectorAll('.nav-role-assureur');
  const assureItems = document.querySelectorAll('.nav-role-assure');
  const adminItems = document.querySelectorAll('.nav-role-admin');
  const expertItems = document.querySelectorAll('.nav-role-expert');
  const roleBadge = document.getElementById('sidebarRoleBadge');
  const roleBtnText = document.getElementById('roleSwitchText');

  // Hide ALL role-specific items first
  assureurItems.forEach(el => (el as HTMLElement).style.display = 'none');
  assureItems.forEach(el => (el as HTMLElement).style.display = 'none');
  adminItems.forEach(el => (el as HTMLElement).style.display = 'none');
  expertItems.forEach(el => (el as HTMLElement).style.display = 'none');

  // Show items for the current role + set badge + next-mode button text
  if (currentRole === 'assure') {
    assureItems.forEach(el => (el as HTMLElement).style.display = '');
    if (roleBadge) {
      roleBadge.textContent = 'ESPACE ASSURÉ';
      roleBadge.className = 'sidebar-role-badge assure';
    }
    if (roleBtnText) roleBtnText.textContent = 'Mode Admin';
  } else if (currentRole === 'admin') {
    adminItems.forEach(el => (el as HTMLElement).style.display = '');
    if (roleBadge) {
      roleBadge.textContent = 'ESPACE ADMIN';
      roleBadge.className = 'sidebar-role-badge admin';
    }
    if (roleBtnText) roleBtnText.textContent = 'Mode Expert';
  } else if (currentRole === 'expert') {
    expertItems.forEach(el => (el as HTMLElement).style.display = '');
    if (roleBadge) {
      roleBadge.textContent = 'ESPACE EXPERT';
      roleBadge.className = 'sidebar-role-badge expert';
    }
    if (roleBtnText) roleBtnText.textContent = 'Mode Assureur';
  } else {
    // assureur (default)
    assureurItems.forEach(el => (el as HTMLElement).style.display = '');
    if (roleBadge) {
      roleBadge.textContent = 'ESPACE ASSUREUR';
      roleBadge.className = 'sidebar-role-badge assureur';
    }
    if (roleBtnText) roleBtnText.textContent = 'Mode Assuré';
  }
}

function setupRoleSwitcher(): void {
  const btn = document.getElementById('roleSwitchBtn');
  if (btn) {
    btn.addEventListener('click', () => {
      // Cycle: assureur → assure → admin → expert → assureur
      const nextRole: UserRole =
        currentRole === 'assureur' ? 'assure'
        : currentRole === 'assure' ? 'admin'
        : currentRole === 'admin' ? 'expert'
        : 'assureur';
      setRole(nextRole);
    });
  }
}

/* ── Activate nav item for the given view ──────────────────── */
function activateNavItem(viewName: string): void {
  const navItems = document.querySelectorAll('#sidebar .nav-item');
  navItems.forEach(nav => {
    const v = nav.getAttribute('data-view');
    nav.classList.toggle('active', v === viewName);
  });

  // Auto detect role from viewName
  if (viewName.startsWith('assure-')) {
    currentRole = 'assure';
  } else if (viewName.startsWith('admin-')) {
    currentRole = 'admin';
  } else if (viewName.startsWith('expert-')) {
    currentRole = 'expert';
  } else if (viewName !== 'settings') {
    currentRole = 'assureur';
  }
  updateSidebarVisibility();
}

// ── Sidebar Toggle ─────────────────────────────────────────────
export function setupSidebarToggle(): void {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('sidebarToggle');
  const toggleIcon = toggleBtn?.querySelector('.toggle-icon');

  if (sidebar && toggleBtn && toggleIcon) {
    const isExpanded = sidebar.classList.contains('expanded');
    toggleBtn.setAttribute('aria-expanded', String(isExpanded));
    toggleIcon.textContent = isExpanded ? 'menu_open' : 'menu';

    toggleBtn.addEventListener('click', () => {
      const nowExpanded = sidebar.classList.toggle('expanded');
      toggleBtn.setAttribute('aria-expanded', String(nowExpanded));
      toggleIcon.textContent = nowExpanded ? 'menu_open' : 'menu';
      window.dispatchEvent(new Event('resize'));
    });
  }
}

// ── Sidebar Navigation ─────────────────────────────────────────
export function setupSidebarNavigation(): void {
  setupRoleSwitcher();

  const navItems = document.querySelectorAll('#sidebar .nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const viewName = item.getAttribute('data-view');
      if (!viewName) return;
      if (viewName === 'logout') {
        import('./api/auth.js').then(({ logout }) => {
          logout().catch(() => {});
          navigateTo('auth-sign-in');
        });
        return;
      }
      activateNavItem(viewName);
      navigateTo(viewName);
    });
  });

  const { view, subTab } = getInitialRoute();
  activateNavItem(view);
  switchView(view, subTab);
}

// ── View Switching ─────────────────────────────────────────────
export function switchView(viewName: string, subTab?: string): void {
  if (viewName === 'landing') return; // landing page is already visible
  hideLandingPage();

  if (viewName && viewName.startsWith('auth-')) {
    import('./views/auth/auth.js').then(({ showAuthPage }) => {
      showAuthPage(viewName.replace('auth-', ''));
    });
    return;
  }

  const dashboard = document.querySelector('.dashboard-container') as HTMLElement | null;
  if (dashboard) dashboard.style.display = '';
  document.querySelectorAll('.auth-view').forEach(el => el.classList.remove('active'));

  // Map all role-specific settings views to shared panel
  const panelViewName = viewName === 'assureur-settings' || viewName === 'assure-settings' || viewName === 'admin-settings' || viewName === 'expert-settings' ? 'settings'
    : viewName === 'admin-clients' ? 'clients'
    : viewName === 'expert-clients' ? 'portfolio'
    : viewName;

  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  const targetView = document.getElementById(`view-${panelViewName}`);
  if (targetView) targetView.classList.add('active');
  updateHeaderTabs(viewName, subTab);

  const clientsPanel = document.getElementById('clientsDetailPanel');
  if (clientsPanel?.classList.contains('active') && viewName !== 'clients') {
    clientsPanel.classList.remove('active');
    document.querySelector('.clients-tab-content[data-content="info"]')?.classList.add('active');
  }

  // Lifecycle for view-specific modules
  if (viewName === 'overview') {
    requestAnimationFrame(() => initOverview());
  } else {
    destroyOverview();
  }

  if (viewName === 'property-risk') {
    requestAnimationFrame(() => initPropertyRisk());
  } else {
    destroyPropertyRisk();
  }

  if (viewName === 'portfolio' || viewName === 'expert-clients') {
    requestAnimationFrame(() => initPortfolio());
  } else {
    destroyPortfolio();
  }

  if (viewName === 'clients' || viewName === 'admin-clients') {
    requestAnimationFrame(() => initClients());
  } else {
    destroyClients();
  }

  if (viewName.startsWith('assure-')) {
    requestAnimationFrame(() => initAssure(viewName));
  } else {
    destroyAssure();
  }

  // Settings views — init for all role-specific settings
  if (viewName === 'settings' || viewName === 'assureur-settings' || viewName === 'assure-settings' || viewName === 'admin-settings' || viewName === 'expert-settings') {
    import('./views/settings/settings.js').then(m => m.initSettings());
  }

  // Admin views lifecycle
  if (viewName === 'admin-overview') {
    import('./views/admin/admin.js').then(m => m.initAdminOverview ? m.initAdminOverview() : null);
  } else if (viewName === 'admin-experts') {
    import('./views/admin/admin.js').then(m => m.initAdminExperts ? m.initAdminExperts() : null);
  }

  // Expert views lifecycle
  if (viewName === 'expert-missions') {
    requestAnimationFrame(() => initExpertMissions());
  } else {
    destroyExpertMissions();
  }
}

// ── Header Tabs ────────────────────────────────────────────────
export function updateHeaderTabs(viewName: string, activeTabKey?: string): void {
  const headerTabs = document.getElementById('headerTabs');
  if (!headerTabs) return;

  const tabNames = VIEW_TABS[viewName] || [];
  const subTabKeys = SUB_TAB_KEYS[viewName] || [];

  // Push actions right when tabs hidden, reset margin when tabs visible
  const headerActions = document.querySelector('.header-actions') as HTMLElement | null;

  if (tabNames.length === 0) {
    headerTabs.style.display = 'none';
    if (headerActions) headerActions.style.marginLeft = 'auto';
    return;
  }
  headerTabs.style.display = '';
  if (headerActions) headerActions.style.marginLeft = '';

  // Determine active tab key
  let activeKey = activeTabKey || subTabKeys[0] || '';
  // For assure views, derive active tab from the view name
  if (viewName.startsWith('assure-') && !activeTabKey) {
    const tabFromView = viewName.replace('assure-', '');
    if (subTabKeys.includes(tabFromView)) {
      activeKey = tabFromView;
    }
  }



  headerTabs.innerHTML = tabNames.map((name, i) => {
    const rawKey = name.toLowerCase();
    const tabKey = subTabKeys[i] || rawKey;
    const isSettingsView = viewName === 'settings' || viewName === 'assureur-settings' || viewName === 'assure-settings' || viewName === 'admin-settings' || viewName === 'expert-settings';
    const icon = isSettingsView
      ? `<span class="material-symbols-outlined tab-icon">${subTabKeys[i] === 'account' ? 'person' : subTabKeys[i] === 'security' ? 'lock' : subTabKeys[i] === 'billing' ? 'credit_card' : subTabKeys[i] === 'notifications' ? 'notifications' : 'link'}</span>`
      : '';
    const isActive = tabKey === activeKey;
    return `<button class="tab-btn ${isActive ? 'active' : ''}" data-tab="${tabKey}">${icon}${name}</button>`;
  }).join('');

  setupHeaderTabs();

  if (activeKey) {
    activateSubTab(viewName, activeKey);
  }
}

export function setupHeaderTabs(): void {
  const ASSURE_VIEW_MAP: Record<string, string> = {
    bien: 'assure-bien',
    travaux: 'assure-travaux',
    engagement: 'assure-engagement',
    dossier: 'assure-dossier',
  };

  const tabs = document.querySelectorAll('.header-tabs .tab-btn');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const tabKey = tab.getAttribute('data-tab');
      if (!tabKey) return;

      const activeView = document.querySelector('.sidebar-nav .nav-item.active');
      const viewName = activeView?.getAttribute('data-view') || '';

      // Handle assure view navigation - map tab key to a different view entirely
      if (viewName.startsWith('assure-') && ASSURE_VIEW_MAP[tabKey]) {
        navigateTo(ASSURE_VIEW_MAP[tabKey]);
        return;
      }

      navigateTo(viewName, tabKey);
    });
  });
}

// ── Sub-Tab Content Switching ──────────────────────────────────
export function showPropertyRiskSubTab(tabName: string): void {
  const panels = document.querySelectorAll('.risk-tab-content');
  if (!panels.length) return;
  const contentKey = SUB_TAB_CONTENT['property-risk']?.[tabName];
  if (!contentKey) return;
  panels.forEach(el => el.classList.remove('active'));
  const target = document.querySelector(`.risk-tab-content[data-content="${contentKey}"]`);
  if (target) target.classList.add('active');

  onRiskTabChange(tabName);
}

export function showViewSubTab(viewName: string, tabName: string): void {
  const prefix = viewName === 'portfolio' || viewName === 'expert-clients' ? 'portfolio'
    : viewName === 'clients' ? 'clients'
    : viewName === 'property-risk' ? 'risk'
    : 'settings';
  const selector = `.${prefix}-tab-content`;
  const panels = document.querySelectorAll(selector);
  if (!panels.length) return;

  const contentKey = SUB_TAB_CONTENT[viewName]?.[tabName];
  if (!contentKey) {
    const target = document.querySelector(`${selector}[data-content="${tabName}"]`);
    if (target) {
      panels.forEach(el => el.classList.remove('active'));
      target.classList.add('active');
    }
    return;
  }
  panels.forEach(el => el.classList.remove('active'));
  const target = document.querySelector(`${selector}[data-content="${contentKey}"]`);
  if (target) target.classList.add('active');
}

// ── Modals ─────────────────────────────────────────────────────
export function openModal(id: string): void {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('open');
}

export function closeModal(id: string): void {
  const modal = document.getElementById(id);
  if (modal) modal.classList.remove('open');
}

export function setupModals(): void {
  document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) overlay.classList.remove('open');
    });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-overlay.open').forEach(m => m.classList.remove('open'));
    }
  });
}

// ── Header Actions ─────────────────────────────────────────────
export function setupHeaderActions(): void {
  const themeBtn = document.getElementById('headerThemeToggle');
  if (themeBtn) {
    const saved = localStorage.getItem('previa-dark-mode');
    if (saved === 'true') document.documentElement.classList.add('dark-mode');

    themeBtn.addEventListener('click', () => {
      const isDark = document.documentElement.classList.toggle('dark-mode');
      localStorage.setItem('previa-dark-mode', String(isDark));
      const settingsToggle = document.getElementById('settingsDarkMode') as HTMLInputElement | null;
      if (settingsToggle) settingsToggle.checked = isDark;
    });
  }

  const trigger = document.getElementById('profileTrigger');
  const menu = document.getElementById('profileMenu');
  if (trigger && menu) {
    trigger.addEventListener('click', (e) => {
      e.stopPropagation();
      menu.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (!menu.contains(target) && !trigger.contains(target)) menu.classList.remove('open');
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') menu.classList.remove('open');
    });

    menu.querySelectorAll('.profile-menu-item').forEach(item => {
      item.addEventListener('click', () => {
        menu.classList.remove('open');
        const action = (item as HTMLElement).getAttribute('data-action');
        if (!action) return;

        switch (action) {
          case 'settings': {
            navigateTo('settings');
            break;
          }
          case 'profile': {
            navigateTo('settings', 'account');
            break;
          }
          case 'logout':
            import('./api/auth.js').then(({ logout }) => {
              logout().catch(() => {});
              navigateTo('auth-sign-in');
            });
            break;
          default: {
            const labels: Record<string, string> = { billing: 'Plan & Facturation', pricing: 'Tarifs', faq: 'FAQ' };
            showInfo(`Page « ${labels[action] || action} » — À implémenter.`);
          }
        }
      });
    });
  }
}

// ── Cross-View Navigation ──────────────────────────────────────
export function setupCrossNavigation(): void {
  document.querySelectorAll('.portfolio-prop').forEach(card => {
    card.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (target.closest('.portfolio-prop-client')) {
        navigateTo('clients');
        return;
      }
      navigateTo('property-risk', 'inspect');
    });
  });
}

// ── Initialize Router (called from main.ts) ──────────────────
export function initRouter(): void {
  setupPopstate();

  const { view, subTab } = getInitialRoute();
  const path = buildPath(view, subTab);
  window.history.replaceState({ view, subTab: subTab || null }, '', path);
}
