/**
 * Overview view module — loads dashboard stats from API.
 * Populates stat cards, pending submissions, activity timeline, and sidebar badge.
 */
import { fetchDashboardStats, fetchAssessmentStats, fetchPendingSubmissions, refreshSidebarBadge, isApiAvailable, type PendingSubmission, type AssessmentStats } from '../../api/data-service.js';

let initialized = false;
let carouselInterval: ReturnType<typeof setInterval> | null = null;

export function initOverview(): void {
  if (initialized) return;
  initialized = true;
  loadStats();
}

export function destroyOverview(): void {
  initialized = false;
  if (carouselInterval !== null) {
    clearInterval(carouselInterval);
    carouselInterval = null;
  }
}

async function loadStats(): Promise<void> {
  try {
    const [stats, assessStats, pendingSubs] = await Promise.all([
      fetchDashboardStats(),
      fetchAssessmentStats(),
      fetchPendingSubmissions(),
    ]);

    // 1. Populate stat cards (new IDs matching the rich dashboard)
    const statCards: Record<string, string> = {
      'ovStatTotalClients': String(stats.totalClients),
      'ovStatTotalProps': String(stats.totalProperties),
      'ovStatAssessments': String(stats.totalAssessments),
    };

    for (const [id, val] of Object.entries(statCards)) {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    }

    // Update banner completion card
    updateBannerStats(stats, assessStats);

    // Update pending submissions count in floating card
    updatePendingSubmissionBadge(pendingSubs.length);

    // Update sidebar notification badge (via shared function)
    refreshSidebarBadge();

    console.log('[Overview] Stats loaded:', { stats, assessStats, pendingSubs: pendingSubs.length });

    if (!isApiAvailable()) {
      showApiBanner();
    }

    // Start carousel animation
    initCarousel();
  } catch (err) {
    console.warn('[Overview] Failed to load stats:', err);
    showApiBanner();
  }
}

/* ── Banner stats update ─────────────────────────────── */

function updateBannerStats(stats: any, assessStats: AssessmentStats): void {
  const scoreEl = document.getElementById('overviewBannerScore');
  if (scoreEl && assessStats.total > 0) {
    const avg = assessStats.evalue > 0
      ? Math.round(assessStats.recent.reduce((s, a) => s + (a.globalScore || 0), 0) / Math.max(assessStats.recent.length, 1))
      : null;
    if (avg !== null) {
      scoreEl.textContent = String(avg);
    }
  }

  // Update client count and secured count in the completion footer
  const statClients = document.getElementById('overviewStatClients');
  if (statClients) {
    statClients.textContent = `${stats.activeClients} clients`;
  }
  const statSecurises = document.getElementById('overviewStatSecurises');
  if (statSecurises) {
    statSecurises.textContent = `${stats.activeClients} sécurisés`;
  }

  // Update risk labels
  const riskLabel = document.getElementById('overviewPropRisk');
  if (riskLabel && stats.totalAssessments > 0) {
    const avgScore = stats.avgScore;
    if (avgScore <= 30) riskLabel.textContent = 'Risque Faible';
    else if (avgScore <= 60) riskLabel.textContent = 'Risque Modéré';
    else riskLabel.textContent = 'Risque Élevé';
  }

  // Update average score in the risk distribution card
  const propScore = document.getElementById('overviewPropScore');
  if (propScore && stats.totalAssessments > 0) {
    const avg = assessStats.evalue > 0
      ? Math.round(assessStats.recent.reduce((s, a) => s + (a.globalScore || 0), 0) / Math.max(assessStats.recent.length, 1))
      : stats.avgScore;
    if (avg !== null && !isNaN(avg)) {
      propScore.textContent = `${avg}%`;
    }
  }
}

/* ── Pending Submission Badge ────────────────────────── */

function updatePendingSubmissionBadge(count: number): void {
  const quickVal = document.getElementById('overviewQuickVal');
  if (quickVal) {
    quickVal.textContent = String(count);
  }
  const quickDesc = document.getElementById('overviewQuickDesc');
  if (quickDesc) {
    quickDesc.textContent = count === 1 ? '1 dossier à examiner' : `${count} dossiers à examiner`;
  }
  const quickTitle = document.getElementById('overviewQuickTitle');
  if (quickTitle) {
    quickTitle.textContent = count > 0 ? 'Soumissions en attente' : 'Aucune soumission';
  }
}

/* ── Carousel rotation for banner gallery ───────────── */

/* ── Carousel rotation for banner gallery ───────────── */

function initCarousel(): void {
  const slides = document.querySelectorAll('.banner-gallery-slide');
  if (slides.length < 2) return;
  let current = 0;
  slides.forEach((s, i) => {
    (s as HTMLElement).style.opacity = i === 0 ? '1' : '0';
    (s as HTMLElement).style.transition = 'opacity 1.5s ease-in-out';
  });
  carouselInterval = setInterval(() => {
    (slides[current] as HTMLElement).style.opacity = '0';
    current = (current + 1) % slides.length;
    (slides[current] as HTMLElement).style.opacity = '1';
  }, 5000);
}

/* ── API Banner ──────────────────────────────────────── */

function showApiBanner(): void {
  const banner = document.querySelector('.banner-section');
  if (!banner) return;

  const existing = document.getElementById('apiFallbackBanner');
  if (existing) return;

  const bannerEl = document.createElement('div');
  bannerEl.id = 'apiFallbackBanner';
  bannerEl.style.cssText = 'display:flex;align-items:center;gap:10px;padding:12px 16px;margin:8px 0 0;border-radius:8px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);font-size:13px;color:var(--text-secondary);';
  bannerEl.innerHTML = '<span class="material-symbols-outlined" style="font-size:20px;color:#f59e0b;">cloud_off</span> API du backend non disponible. Les statistiques utilisent des données locales. Lancez <code style="font-size:12px;background:var(--bg-panel);padding:2px 6px;border-radius:4px;color:var(--text-primary);">cd backend && npm run dev</code> pour activer les données temps réel.';
  banner.insertAdjacentElement('afterend', bannerEl);
}

/* ── API Banner ──────────────────────────────────────── */
