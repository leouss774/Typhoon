"""Add document upload zone to step 5 of the assured form."""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

UPLOAD_HTML = '''            </div>

            <!-- Document Upload Zone -->
            <div class="upload-zone" id="assureUploadZone" style="background:var(--bg-panel);border:2px dashed var(--border-color);border-radius:var(--border-radius-md);padding:20px 16px;display:flex;flex-direction:column;align-items:center;gap:10px;cursor:pointer;transition:all 0.2s ease;text-align:center;">
              <span class="material-symbols-outlined" style="font-size:32px!important;color:var(--color-primary);opacity:0.5;">cloud_upload</span>
              <div>
                <div style="font-size:13px;font-weight:500;color:var(--text-primary);">Ajouter des documents</div>
                <div style="font-size:11px;color:var(--text-muted);">Photos, plans, diagnostics, PDFs — glissez-déposez ou cliquez</div>
              </div>
              <input type="file" id="assureFileInput" multiple accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.dwg,.dxf,.doc,.docx" style="display:none;">
              <button type="button" class="assure-upload-btn" style="padding:6px 16px;border:1.5px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);font-family:var(--font-primary);font-size:12px;cursor:pointer;transition:all 0.15s ease;display:flex;align-items:center;gap:6px;">
                <span class="material-symbols-outlined" style="font-size:16px!important;">add_photo_alternate</span> Sélectionner des fichiers
              </button>
              <div style="font-size:10px;color:var(--text-muted);">Formats acceptés : JPG, PNG, PDF, DWG, DOC — Max 20 Mo par fichier</div>
            </div>

            <!-- Upload Preview List -->
            <div id="assureUploadList" style="display:none;flex-direction:column;gap:6px;padding:4px 0;"></div>

            <div style="display:flex;justify-content:space-between;gap:8px;padding-top:8px;">'''

# Find the insertion point: the current buttons div start after summary section
old_marker = '''            </div>

            <div style=\"display:flex;justify-content:space-between;gap:8px;padding-top:8px;\">
              <button type=\"button\" class=\"assure-btn-back\"'''

if old_marker in content:
    content = content.replace(old_marker, UPLOAD_HTML, 1)
    print('✅ Upload zone added to step 5')
else:
    print('⚠️  Marker not found, trying alternative...')
    # Try to find any buttons div in step 5 area
    alt_marker = '''            <div style=\"display:flex;justify-content:space-between;gap:8px;padding-top:8px;\">
              <button type=\"button\" class=\"assure-btn-back\"'''
    if alt_marker in content:
        content = content.replace(alt_marker, UPLOAD_HTML, 1)
        print('✅ Upload zone added (alt marker)')
    else:
        print('❌ Insertion point not found')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Add CSS
with open('src/views/assure/assure.css', 'a', encoding='utf-8') as f:
    f.write("""
/* ── Upload zone ────────────────────────────────────────────── */
.upload-zone.dragover {
  border-color: var(--color-primary) !important;
  background: rgba(197,106,61,0.04) !important;
  transform: scale(1.01);
}

.upload-zone.has-files {
  border-color: #10b981 !important;
  background: rgba(16,185,129,0.04) !important;
}

.assure-upload-btn:hover {
  border-color: var(--color-primary) !important;
  color: var(--color-primary) !important;
  background: rgba(197,106,61,0.04) !important;
}

/* Upload item list */
.upload-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  animation: uploadItemIn 0.25s ease;
}

@keyframes uploadItemIn {
  from { opacity: 0; transform: translateY(-8px); }
  to { opacity: 1; transform: translateY(0); }
}

.upload-item-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: rgba(197,106,61,0.08);
  color: var(--color-primary);
  overflow: hidden;
}

.upload-item-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-item-icon .material-symbols-outlined {
  font-size: 18px !important;
}

.upload-item-info {
  flex: 1;
  min-width: 0;
}

.upload-item-name {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.upload-item-size {
  font-size: 10px;
  color: var(--text-muted);
}

.upload-item-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.upload-item-remove:hover {
  background: rgba(239,68,68,0.1);
  color: #ef4444;
}

.upload-item-remove .material-symbols-outlined {
  font-size: 14px !important;
}
""")

print('✅ Upload CSS added')
