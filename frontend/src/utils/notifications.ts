/**
 * Notifications — shared toast and modal utilities.
 * Replaces all alert() / prompt() calls with styled UI components.
 */

/* ── Toast System ─────────────────────────────────────── */

let toastContainer: HTMLElement | null = null;

function ensureToastContainer(): HTMLElement {
  if (toastContainer && document.body.contains(toastContainer)) return toastContainer;
  toastContainer = document.createElement('div');
  toastContainer.id = 'previa-toast-container';
  toastContainer.style.cssText =
    'position:fixed;bottom:24px;right:24px;display:flex;flex-direction:column;gap:8px;z-index:10000;max-width:380px;';
  document.body.appendChild(toastContainer);
  return toastContainer;
}

export function showToast(
  message: string,
  type: 'success' | 'error' | 'info' | 'warning' = 'info',
  durationMs: number = 4000
): void {
  const container = ensureToastContainer();
  const toast = document.createElement('div');
  toast.style.cssText = `
    display:flex;align-items:center;gap:10px;
    padding:12px 16px;
    border-radius:8px;
    font-family:Outfit,system-ui,sans-serif;
    font-size:13px;
    font-weight:500;
    color:#fff;
    background:${type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : type === 'warning' ? '#d97706' : '#2563eb'};
    box-shadow:0 4px 12px rgba(0,0,0,0.15);
    animation:previaToastIn 0.3s ease;
    cursor:pointer;
  `;

  const icons: Record<string, string> = {
    success: 'check_circle',
    error: 'error',
    warning: 'warning',
    info: 'info',
  };

  toast.innerHTML = `
    <span class="material-symbols-outlined" style="font-size:18px!important;flex-shrink:0;">${icons[type]}</span>
    <span style="flex:1;">${message}</span>
  `;

  toast.addEventListener('click', () => removeToast(toast));
  container.appendChild(toast);

  const timeoutId = setTimeout(() => removeToast(toast), durationMs);
  toast.addEventListener('mouseenter', () => clearTimeout(timeoutId));
  toast.addEventListener('mouseleave', () => setTimeout(() => removeToast(toast), durationMs));
}

function removeToast(toast: HTMLElement): void {
  if (!toast.parentNode) return;
  toast.style.transition = 'opacity 0.3s, transform 0.3s';
  toast.style.opacity = '0';
  toast.style.transform = 'translateX(20px)';
  setTimeout(() => { if (toast.parentNode) toast.remove(); }, 300);
}

/* ── Modal System ─────────────────────────────────────── */

let modalContainer: HTMLElement | null = null;

interface ModalOptions {
  title: string;
  content: string;
  confirmLabel?: string;
  cancelLabel?: string;
  showCancel?: boolean;
  inputLabel?: string;
  inputPlaceholder?: string;
  inputValue?: string;
  variant?: 'default' | 'input' | 'confirm';
}

interface ModalResult {
  confirmed: boolean;
  value?: string;
}

