"""Add a recap summary section to step 5 of the assured form wizard."""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── The summary HTML to inject between fields and buttons ────

SUMMARY_HTML = '''            </div>

            <!-- Recap Summary -->
            <div id="assureFormSummary" style="background:var(--bg-panel);border-radius:var(--border-radius-md);border:1px solid var(--border-color);padding:14px 16px;display:flex;flex-direction:column;gap:12px;">
              <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);display:flex;align-items:center;gap:6px;margin:0;">
                <span class="material-symbols-outlined" style="font-size:16px!important;color:var(--color-primary);">checklist</span>
                Récapitulatif de votre bien
              </h4>

              <!-- Section 1: Localisation -->
              <div class="summary-section">
                <div class="summary-section-title">Localisation &amp; Type de bien</div>
                <div class="summary-grid">
                  <div class="summary-item"><span class="summary-label">Adresse</span><span class="summary-value" id="summaryAddress">—</span></div>
                  <div class="summary-item"><span class="summary-label">Code postal</span><span class="summary-value" id="summaryPostalCode">—</span></div>
                  <div class="summary-item"><span class="summary-label">Ville</span><span class="summary-value" id="summaryCity">—</span></div>
                  <div class="summary-item"><span class="summary-label">Type de bien</span><span class="summary-value" id="summaryTypeBien">—</span></div>
                  <div class="summary-item"><span class="summary-label">Surface</span><span class="summary-value" id="summarySurface">—</span></div>
                  <div class="summary-item"><span class="summary-label">Pièces</span><span class="summary-value" id="summaryPieces">—</span></div>
                  <div class="summary-item"><span class="summary-label">Étages</span><span class="summary-value" id="summaryEtages">—</span></div>
                </div>
              </div>

              <!-- Section 2: Structure -->
              <div class="summary-section">
                <div class="summary-section-title">Structure &amp; Construction</div>
                <div class="summary-grid">
                  <div class="summary-item"><span class="summary-label">Année construction</span><span class="summary-value" id="summaryAnneeConst">—</span></div>
                  <div class="summary-item"><span class="summary-label">Année rénovation</span><span class="summary-value" id="summaryAnneeRenov">—</span></div>
                  <div class="summary-item"><span class="summary-label">Type structure</span><span class="summary-value" id="summaryStructure">—</span></div>
                  <div class="summary-item"><span class="summary-label">État structure</span><span class="summary-value" id="summaryEtatStructure">—</span></div>
                  <div class="summary-item"><span class="summary-label">Fissures</span><span class="summary-value" id="summaryFissures">—</span></div>
                  <div class="summary-item"><span class="summary-label">Affaissement</span><span class="summary-value" id="summaryAffaissement">—</span></div>
                  <div class="summary-item"><span class="summary-label">Fondations</span><span class="summary-value" id="summaryFondations">—</span></div>
                  <div class="summary-item"><span class="summary-label">Hauteur plancher</span><span class="summary-value" id="summaryHauteur">—</span></div>
                </div>
              </div>

              <!-- Section 3: Toiture & Isolation -->
              <div class="summary-section">
                <div class="summary-section-title">Toiture &amp; Isolation</div>
                <div class="summary-grid">
                  <div class="summary-item"><span class="summary-label">Type toiture</span><span class="summary-value" id="summaryTypeToiture">—</span></div>
                  <div class="summary-item"><span class="summary-label">Matériau</span><span class="summary-value" id="summaryMateriauToit">—</span></div>
                  <div class="summary-item"><span class="summary-label">Âge toiture</span><span class="summary-value" id="summaryAgeToiture">—</span></div>
                  <div class="summary-item"><span class="summary-label">Année toiture</span><span class="summary-value" id="summaryAnneeToiture">—</span></div>
                  <div class="summary-item"><span class="summary-label">État toiture</span><span class="summary-value" id="summaryEtatToiture">—</span></div>
                  <div class="summary-item"><span class="summary-label">Isolation toiture</span><span class="summary-value" id="summaryIsolToiture">—</span></div>
                  <div class="summary-item"><span class="summary-label">Isolation murs</span><span class="summary-value" id="summaryIsolMurs">—</span></div>
                  <div class="summary-item"><span class="summary-label">Isolation sol</span><span class="summary-value" id="summaryIsolSol">—</span></div>
                  <div class="summary-item"><span class="summary-label">Panneaux solaires</span><span class="summary-value" id="summaryPanneaux">—</span></div>
                </div>
              </div>

              <!-- Section 4: Équipements -->
              <div class="summary-section">
                <div class="summary-section-title">Équipements &amp; Conformité</div>
                <div class="summary-grid">
                  <div class="summary-item"><span class="summary-label">Chauffage</span><span class="summary-value" id="summaryChauffage">—</span></div>
                  <div class="summary-item"><span class="summary-label">Installation électrique</span><span class="summary-value" id="summaryElectrique">—</span></div>
                  <div class="summary-item"><span class="summary-label">Climatisation</span><span class="summary-value" id="summaryClim">—</span></div>
                  <div class="summary-item"><span class="summary-label">Détecteurs fumée</span><span class="summary-value" id="summaryDetecteurs">—</span></div>
                  <div class="summary-item"><span class="summary-label">Occupation</span><span class="summary-value" id="summaryOccupation">—</span></div>
                  <div class="summary-item"><span class="summary-label">Infiltrations</span><span class="summary-value" id="summaryInfiltrations">—</span></div>
                  <div class="summary-item"><span class="summary-label">Sous-sol</span><span class="summary-value" id="summarySousSol">—</span></div>
                  <div class="summary-item"><span class="summary-label">Cave</span><span class="summary-value" id="summaryCave">—</span></div>
                  <div class="summary-item"><span class="summary-label">Garage</span><span class="summary-value" id="summaryGarage">—</span></div>
                  <div class="summary-item"><span class="summary-label">Arbres proches</span><span class="summary-value" id="summaryArbres">—</span></div>
                </div>
              </div>

              <!-- Section 5: Finalisation -->
              <div class="summary-section">
                <div class="summary-section-title">DPE &amp; Finalisation</div>
                <div class="summary-grid">
                  <div class="summary-item"><span class="summary-label">Classe DPE</span><span class="summary-value" id="summaryDpe">—</span></div>
                  <div class="summary-item"><span class="summary-label">Exposition</span><span class="summary-value" id="summaryExposition">—</span></div>
                  <div class="summary-item"><span class="summary-label">Mitoyenneté</span><span class="summary-value" id="summaryMitoyennete">—</span></div>
                  <div class="summary-item"><span class="summary-label">Capital assuré</span><span class="summary-value" id="summaryCapital">—</span></div>
                </div>
              </div>
            </div>

            <div style="display:flex;justify-content:space-between;gap:8px;padding-top:8px;">'''

