"""Rebuild view-assure-bien panel with:
- Complete 5-step form (30+ afi_* fields)
- Form/Dashboard mode toggle
- Dashboard view (risk gauges, stats, property info)
- Signature modal
"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── The complete view-assure-bien panel ──────────────────────────

NEW_PANEL = '''    <!-- ====== VIEW: Assuré — Bien ====== -->
    <section class="view-panel" id="view-assure-bien">
      <!-- Mode Selector (hidden until form is completed) -->
      <div class="assure-mode-selector" id="assureModeSelector" style="display:none;align-items:center;gap:8px;padding:8px 0;">
        <button class="assure-mode-btn active" id="assureModeDashBtn">
          <span class="material-symbols-outlined">dashboard</span> Tableau de bord
        </button>
        <button class="assure-mode-btn" id="assureModeFormBtn">
          <span class="material-symbols-outlined">edit</span> Modifier mon bien
        </button>
      </div>

      <!-- ====== FORM VIEW ====== -->
      <div id="assureFormView" style="display:flex;flex-direction:column;gap:12px;flex:1;min-height:0;">
        <!-- Steps indicator -->
        <div class="afs-steps" style="display:flex;gap:4px;padding:4px 0;flex-shrink:0;">
          <div class="afs-step active" data-step="1"><span class="afs-step-num">1</span><span class="afs-step-label">Adresse</span></div>
          <div class="afs-step" data-step="2"><span class="afs-step-num">2</span><span class="afs-step-label">Structure</span></div>
          <div class="afs-step" data-step="3"><span class="afs-step-num">3</span><span class="afs-step-label">Toiture</span></div>
          <div class="afs-step" data-step="4"><span class="afs-step-num">4</span><span class="afs-step-label">Équipements</span></div>
          <div class="afs-step" data-step="5"><span class="afs-step-num">5</span><span class="afs-step-label">Finalisation</span></div>
        </div>

        <form id="assurePropertyForm" style="display:flex;flex-direction:column;gap:12px;flex:1;min-height:0;">
          <!-- STEP 1: Adresse & Type de bien -->
          <div class="afs-panel active" data-step="1" style="display:flex;flex-direction:column;gap:10px;flex:1;">
            <div class="afs-panel-header">
              <h3>Localisation & Type de bien</h3>
              <p>Adresse, type de propriété et caractéristiques principales</p>
            </div>
            <div class="afs-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div class="afi-field" style="grid-column:1/-1;">
                <label class="afi-label">Adresse du bien</label>
                <input type="text" class="afi-input" id="afi_address" placeholder="Numéro et nom de voie" required>
              </div>
              <div class="afi-field">
                <label class="afi-label">Code postal</label>
                <input type="text" class="afi-input" id="afi_postalCode" placeholder="75002" maxlength="5" required>
              </div>
              <div class="afi-field">
                <label class="afi-label">Ville</label>
                <input type="text" class="afi-input" id="afi_city" placeholder="Paris" required>
              </div>
              <div class="afi-field">
                <label class="afi-label">Type de bien</label>
                <select class="afi-select" id="afi_typeBien">
                  <option value="">Sélectionnez...</option>
                  <option value="maison">Maison individuelle</option>
                  <option value="appartement">Appartement</option>
                  <option value="immeuble">Immeuble</option>
                  <option value="local_commercial">Local commercial</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Surface (m²)</label>
                <input type="number" class="afi-input" id="afi_surface" placeholder="120" min="1">
              </div>
              <div class="afi-field">
                <label class="afi-label">Nombre de pièces</label>
                <input type="number" class="afi-input" id="afi_nbPieces" placeholder="5" min="1">
              </div>
              <div class="afi-field">
                <label class="afi-label">Nombre d'étages</label>
                <input type="number" class="afi-input" id="afi_nbEtages" placeholder="2" min="0">
              </div>
            </div>
            <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:auto;padding-top:8px;">
              <button type="button" class="assure-btn-next" data-next="2" style="padding:8px 24px;border:none;border-radius:6px;background:var(--color-primary);color:#fff;font-family:var(--font-primary);font-size:13px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:6px;">
                Suivant <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_forward</span>
              </button>
            </div>
          </div>

          <!-- STEP 2: Structure & Construction -->
          <div class="afs-panel" data-step="2" style="display:none;flex-direction:column;gap:10px;flex:1;">
            <div class="afs-panel-header">
              <h3>Structure & Construction</h3>
              <p>Année de construction, état général et caractéristiques structurelles</p>
            </div>
            <div class="afs-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div class="afi-field">
                <label class="afi-label">Année de construction</label>
                <input type="number" class="afi-input" id="afi_anneeConstruction" placeholder="1985" min="1800" max="2026">
              </div>
              <div class="afi-field">
                <label class="afi-label">Année de rénovation</label>
                <input type="number" class="afi-input" id="afi_anneeRenovation" placeholder="2015" min="1800" max="2026">
              </div>
              <div class="afi-field">
                <label class="afi-label">Type de structure</label>
                <select class="afi-select" id="afi_typeStructure">
                  <option value="">Sélectionnez...</option>
                  <option value="beton">Béton armé</option>
                  <option value="bois">Bois</option>
                  <option value="acier">Acier</option>
                  <option value="pierre">Pierre / Maçonnerie</option>
                  <option value="mixte">Mixte</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">État de la structure</label>
                <select class="afi-select" id="afi_etatStructure">
                  <option value="">Sélectionnez...</option>
                  <option value="neuf">Neuf</option>
                  <option value="bon">Bon état</option>
                  <option value="moyen">État moyen</option>
                  <option value="vétuste">Vétuste</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Fissures apparentes</label>
                <select class="afi-select" id="afi_fissures">
                  <option value="">Sélectionnez...</option>
                  <option value="aucune">Aucune</option>
                  <option value="fines">Fines (≤ 2mm)</option>
                  <option value="moyennes">Moyennes (2-5mm)</option>
                  <option value="larges">Larges (> 5mm)</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Affaissement</label>
                <select class="afi-select" id="afi_affaissement">
                  <option value="">Sélectionnez...</option>
                  <option value="aucun">Aucun</option>
                  <option value="leger">Léger</option>
                  <option value="significatif">Significatif</option>
                  <option value="critique">Critique</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Profondeur des fondations</label>
                <select class="afi-select" id="afi_profondeurFondations">
                  <option value="">Sélectionnez...</option>
                  <option value="superficielles">Superficielles (< 1m)</option>
                  <option value="semi">Semi-profondes (1-3m)</option>
                  <option value="profondes">Profondes (> 3m)</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Hauteur sous plancher (m)</label>
                <input type="number" class="afi-input" id="afi_hauteurPlancher" placeholder="2.5" min="1" step="0.1">
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;gap:8px;margin-top:auto;padding-top:8px;">
              <button type="button" class="assure-btn-back" style="padding:8px 24px;border:1.5px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);font-family:var(--font-primary);font-size:13px;cursor:pointer;display:flex;align-items:center;gap:6px;" data-prev="1">
                <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Précédent
              </button>
              <button type="button" class="assure-btn-next" data-next="3" style="padding:8px 24px;border:none;border-radius:6px;background:var(--color-primary);color:#fff;font-family:var(--font-primary);font-size:13px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:6px;">
                Suivant <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_forward</span>
              </button>
            </div>
          </div>

          <!-- STEP 3: Toiture & Isolation -->
          <div class="afs-panel" data-step="3" style="display:none;flex-direction:column;gap:10px;flex:1;">
            <div class="afs-panel-header">
              <h3>Toiture & Isolation</h3>
              <p>Caractéristiques de la toiture et niveaux d'isolation</p>
            </div>
            <div class="afs-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div class="afi-field">
                <label class="afi-label">Type de toiture</label>
                <select class="afi-select" id="afi_typeToiture">
                  <option value="">Sélectionnez...</option>
                  <option value="tuiles">Tuiles</option>
                  <option value="ardoises">Ardoises</option>
                  <option value="toit_plat">Toit plat</option>
                  <option value="metal">Bac acier / Métal</option>
                  <option value="chaume">Chaume</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Matériau du toit</label>
                <select class="afi-select" id="afi_materiauToit">
                  <option value="">Sélectionnez...</option>
                  <option value="terre_cuite">Terre cuite</option>
                  <option value="beton">Béton</option>
                  <option value="acier">Acier</option>
                  <option value="zinc">Zinc</option>
                  <option value="bois">Bois</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Âge de la toiture (ans)</label>
                <input type="number" class="afi-input" id="afi_ageToiture" placeholder="15" min="0">
              </div>
              <div class="afi-field">
                <label class="afi-label">Année de la toiture</label>
                <input type="number" class="afi-input" id="afi_anneeToiture" placeholder="2010" min="1900" max="2026">
              </div>
              <div class="afi-field">
                <label class="afi-label">État de la toiture</label>
                <select class="afi-select" id="afi_etatToiture">
                  <option value="">Sélectionnez...</option>
                  <option value="excellent">Excellent</option>
                  <option value="bon">Bon</option>
                  <option value="moyen">Moyen</option>
                  <option value="mauvais">Mauvais</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Isolation de la toiture</label>
                <select class="afi-select" id="afi_isolationToiture">
                  <option value="">Sélectionnez...</option>
                  <option value="excellente">Excellente</option>
                  <option value="bonne">Bonne</option>
                  <option value="moyenne">Moyenne</option>
                  <option value="insuffisante">Insuffisante</option>
                  <option value="aucune">Aucune</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Isolation des murs</label>
                <select class="afi-select" id="afi_isolationMurs">
                  <option value="">Sélectionnez...</option>
                  <option value="excellente">Excellente</option>
                  <option value="bonne">Bonne</option>
                  <option value="moyenne">Moyenne</option>
                  <option value="insuffisante">Insuffisante</option>
                  <option value="aucune">Aucune</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Isolation du sol</label>
                <select class="afi-select" id="afi_isolationSol">
                  <option value="">Sélectionnez...</option>
                  <option value="excellente">Excellente</option>
                  <option value="bonne">Bonne</option>
                  <option value="moyenne">Moyenne</option>
                  <option value="insuffisante">Insuffisante</option>
                  <option value="aucune">Aucune</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Panneaux solaires</label>
                <label class="afi-check-label" style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                  <input type="checkbox" id="afi_panneauxSolaires"> Présence de panneaux solaires
                </label>
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;gap:8px;margin-top:auto;padding-top:8px;">
              <button type="button" class="assure-btn-back" style="padding:8px 24px;border:1.5px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);font-family:var(--font-primary);font-size:13px;cursor:pointer;display:flex;align-items:center;gap:6px;" data-prev="2">
                <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Précédent
              </button>
              <button type="button" class="assure-btn-next" data-next="4" style="padding:8px 24px;border:none;border-radius:6px;background:var(--color-primary);color:#fff;font-family:var(--font-primary);font-size:13px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:6px;">
                Suivant <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_forward</span>
              </button>
            </div>
          </div>

          <!-- STEP 4: Équipements & Conformité -->
          <div class="afs-panel" data-step="4" style="display:none;flex-direction:column;gap:10px;flex:1;">
            <div class="afs-panel-header">
              <h3>Équipements & Conformité</h3>
              <p>Chauffage, électricité, sous-sols et équipements de sécurité</p>
            </div>
            <div class="afs-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div class="afi-field">
                <label class="afi-label">Chauffage principal</label>
                <select class="afi-select" id="afi_chauffagePrincipal">
                  <option value="">Sélectionnez...</option>
                  <option value="gaz">Gaz</option>
                  <option value="electrique">Électrique</option>
                  <option value="fioul">Fioul</option>
                  <option value="bois">Bois / Granulés</option>
                  <option value="pompe_chaleur">Pompe à chaleur</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Installation électrique (année)</label>
                <input type="number" class="afi-input" id="afi_installationElectriqueAnnee" placeholder="2005" min="1950" max="2026">
              </div>
              <div class="afi-field">
                <label class="afi-label">Climatisation</label>
                <label class="afi-check-label" style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                  <input type="checkbox" id="afi_climatisation"> Présence de climatisation
                </label>
              </div>
              <div class="afi-field">
                <label class="afi-label">Détecteurs de fumée</label>
                <label class="afi-check-label" style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                  <input type="checkbox" id="afi_presenceDetecteursFumee"> Détecteurs installés
                </label>
              </div>
              <div class="afi-field">
                <label class="afi-label">Occupation du bien</label>
                <select class="afi-select" id="afi_occupation">
                  <option value="">Sélectionnez...</option>
                  <option value="proprietaire">Propriétaire occupant</option>
                  <option value="locataire">Locataire</option>
                  <option value="vide">Logement vacant</option>
                  <option value="secondaire">Résidence secondaire</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Infiltrations d'eau</label>
                <select class="afi-select" id="afi_infiltrations">
                  <option value="">Sélectionnez...</option>
                  <option value="aucune">Aucune</option>
                  <option value="occasionnelles">Occasionnelles</option>
                  <option value="frequentes">Fréquentes</option>
                  <option value="permanentes">Permanentes</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label" style="display:block;margin-bottom:4px;">Sous-sol / Cave / Garage</label>
                <div style="display:flex;flex-wrap:wrap;gap:12px;">
                  <label class="afi-check-label" style="display:flex;align-items:center;gap:6px;">
                    <input type="checkbox" id="afi_presenceSousSol"> Sous-sol
                  </label>
                  <label class="afi-check-label" style="display:flex;align-items:center;gap:6px;">
                    <input type="checkbox" id="afi_presenceCave"> Cave
                  </label>
                  <label class="afi-check-label" style="display:flex;align-items:center;gap:6px;">
                    <input type="checkbox" id="afi_presenceGarage"> Garage
                  </label>
                </div>
              </div>
              <div class="afi-field">
                <label class="afi-label">Clapet anti-retour</label>
                <label class="afi-check-label" style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                  <input type="checkbox" id="afi_clapetAntiRetour"> Installé
                </label>
              </div>
              <div class="afi-field">
                <label class="afi-label">Équipements électriques sous-sol</label>
                <label class="afi-check-label" style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                  <input type="checkbox" id="afi_equipementsElecSousSol"> Présents
                </label>
              </div>
              <div class="afi-field">
                <label class="afi-label">Arbres à proximité</label>
                <label class="afi-check-label" style="display:flex;align-items:center;gap:8px;margin-top:4px;">
                  <input type="checkbox" id="afi_arbresProches"> Arbres proches du bâtiment
                </label>
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;gap:8px;margin-top:auto;padding-top:8px;">
              <button type="button" class="assure-btn-back" style="padding:8px 24px;border:1.5px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);font-family:var(--font-primary);font-size:13px;cursor:pointer;display:flex;align-items:center;gap:6px;" data-prev="3">
                <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Précédent
              </button>
              <button type="button" class="assure-btn-next" data-next="5" style="padding:8px 24px;border:none;border-radius:6px;background:var(--color-primary);color:#fff;font-family:var(--font-primary);font-size:13px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:6px;">
                Suivant <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_forward</span>
              </button>
            </div>
          </div>

          <!-- STEP 5: Finalisation -->
          <div class="afs-panel" data-step="5" style="display:none;flex-direction:column;gap:10px;flex:1;">
            <div class="afs-panel-header">
              <h3>Finalisation</h3>
              <p>DPE, observations et montant assuré</p>
            </div>
            <div class="afs-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div class="afi-field">
                <label class="afi-label">Classe DPE</label>
                <select class="afi-select" id="afi_dpeClass">
                  <option value="">Sélectionnez...</option>
                  <option value="A">A — Très économe</option>
                  <option value="B">B — Économe</option>
                  <option value="C">C — Assez économe</option>
                  <option value="D">D — Moyen</option>
                  <option value="E">E — Assez énergivore</option>
                  <option value="F">F — Énergivore</option>
                  <option value="G">G — Très énergivore</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Exposition solaire</label>
                <select class="afi-select" id="afi_expositionSolaire">
                  <option value="">Sélectionnez...</option>
                  <option value="plein_sud">Plein sud</option>
                  <option value="sud_est">Sud-est</option>
                  <option value="sud_ouest">Sud-ouest</option>
                  <option value="nord">Nord</option>
                  <option value="mixte">Mixte</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Zone de mitoyenneté</label>
                <select class="afi-select" id="afi_zoneMitoyennete">
                  <option value="">Sélectionnez...</option>
                  <option value="isole">Isolé</option>
                  <option value="mitoyen_un">Mitoyen d'un côté</option>
                  <option value="mitoyen_deux">Mitoyen des deux côtés</option>
                  <option value="mitoyen">En bande</option>
                </select>
              </div>
              <div class="afi-field">
                <label class="afi-label">Capital assuré (€)</label>
                <input type="number" class="afi-input" id="afi_capitalAssure" placeholder="250000" min="0" step="1000">
              </div>
              <div class="afi-field" style="grid-column:1/-1;">
                <label class="afi-label">Observations</label>
                <textarea class="afi-textarea" id="afi_observations" rows="3" placeholder="Autres informations pertinentes concernant le bien..."></textarea>
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;gap:8px;margin-top:auto;padding-top:8px;">
              <button type="button" class="assure-btn-back" style="padding:8px 24px;border:1.5px solid var(--border-color);border-radius:6px;background:transparent;color:var(--text-secondary);font-family:var(--font-primary);font-size:13px;cursor:pointer;display:flex;align-items:center;gap:6px;" data-prev="4">
                <span class="material-symbols-outlined" style="font-size:16px!important;">arrow_back</span> Précédent
              </button>
              <button type="submit" class="assure-btn-submit" id="assureFormSubmitBtn" style="padding:8px 24px;border:none;border-radius:6px;background:#10b981;color:#fff;font-family:var(--font-primary);font-size:13px;font-weight:500;cursor:pointer;display:flex;align-items:center;gap:6px;">
                <span class="material-symbols-outlined" style="font-size:16px!important;">save</span> Enregistrer mon bien
              </button>
            </div>
          </div>
        </form>
      </div>

      <!-- ====== DASHBOARD VIEW ====== -->
      <div id="assureDashView" style="display:none;flex-direction:column;gap:12px;flex:1;min-height:0;">
        <!-- Welcome Banner -->
        <div class="assure-banner" style="background:linear-gradient(135deg,#1e1b4b,#312e81);border-radius:var(--border-radius-md);padding:20px 24px;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;">
          <div>
            <div class="assure-welcome">Espace Assuré</div>
            <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
              <span style="font-size:18px;font-weight:600;color:#fff;" id="assureBannerName">—</span>
              <span class="assure-engagement-status pending" id="assureBannerPolicyTag" style="font-size:10px;">...</span>
            </div>
            <div class="assure-banner-address" id="assureBannerAddress" style="color:rgba(255,255,255,0.7);font-size:13px;">—</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:32px;font-weight:300;color:#fff;" id="assureBannerScore">—</div>
            <div style="font-size:12px;color:rgba(255,255,255,0.6);" id="assureBannerRisk">—</div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="assure-stats-row" style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;">
          <div class="assure-stat-card">
            <span class="assure-stat-label">Score Risque</span>
            <span class="assure-stat-value" id="assureStatScore">—</span>
          </div>
          <div class="assure-stat-card">
            <span class="assure-stat-label">Économies/an</span>
            <span class="assure-stat-value" id="assureStatSavings">—</span>
            <span class="assure-stat-sub">Après travaux</span>
          </div>
          <div class="assure-stat-card">
            <span class="assure-stat-label">Engagement</span>
            <span class="assure-stat-value" style="font-size:14px;font-weight:400;" id="assureStatEngagement">—</span>
          </div>
        </div>

        <!-- Main content: Property info + Risk gauges -->
        <div style="display:flex;gap:12px;flex:1;min-height:0;">
          <!-- Property info card -->
          <div style="flex:1;background:var(--bg-card);border-radius:var(--border-radius-md);border:1px solid var(--border-color);padding:16px;display:flex;flex-direction:column;gap:10px;">
            <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);display:flex;align-items:center;gap:6px;">
              <span class="material-symbols-outlined" style="font-size:16px!important;color:var(--color-primary);">home</span> Mon Bien
            </h4>
            <div class="assure-prop-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
              <div class="assure-prop-item">
                <span class="assure-prop-label">Adresse</span>
                <span class="assure-prop-value" id="assurePropAddress">—</span>
              </div>
              <div class="assure-prop-item">
                <span class="assure-prop-label">Ville</span>
                <span class="assure-prop-value" id="assurePropCity">—</span>
              </div>
              <div class="assure-prop-item">
                <span class="assure-prop-label">Classe DPE</span>
                <span class="assure-prop-value" id="assurePropDpe">—</span>
              </div>
              <div class="assure-prop-item">
                <span class="assure-prop-label">Construction</span>
                <span class="assure-prop-value" id="assurePropYear">—</span>
              </div>
              <div class="assure-prop-item">
                <span class="assure-prop-label">Risque</span>
                <span class="assure-prop-value" id="assurePropRisk">—</span>
              </div>
              <div class="assure-prop-item">
                <span class="assure-prop-label">Score</span>
                <span class="assure-prop-value" id="assurePropScore">—</span>
              </div>
            </div>
            <div style="margin-top:auto;display:flex;gap:8px;padding-top:8px;border-top:1px solid var(--border-color);">
              <a id="assurePropRiskLink" style="display:none;align-items:center;gap:6px;padding:6px 12px;border-radius:6px;background:rgba(197,106,61,0.1);color:var(--color-primary);font-size:12px;font-weight:500;text-decoration:none;cursor:pointer;">
                <span class="material-symbols-outlined" style="font-size:14px!important;">open_in_new</span> Voir l'analyse risque
              </a>
            </div>
          </div>

          <!-- Risk gauges -->
          <div style="width:300px;flex-shrink:0;background:var(--bg-card);border-radius:var(--border-radius-md);border:1px solid var(--border-color);padding:16px;display:flex;flex-direction:column;gap:10px;">
            <h4 style="font-size:13px;font-weight:600;color:var(--text-primary);display:flex;align-items:center;gap:6px;">
              <span class="material-symbols-outlined" style="font-size:16px!important;color:var(--color-primary);">analytics</span> Risques Géorisques
            </h4>
            <svg viewBox="0 0 100 50" style="width:100%;height:60px;">
              <defs>
                <linearGradient id="chart-grad-bien" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stop-color="#10b981"/>
                  <stop offset="40%" stop-color="#f59e0b"/>
                  <stop offset="75%" stop-color="#ef4444"/>
                </linearGradient>
              </defs>
              <path d="M10,45 Q20,10 50,10 Q80,10 90,45" fill="none" stroke="url(#chart-grad-bien)" stroke-width="2" opacity="0.4"/>
            </svg>
            <div style="display:flex;flex-direction:column;gap:8px;">
              <div class="assure-gauge-row" style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:11px;color:var(--text-muted);width:70px;">Inondation</span>
                <div class="assure-gauge-mini" style="flex:1;height:6px;background:var(--border-color);border-radius:3px;position:relative;overflow:hidden;">
                  <div class="assure-gauge-fill" style="height:100%;border-radius:3px;transition:width 0.8s ease;width:30%;" id="assurGaugeBienFlood"></div>
                </div>
                <span style="font-size:12px;font-weight:600;min-width:30px;text-align:right;" id="assurGaugeBienFloodVal">—</span>
              </div>
              <div class="assure-gauge-row" style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:11px;color:var(--text-muted);width:70px;">RGA (Argile)</span>
                <div class="assure-gauge-mini" style="flex:1;height:6px;background:var(--border-color);border-radius:3px;position:relative;overflow:hidden;">
                  <div class="assure-gauge-fill" style="height:100%;border-radius:3px;transition:width 0.8s ease;width:50%;" id="assurGaugeBienClay"></div>
                </div>
                <span style="font-size:12px;font-weight:600;min-width:30px;text-align:right;" id="assurGaugeBienClayVal">—</span>
              </div>
              <div class="assure-gauge-row" style="display:flex;align-items:center;gap:8px;">
                <span style="font-size:11px;color:var(--text-muted);width:70px;">Séisme</span>
                <div class="assure-gauge-mini" style="flex:1;height:6px;background:var(--border-color);border-radius:3px;position:relative;overflow:hidden;">
                  <div class="assure-gauge-fill" style="height:100%;border-radius:3px;transition:width 0.8s ease;width:10%;" id="assurGaugeBienSeismic"></div>
                </div>
                <span style="font-size:12px;font-weight:600;min-width:30px;text-align:right;" id="assurGaugeBienSeismicVal">—</span>
              </div>
            </div>
            <div style="margin-top:auto;display:flex;align-items:center;gap:6px;padding-top:8px;border-top:1px solid var(--border-color);">
              <span class="material-symbols-outlined" style="font-size:14px!important;color:#10b981;">trending_up</span>
              <span style="font-size:11px;color:var(--text-secondary);">Amélioration estimée : </span>
              <span style="font-size:13px;font-weight:600;" id="assureBienImprove">—</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ====== SIGNATURE MODAL ====== -->
      <div class="assure-modal-overlay" id="assureSignModal" style="display:none;position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.5);z-index:500;justify-content:center;align-items:center;">
        <div class="assure-modal" style="background:var(--bg-panel);border-radius:var(--border-radius-lg);width:480px;max-width:90vw;max-height:85vh;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:14px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <h3 style="font-size:16px;font-weight:600;color:var(--text-primary);display:flex;align-items:center;gap:6px;">
              <span class="material-symbols-outlined" style="color:var(--color-primary);">how_to_reg</span> Signer l'engagement
            </h3>
            <button type="button" id="assureSignModalClose" style="background:none;border:none;color:var(--text-muted);cursor:pointer;padding:4px;">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>

          <div style="background:var(--bg-card);border-radius:var(--border-radius-sm);padding:12px 14px;display:flex;flex-direction:column;gap:6px;">
            <div class="assure-policy-row" style="display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid var(--border-color);">
              <span style="color:var(--text-muted);">Référence police</span>
              <span style="font-weight:500;" id="assureModalPolRef">—</span>
            </div>
            <div class="assure-policy-row" style="display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid var(--border-color);">
              <span style="color:var(--text-muted);">Assuré</span>
              <span style="font-weight:500;" id="assureModalClient">—</span>
            </div>
            <div class="assure-policy-row" style="display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid var(--border-color);">
              <span style="color:var(--text-muted);">Nouvelle prime</span>
              <span style="font-weight:600;color:#10b981;" id="assureModalNewPremium">—</span>
            </div>
            <div class="assure-policy-row" style="display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid var(--border-color);">
              <span style="color:var(--text-muted);">Économies</span>
              <span style="font-weight:600;color:#10b981;" id="assureModalSavings">—</span>
            </div>
            <div class="assure-policy-row" style="display:flex;justify-content:space-between;font-size:12px;padding:4px 0;border-bottom:1px solid var(--border-color);">
              <span style="color:var(--text-muted);">Coût total des travaux</span>
              <span style="font-weight:500;" id="assureModalTotalCost">—</span>
            </div>
            <div class="assure-policy-row" style="display:flex;justify-content:space-between;font-size:12px;padding:4px 0;">
              <span style="color:var(--text-muted);">Validité de l'offre</span>
              <span style="font-weight:500;" id="assureModalExpiry">—</span>
            </div>
          </div>

          <div>
            <h4 style="font-size:12px;font-weight:600;color:var(--text-primary);margin-bottom:6px;">Travaux inclus</h4>
            <div class="assure-avenant-works" id="assureModalWorks"></div>
          </div>

          <div style="background:rgba(245,158,11,0.08);border:1px solid rgba(245,158,11,0.2);border-radius:var(--border-radius-sm);padding:10px 12px;display:flex;gap:8px;">
            <span class="material-symbols-outlined" style="font-size:16px!important;color:#f59e0b;flex-shrink:0;">info</span>
            <p style="font-size:11px;color:var(--text-secondary);line-height:1.5;">En signant cet engagement, vous vous engagez à réaliser les travaux listés ci-dessus. Votre prime d'assurance sera ajustée en fonction des économies estimées.</p>
          </div>

          <button type="button" id="assureSignConfirm" style="width:100%;padding:10px;border:none;border-radius:6px;background:var(--color-primary);color:#fff;font-family:var(--font-primary);font-size:14px;font-weight:600;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:6px;">
            <span class="material-symbols-outlined">how_to_reg</span> Signer l'engagement
          </button>
          <p style="text-align:center;font-size:10px;color:var(--text-muted);">Conformément à la réglementation, vous disposez d'un délai de rétractation de 14 jours.</p>
        </div>
      </div>
    </section>'''

# ── Find and replace the old view-assure-bien ────────────────────

old_start = content.find('id="view-assure-bien"')
if old_start < 0:
    old_start = content.find("id='view-assure-bien'")
if old_start < 0:
    old_start = content.find('id=\"view-assure-bien\"')

if old_start < 0:
    print('ERROR: Could not find view-assure-bien')
    exit(1)

# Find the section start
section_start = content.rfind('<section', 0, old_start)
after = content[section_start:]

# Find the matching closing section
depth = 1
i = after.find('>', 50) + 1
while i < len(after) and depth > 0:
    next_open = after.find('<section', i)
    next_close = after.find('</section>', i)
    if next_close == -1:
        break
    if next_open != -1 and next_open < next_close:
        depth += 1
        i = after.find('>', next_open) + 1
    else:
        depth -= 1
        i = next_close + 10

old_panel = after[:i]
print(f'Found old panel: {len(old_panel)} chars, replacing with {len(NEW_PANEL)} chars')

new_content = content.replace(old_panel, NEW_PANEL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('✅ view-assure-bien rebuilt successfully!')

# Verify the key IDs exist
import re
ids_needed = [
    'assureFormView', 'assureDashView', 'assureModeSelector',
    'assureModeDashBtn', 'assureModeFormBtn',
    'assurePropertyForm', 'assureFormSubmitBtn',
    'assureSignModal', 'assureSignModalClose', 'assureSignConfirm',
    'assureBannerName', 'assureBannerAddress', 'assureBannerPolicyTag',
    'assureBannerScore', 'assureBannerRisk',
    'assureStatScore', 'assureStatSavings', 'assureStatEngagement',
    'assurePropAddress', 'assurePropCity', 'assurePropDpe',
    'assurePropYear', 'assurePropRisk', 'assurePropScore',
    'assurGaugeBienFlood', 'assurGaugeBienClay', 'assurGaugeBienSeismic',
    'assurGaugeBienFloodVal', 'assurGaugeBienClayVal', 'assurGaugeBienSeismicVal',
    'assureBienImprove',
    'afi_address', 'afi_postalCode', 'afi_city', 'afi_typeBien',
    'afi_surface', 'afi_nbPieces', 'afi_nbEtages',
    'afi_anneeConstruction', 'afi_anneeRenovation',
    'afi_typeStructure', 'afi_etatStructure', 'afi_fissures', 'afi_affaissement',
    'afi_profondeurFondations', 'afi_hauteurPlancher',
    'afi_typeToiture', 'afi_materiauToit', 'afi_ageToiture', 'afi_anneeToiture',
    'afi_etatToiture', 'afi_isolationToiture', 'afi_isolationMurs', 'afi_isolationSol',
    'afi_panneauxSolaires',
    'afi_chauffagePrincipal', 'afi_installationElectriqueAnnee',
    'afi_climatisation', 'afi_presenceDetecteursFumee',
    'afi_occupation', 'afi_infiltrations',
    'afi_presenceSousSol', 'afi_presenceCave', 'afi_presenceGarage',
    'afi_clapetAntiRetour', 'afi_equipementsElecSousSol', 'afi_arbresProches',
    'afi_dpeClass', 'afi_expositionSolaire', 'afi_zoneMitoyennete',
    'afi_capitalAssure', 'afi_observations',
    'afi_presenceDetecteursFumee',
]

missing = [iid for iid in ids_needed if 'id=\n  "' + iid + '"' not in new_content and "id='" + iid + "'" not in new_content]
if missing:
    print(f'⚠️  Missing IDs: {len(missing)}')
    for m in missing:
        print(f'  - {m}')
else:
    print(f'✅ All {len(ids_needed)} critical IDs found!')