export function showModal(options: ModalOptions): Promise<ModalResult> {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.id = 'previa-modal-overlay';
    overlay.style.cssText = `
      position:fixed;top:0;left:0;width:100vw;height:100vh;
      background:rgba(0,0,0,0.5);z-index:9999;
      display:flex;justify-content:center;align-items:center;
      animation:previaModalFadeIn 0.2s ease;
      font-family:Outfit,system-ui,sans-serif;
    `;

    const isInput = options.variant === 'input';

    overlay.innerHTML = `
      <div style="
        background:var(--bg-panel,#fff);border-radius:12px;
        width:${isInput ? '440px' : '400px'};max-width:90vw;
        box-shadow:0 8px 32px rgba(0,0,0,0.2);
        animation:previaModalSlideIn 0.25s ease;
        overflow:hidden;
      ">
        <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid var(--border-color,#e5e7eb);">
          <h3 style="margin:0;font-size:15px;font-weight:600;color:var(--text-primary,#1f2937);">${options.title}</h3>
          <button type="button" id="previa-modal-close" style="
            background:none;border:none;cursor:pointer;
            color:var(--text-muted,#9ca3af);padding:4px;border-radius:6px;
            display:flex;align-items:center;justify-content:center;
          "><span class="material-symbols-outlined" style="font-size:20px!important;">close</span></button>
        </div>
        <div style="padding:20px;font-size:13px;color:var(--text-secondary,#6b7280);line-height:1.5;">
          ${options.content}
          ${isInput ? `
            <div style="margin-top:12px;">
              <label style="display:block;font-size:12px;font-weight:500;color:var(--text-primary,#1f2937);margin-bottom:6px;">${options.inputLabel || 'Email'}</label>
              <input type="email" id="previa-modal-input" value="${options.inputValue || ''}" placeholder="${options.inputPlaceholder || ''}" style="
                width:100%;padding:9px 12px;border:1.5px solid var(--border-color,#e5e7eb);
                border-radius:8px;font-family:inherit;font-size:13px;
                box-sizing:border-box;outline:none;
                background:var(--bg-panel,#f9fafb);color:var(--text-primary,#1f2937);
              ">
            </div>
          ` : ''}
        </div>
        <div style="display:flex;justify-content:flex-end;gap:8px;padding:12px 20px;border-top:1px solid var(--border-color,#e5e7eb);">
          ${options.showCancel !== false ? `
            <button type="button" id="previa-modal-cancel" style="
              padding:8px 16px;border:1.5px solid var(--border-color,#e5e7eb);
              border-radius:8px;background:transparent;
              cursor:pointer;font-family:inherit;font-size:13px;
              color:var(--text-secondary,#6b7280);font-weight:500;
            ">${options.cancelLabel || 'Annuler'}</button>
          ` : ''}
          <button type="button" id="previa-modal-confirm" style="
            padding:8px 16px;border:none;border-radius:8px;
            background:var(--color-primary,#c56a3d);color:#fff;
            cursor:pointer;font-family:inherit;font-size:13px;font-weight:600;
          ">${options.confirmLabel || options.variant === 'input' ? 'Confirmer' : 'OK'}</button>
        </div>
      </div>
    `;

    document.body.appendChild(overlay);

    const closeModal = (result: ModalResult) => {
      overlay.style.transition = 'opacity 0.2s';
      overlay.style.opacity = '0';
      setTimeout(() => { if (overlay.parentNode) overlay.remove(); }, 200);
      resolve(result);
    };

    overlay.querySelector('#previa-modal-close')?.addEventListener('click', () => closeModal({ confirmed: false }));
    overlay.querySelector('#previa-modal-cancel')?.addEventListener('click', () => closeModal({ confirmed: false }));
    overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal({ confirmed: false }); });

    overlay.querySelector('#previa-modal-confirm')?.addEventListener('click', () => {
      const input = document.getElementById('previa-modal-input') as HTMLInputElement | null;
      closeModal({ confirmed: true, value: input?.value || '' });
    });

    // Focus input if present
    setTimeout(() => {
      const input = document.getElementById('previa-modal-input') as HTMLInputElement | null;
      if (input) input.focus();
    }, 100);
  });
}

// Convenience wrappers
export function showSuccess(message: string): void {
  showToast(message, 'success');
}

export function showError(message: string): void {
  showToast(message, 'error');
}

export function showInfo(message: string): void {
  showToast(message, 'info');
}

export function showWarning(message: string): void {
  showToast(message, 'warning');
}

export function showConfirm(title: string, content: string): Promise<boolean> {
  return showModal({
    title,
    content,
    variant: 'confirm',
    confirmLabel: 'Confirmer',
    cancelLabel: 'Annuler',
  }).then(r => r.confirmed);
}

export function showPrompt(options: {
  title: string;
  content: string;
  inputLabel?: string;
  inputPlaceholder?: string;
  inputValue?: string;
}): Promise<string | null> {
  return showModal({
    ...options,
    variant: 'input',
    confirmLabel: 'Confirmer',
    cancelLabel: 'Annuler',
  }).then(r => r.confirmed ? r.value || null : null);
}

// Inject animation keyframes once
(function injectStyles(): void {
  if (document.getElementById('previa-notif-styles')) return;
  const style = document.createElement('style');
  style.id = 'previa-notif-styles';
  style.textContent = `
    @keyframes previaToastIn {
      from { opacity:0; transform:translateX(20px); }
      to { opacity:1; transform:translateX(0); }
    }
    @keyframes previaModalFadeIn {
      from { opacity:0; }
      to { opacity:1; }
    }
    @keyframes previaModalSlideIn {
      from { opacity:0; transform:translateY(-10px); }
      to { opacity:1; transform:translateY(0); }
    }
  `;
  document.head.appendChild(style);
})();