# ── Find and replace ────────────────────────────────────────────

# Find step 5 panel
old_marker = '''              <div class=\"afi-field\" style=\"grid-column:1/-1;\">
                <label class=\"afi-label\">Observations</label>
                <textarea class=\"afi-textarea\" id=\"afi_observations\" rows=\"3\" placeholder=\"Autres informations pertinentes concernant le bien...\"></textarea>
              </div>
            </div>
            <div style=\"display:flex;justify-content:space-between;gap:8px;margin-top:auto;padding-top:8px;\">'''

if old_marker in content:
    content = content.replace(old_marker, SUMMARY_HTML)
    print('✅ Summary section added to step 5')
else:
    print('⚠️  Could not find exact marker, trying alt...')
    # Try without the margin-top:auto
    alt_marker = '''              <div class=\"afi-field\" style=\"grid-column:1/-1;\">
                <label class=\"afi-label\">Observations</label>
                <textarea class=\"afi-textarea\" id=\"afi_observations\" rows=\"3\" placeholder=\"Autres informations pertinentes concernant le bien...\"></textarea>
              </div>
            </div>
            <div style=\"display:flex;justify-content:space-between;gap:8px;padding-top:8px;\">'''
    if alt_marker in content:
        content = content.replace(alt_marker, SUMMARY_HTML)
        print('✅ Summary section added to step 5 (alt marker)')
    else:
        print('❌ Could not find insertion point')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# ── Add summary CSS to assure.css ─────────────────────────────

with open('src/views/assure/assure.css', 'a', encoding='utf-8') as f:
    f.write("""
/* ── Form recap summary ────────────────────────────────────── */
.summary-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.summary-section + .summary-section {
  padding-top: 10px;
  border-top: 1px solid var(--border-color);
}

.summary-section-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.4px;
  margin-bottom: 2px;
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px 16px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  border-bottom: 1px dashed var(--border-color);
  font-size: 12px;
}

.summary-label {
  color: var(--text-muted);
  font-weight: 500;
}

.summary-value {
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
}
""")

print('✅ Summary CSS added to assure.css')
