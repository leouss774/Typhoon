/**
 * Merged Assessment — Fusion des 3 sources (user_data + agent_data + step7)
 * ========================================================================
 *
 * Prend les 3 fichiers JSON en entrée et produit un MergedAssessment unifié
 * avec zones pour le Jumeau Numérique 3D (avant/après).
 *
 * Entrées:
 *   1. user_data  — Formulaire client (données déclaratives)
 *   2. agent_data — Orchestrateur Prévia (RiskAssessmentInput + PerilScores)
 *   3. step7      — Moteur de scoring externe (step7_demo_output.json)
 *
 * Sortie:
 *   MergedAssessment — Zones fusionnées pour la 3D + projection 2050
 */

/* ═══════════════════════════════════════════════════════════════
   Types — Zone Assessment (format contract JSON pour la 3D)
   ═══════════════════════════════════════════════════════════════ */

export interface Recommandation {
  travaux: string;
  cout_estime: string;
  gain_resilience: number;
}

export interface TestVulnerabilite {
  verdict: string;
  explication: string;
}

export interface TriggeredRule {
  rule_id: string;
  peril: string;
  points: number;
  justification: string;
  source_fields: string[];
  activated_by_llm: boolean;
}

export interface ZoneAssessment {
  risque: number;           // 0-100
  niveau: 'faible' | 'moyen' | 'eleve' | 'critique';
  alea_principal: string;
  justification: string;
  recommandations: Recommandation[];
  test_vulnerabilite?: TestVulnerabilite;
  triggered_rules: TriggeredRule[];
}

/* ═══════════════════════════════════════════════════════════════
   Footprint Geometry — Empreinte au sol du bâtiment
   ═══════════════════════════════════════════════════════════════ */

export interface FootprintGeometry {
  type: 'MultiPolygon' | 'Polygon';
  coordinates: number[][][][] | number[][][];
}

export interface MergedAssessment {
  score_global: number;
  zones: Record<string, ZoneAssessment>;
  projection_2050: {
    score_global: number;
    zones: Record<string, ZoneAssessment>;
  };
  // Métadonnées
  address: string;
  commune: string;
  code_insee: string;
  date_evaluation: string;
  // Confiance et données manquantes
  confidence: {
    level: 'high' | 'medium' | 'low';
    notes: string[];
  };
  donnees_manquantes: string[];
  /** Empreinte au sol du bâtiment (géométrie MultiPolygon BDNB en Lambert-93) */
  footprint?: FootprintGeometry | null;
}

/* ═══════════════════════════════════════════════════════════════
   Zone mapping — Périls → Zones 3D
   ═══════════════════════════════════════════════════════════════
   
   Chaque zone 3D est une combinaison pondérée des périls des 2 moteurs.
   Les poids reflètent l'impact relatif de chaque péril sur la zone.

   Zones: fondations, toiture, murs, sous_sol, fenetres
*/

interface ZoneDefinition {
  id: string;
  label: string;
  perils: Array<{
    key: string;
    source: 'step7' | 'previa';
    weight: number;
    alea_label: string;
  }>;
}

const ZONE_DEFINITIONS: ZoneDefinition[] = [
  {
    id: 'fondations',
    label: 'Fondations',
    perils: [
      { key: 'infiltration',  source: 'step7',  weight: 0.50, alea_label: 'Infiltration' },
      { key: 'aléas_naturels', source: 'step7', weight: 0.20, alea_label: 'RGA' },
      { key: 'rga',           source: 'previa', weight: 0.30, alea_label: 'RGA' },
    ],
  },
  {
    id: 'toiture',
    label: 'Toiture',
    perils: [
      { key: 'thermique',    source: 'step7',  weight: 0.60, alea_label: 'Thermique' },
      { key: 'tempete',      source: 'previa', weight: 0.40, alea_label: 'Tempête' },
    ],
  },
  {
    id: 'murs',
    label: 'Murs',
    perils: [
      { key: 'thermique',    source: 'step7',  weight: 0.30, alea_label: 'Thermique' },
      { key: 'tempete',      source: 'previa', weight: 0.30, alea_label: 'Tempête' },
      { key: 'seisme',       source: 'previa', weight: 0.20, alea_label: 'Séisme' },
      { key: 'aléas_naturels', source: 'step7', weight: 0.20, alea_label: 'Aléas naturels' },
    ],
  },
  {
    id: 'sous_sol',
    label: 'Sous-sol',
    perils: [
      { key: 'infiltration',  source: 'step7',  weight: 0.40, alea_label: 'Infiltration' },
      { key: 'aléas_naturels', source: 'step7', weight: 0.30, alea_label: 'Radon / cavités' },
      { key: 'inondation',   source: 'previa', weight: 0.30, alea_label: 'Inondation' },
    ],
  },
  {
    id: 'fenetres',
    label: 'Menuiseries',
    perils: [
      { key: 'thermique',         source: 'step7',  weight: 0.50, alea_label: 'Thermique' },
      { key: 'incendie_électrique', source: 'step7', weight: 0.30, alea_label: 'Incendie électrique' },
      { key: 'incendie',          source: 'previa', weight: 0.20, alea_label: 'Incendie' },
    ],
  },
];

/* ═══════════════════════════════════════════════════════════════
   Helpers
   ═══════════════════════════════════════════════════════════════ */

function clamp(n: number): number {
  return Math.max(0, Math.min(100, Math.round(n)));
}

function niveauFromScore(score: number): ZoneAssessment['niveau'] {
  if (score >= 80) return 'critique';
  if (score >= 60) return 'eleve';
  if (score >= 35) return 'moyen';
  return 'faible';
}

function getAleaPrincipal(zone: ZoneDefinition, step7Perils: Record<string, { score: number }>, previaScores: Record<string, number>): string {
  let maxWeighted = 0;
  let alea = zone.perils[0]?.alea_label || 'Inconnu';
  for (const p of zone.perils) {
    const score = p.source === 'step7' ? (step7Perils[p.key]?.score || 0) : (previaScores[p.key] || 0);
    const weighted = score * p.weight;
    if (weighted > maxWeighted) {
      maxWeighted = weighted;
      alea = p.alea_label;
    }
  }
  return alea;
}

/* ═══════════════════════════════════════════════════════════════
   Build triggered_rules for a zone from step7 data
   ═══════════════════════════════════════════════════════════════ */

function collectZoneRules(zoneId: string, step7: Step7Input): TriggeredRule[] {
  const zoneDef = ZONE_DEFINITIONS.find(z => z.id === zoneId);
  if (!zoneDef || !step7.score?.perils) return [];

  const rules: TriggeredRule[] = [];

  for (const peril of zoneDef.perils) {
    if (peril.source !== 'step7') continue;
    const perilData = step7.score.perils[peril.key];
    if (!perilData?.triggered_rules) continue;

    for (const rule of perilData.triggered_rules) {
      rules.push({
        rule_id: rule.rule_id || 'unknown',
        peril: peril.key,
        points: rule.points || 0,
        justification: rule.justification || 'Aucune justification',
        source_fields: rule.source_fields || [],
        activated_by_llm: rule.activated_by_llm || false,
      });
    }
  }

  return rules.sort((a, b) => b.points - a.points);
}

/* ═══════════════════════════════════════════════════════════════
   Build recommandations for a zone
   ═══════════════════════════════════════════════════════════════ */

function buildRecommandations(zoneId: string, score: number): Recommandation[] {
  const recs: Record<string, Recommandation[]> = {
    fondations: [
      { travaux: 'Étude géotechnique préalable', cout_estime: '2000-4000€', gain_resilience: 15 },
      { travaux: 'Reprise des fondations par micro-pieux', cout_estime: '8000-15000€', gain_resilience: 35 },
      { travaux: 'Drainage périphérique renforcé', cout_estime: '3000-6000€', gain_resilience: 25 },
    ],
    toiture: [
      { travaux: 'Remplacement de l\'isolation (laine de roche)', cout_estime: '4000-8000€', gain_resilience: 30 },
      { travaux: 'Réparation des tuiles endommagées', cout_estime: '1500-3000€', gain_resilience: 20 },
      { travaux: 'Installation de chéneaux renforcés', cout_estime: '1000-2000€', gain_resilience: 15 },
    ],
    murs: [
      { travaux: 'Rebouchage des fissures', cout_estime: '800-2000€', gain_resilience: 20 },
      { travaux: 'Application d\'un revêtement hydrofuge', cout_estime: '2000-4000€', gain_resilience: 25 },
      { travaux: 'Isolation thermique par extérieur (ITE)', cout_estime: '8000-15000€', gain_resilience: 35 },
    ],
    sous_sol: [
      { travaux: 'Cuvelage des murs enterrés', cout_estime: '5000-10000€', gain_resilience: 30 },
      { travaux: 'Pompe de relevage + clapet anti-retour', cout_estime: '1500-3000€', gain_resilience: 25 },
      { travaux: 'Ventilation mécanique contrôlée', cout_estime: '2000-4000€', gain_resilience: 20 },
    ],
    fenetres: [
      { travaux: 'Remplacement des joints d\'étanchéité', cout_estime: '300-800€', gain_resilience: 15 },
      { travaux: 'Installation de volets roulants isolants', cout_estime: '2000-5000€', gain_resilience: 25 },
      { travaux: 'Survitrage anti-tempête', cout_estime: '3000-6000€', gain_resilience: 30 },
    ],
  };

  const zoneRecs = recs[zoneId] || recs.fondations;
  // Filtrer par sévérité : si score bas, moins de recommandations
  if (score < 30) return zoneRecs.slice(0, 1);
  if (score < 60) return zoneRecs.slice(0, 2);
  return zoneRecs;
}

/* ═══════════════════════════════════════════════════════════════
   Test de vulnérabilité — Généré à partir des données
   ═══════════════════════════════════════════════════════════════ */

function buildTestVulnerabilite(zoneId: string, score: number, userData?: UserDataInput | null): TestVulnerabilite | undefined {
  if (score < 30) return undefined;

  const tests: Record<string, { ok: string; ko: string }> = {
    fondations: {
      ok: 'Les fondations semblent adaptées au type de sol. Aucun signe de fragilité structurelle majeure.',
      ko: 'La présence d\'argile et l\'ancienneté de la construction indiquent une vulnérabilité élevée au retrait-gonflement.',
    },
    toiture: {
      ok: 'La toiture est en bon état général. Les matériaux sont adaptés aux conditions climatiques locales.',
      ko: 'La toiture présente des signes de vieillissement. Risque de fuite et de déperdition calorifique en cas d\'épisode climatique extrême.',
    },
    murs: {
      ok: 'Les murs ne présentent pas de fissures structurelles. L\'isolation est conforme aux normes.',
      ko: 'Des fissures capillaires sont visibles. La structure est vulnérable aux cycles gel-dégel.',
    },
    sous_sol: {
      ok: 'Le sous-sol est sain. Aucun signe d\'humidité ou de remontée de nappe.',
      ko: 'Risque avéré de remontée de nappe et/ou de radon. Le sous-sol nécessite une attention particulière.',
    },
    fenetres: {
      ok: 'Les menuiseries sont récentes et bien isolées. Double vitrage en bon état.',
      ko: 'Les menuiseries sont anciennes. Risque de pont thermique et d\'infiltration d\'air.',
    },
  };

  const t = tests[zoneId] || tests.fondations;
  const fissures = userData?.fissures?.toLowerCase() || '';
  const infiltrations = userData?.infiltrations?.toLowerCase() || '';

  const isKo = score >= 60 ||
    (zoneId === 'fondations' && fissures.includes('importantes')) ||
    (zoneId === 'toiture' && infiltrations.includes('oui')) ||
    (zoneId === 'murs' && fissures.includes('légères')) ||
    (zoneId === 'sous_sol' && infiltrations.includes('oui'));

  return {
    verdict: isKo ? 'Vulnérable' : 'Résistant',
    explication: isKo ? t.ko : t.ok,
  };
}

/* ═══════════════════════════════════════════════════════════════
   Unified Assessment Input — Single JSON combining all 3 sources
   ═══════════════════════════════════════════════════════════════ */

/**
 * Format unifié qui encapsule les 3 sources en un seul fichier JSON :
 *   user_data  → formulaire client (déclaratif)
 *   agent_data → API publiques (BDNB, Géorisques, IGN, DVF, climat)
 *   step7      → moteur de scoring externe
 */
export interface UnifiedAssessmentInput {
  version: string;
  generated_at: string;
  user_data?: UserDataInput | null;
  agent_data?: {
    adresse?: string;
    coordonnees?: { latitude: number; longitude: number };
    code_insee?: string;
    score_geocodage?: number;
    georisques?: any;
    bdnb?: any;
    scores?: {
      score_incendie?: number;
      score_degats_eaux?: number;
      score_structurel?: number;
      score_global?: number;
      completude_donnees?: number;
    };
    [key: string]: any;
  } | null;
  step7?: Step7Input | null;
  demo_cases?: any[];
}

/* ═══════════════════════════════════════════════════════════════
   Input type definitions
   ═══════════════════════════════════════════════════════════════ */

export interface UserDataInput {
  adresse?: string;
  type_bien?: string;
  surface?: number;
  nb_etages?: number;
  occupation?: string;
  annee_construction?: number;
  annee_renovation?: number;
  type_structure?: string;
  etat_structure?: string;
  fissures?: string;
  affaissement?: string;
  type_toiture?: string;
  age_toiture?: number;
  etat_toiture?: string;
  infiltrations?: string;
  presence_sous_sol?: boolean;
  presence_cave?: boolean;
  [key: string]: any;
}

export interface AgentDataInput {
  adresse?: string;
  coordonnees?: { latitude: number; longitude: number; };
  code_insee?: string;
  georisques?: any;
  [key: string]: any;
}

export interface Step7PerilScore {
  raw_score: number;
  score: number;
  max_score: number;
  triggered_rules: Array<{
    rule_id?: string;
    peril?: string;
    priority?: number;
    points?: number;
    justification?: string;
    source_fields?: string[];
    activated_by_llm?: boolean;
  }>;
}

export interface Step7Input {
  address?: { adresse?: string; code_insee?: string; };
  risk_context?: {
    proxy_climatique?: any;
    rga?: any;
    zone_sismique?: any;
    radon?: any;
    cavites?: any;
    historique_catnat?: any;
    facilites_proches?: any;
    donnees_topo?: any;
    eaux_souterraines?: any;
    donnees_manquantes?: string[];
  };
  score?: {
    global: number;
    global_raw?: number;
    weights?: Record<string, number>;
    perils: Record<string, Step7PerilScore>;
  };
  confidence?: {
    level: string;
    notes?: Array<{ confidence_id: string; impact: string; note: string; }>;
  };
  traceability?: {
    score_engine?: string;
    mistral_used?: boolean;
    selected_composed_rule_ids?: string[];
  };
  mistral?: {
    activated_rule_ids?: string[];
    declarative_consistency_status?: string;
  };
  profil_bien?: Record<string, any>;
  [key: string]: any;
}

/* ═══════════════════════════════════════════════════════════════
   MAIN — mergeAssessment()
   ═══════════════════════════════════════════════════════════════ */

export function mergeAssessment(
  userData?: UserDataInput | null,
  step7?: Step7Input | null,
  previaScores?: Record<string, number> | null,
): MergedAssessment {
  // --- Extract step7 perils scores ---
  const step7Perils: Record<string, { score: number; rules: TriggeredRule[] }> = {};
  if (step7?.score?.perils) {
    for (const [key, peril] of Object.entries(step7.score.perils)) {
      step7Perils[key] = {
        score: peril.score || 0,
        rules: (peril.triggered_rules || []).map(r => ({
          rule_id: r.rule_id || 'unknown',
          peril: r.peril || key,
          points: r.points || 0,
          justification: r.justification || '',
          source_fields: r.source_fields || [],
          activated_by_llm: r.activated_by_llm || false,
        })),
      };
    }
  }

  // --- Default previaScores if missing ---
  const defPrevia: Record<string, number> = {
    inondation: 0, rga: 0, tempete: 0, incendie: 0, seisme: 0,
  };
  const previa = previaScores || defPrevia;

  // --- Compute zones ---
  const zones: Record<string, ZoneAssessment> = {};
  const projectedZones: Record<string, ZoneAssessment> = {};

  // Deltas climatiques pour projection 2050
  const CLIMATE_DELTAS: Record<string, number> = {
    infiltration: 0.15,
    thermique: 0.25,
    incendie_électrique: 0.05,
    aléas_naturels: 0.10,
    inondation: 0.15,
    rga: 0.20,
    tempete: 0.10,
    incendie: 0.05,
    seisme: 0.02,
  };

  for (const zoneDef of ZONE_DEFINITIONS) {
    let score = 0;
    let projectedScore = 0;

    for (const peril of zoneDef.perils) {
      const perilScore = peril.source === 'step7'
        ? (step7Perils[peril.key]?.score || 0)
        : (previa[peril.key] || 0);

      score += perilScore * peril.weight;

      // Projection: apply climate delta
      const delta = CLIMATE_DELTAS[peril.key] || 0.10;
      projectedScore += Math.min(100, perilScore * (1 + delta)) * peril.weight;
    }

    score = clamp(score);
    projectedScore = clamp(projectedScore);

    const triggeredRules = collectZoneRules(zoneDef.id, step7!);
    const aleaPrincipal = getAleaPrincipal(zoneDef, step7Perils, previa);

    zones[zoneDef.id] = {
      risque: score,
      niveau: niveauFromScore(score),
      alea_principal: aleaPrincipal,
      justification: `Risque ${niveauFromScore(score)} sur la zone ${zoneDef.label}. Score combiné: ${score}/100. Aléa principal: ${aleaPrincipal}.`,
      recommandations: buildRecommandations(zoneDef.id, score),
      test_vulnerabilite: buildTestVulnerabilite(zoneDef.id, score, userData),
      triggered_rules: triggeredRules,
    };

    projectedZones[zoneDef.id] = {
      risque: projectedScore,
      niveau: niveauFromScore(projectedScore),
      alea_principal: aleaPrincipal,
      justification: `Projection 2050: risque ${niveauFromScore(projectedScore)} sur ${zoneDef.label}. Score projeté: ${projectedScore}/100. Aggravation due au changement climatique.`,
      recommandations: buildRecommandations(zoneDef.id, projectedScore),
      test_vulnerabilite: buildTestVulnerabilite(zoneDef.id, projectedScore, userData),
      triggered_rules: triggeredRules,
    };
  }

  // --- Global scores ---
  const globalScore = clamp(
    Object.values(zones).reduce((sum, z) => sum + z.risque, 0) / Object.keys(zones).length
  );
  const projectedGlobalScore = clamp(
    Object.values(projectedZones).reduce((sum, z) => sum + z.risque, 0) / Object.keys(projectedZones).length
  );

  // --- Confidence ---
  const confidenceLevel = step7?.confidence?.level || 'medium';
  const confidenceNotes: string[] = (step7?.confidence?.notes || []).map(
    n => `[${n.impact}] ${n.note}`
  );
  if (!userData) {
    confidenceNotes.push('[high] Aucune donnée déclarative — scores basés uniquement sur les APIs publiques');
  }

  // --- Données manquantes ---
  const donneesManquantes: string[] = step7?.risk_context?.donnees_manquantes || [];
  if (!userData?.fissures) donneesManquantes.push('fissures (donnée déclarative manquante)');
  if (!userData?.presence_sous_sol) donneesManquantes.push('présence sous-sol (donnée déclarative manquante)');

  return {
    score_global: globalScore,
    zones,
    projection_2050: {
      score_global: projectedGlobalScore,
      zones: projectedZones,
    },
    address: userData?.adresse || step7?.address?.adresse || '',
    commune: step7?.address?.adresse?.split(',').pop()?.trim() || '',
    code_insee: step7?.address?.code_insee || '',
    date_evaluation: new Date().toISOString().split('T')[0],
    confidence: {
      level: confidenceLevel as 'high' | 'medium' | 'low',
      notes: confidenceNotes,
    },
    donnees_manquantes: donneesManquantes,
  };
}

/* ═══════════════════════════════════════════════════════════════
   Sample step7 data — embedded for demo mode (no backend needed)
   ═══════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════════
   Parse Unified JSON → 3 sources séparées pour mergeAssessment()
   ═══════════════════════════════════════════════════════════════ */

/**
 * Parse un UnifiedAssessmentInput et extrait les 3 sources.
 * Gère aussi les formats legacy (step7 seul, demo_cases wrapper).
 */
export function parseUnifiedInput(json: any): {
  userData: UserDataInput | null;
  step7: Step7Input | null;
  previaScores: Record<string, number> | null;
  footprint: any;
} {
  const result = { userData: null as UserDataInput | null, step7: null as Step7Input | null, previaScores: null as Record<string, number> | null, footprint: null as any };

  // Détection du format UnifiedAssessmentInput
  if (json.user_data || json.agent_data || json.step7 || json.version) {
    // Extraire user_data
    result.userData = json.user_data || null;

    // Extraire step7
    if (json.step7) {
      // Normaliser demo_cases wrapper si présent dans step7
      let step7Data = json.step7;
      if (step7Data.demo_cases && Array.isArray(step7Data.demo_cases) && step7Data.demo_cases.length > 0) {
        step7Data = step7Data.demo_cases[0];
      }
      result.step7 = step7Data as Step7Input;
    }

    // Extraire les scores depuis agent_data
    if (json.agent_data?.scores) {
      result.previaScores = {
        inondation: json.agent_data.scores.score_degats_eaux ?? 0,
        rga: json.agent_data.scores.score_structurel ?? 0,
        tempete: json.agent_data.scores.score_structurel ?? 0,
        incendie: json.agent_data.scores.score_incendie ?? 0,
        seisme: json.agent_data.scores.score_global ?? 0,
      };
    }

    // Extraire footprint depuis agent_data
    if (json.agent_data?.bdnb?.geometry) {
      result.footprint = json.agent_data.bdnb.geometry;
    } else if (json.agent_data?.footprint) {
      result.footprint = json.agent_data.footprint;
    }

    return result;
  }

  // Format legacy: demo_cases wrapper
  if (json.demo_cases && Array.isArray(json.demo_cases) && json.demo_cases.length > 0) {
    const first = json.demo_cases[0];
    result.step7 = first as Step7Input;
    return result;
  }

  // Format legacy: step7 direct
  if (json.score?.perils) {
    result.step7 = json as Step7Input;
    return result;
  }

  return result;
}

export const SAMPLE_STEP7_DATA: Step7Input = {
  "address": {
    "adresse": "8 Allée du Port Maillard 44000 Nantes",
    "code_insee": "44109"
  },
  "risk_context": {
    "rga": { "present": true, "exposition": "faible", "code_exposition": "1" },
    "zone_sismique": { "present": true, "zone_code": "3", "zone_libelle": "3 - MODEREE" },
    "radon": { "present": true, "classe_potentiel": "3" },
    "cavites": { "present": false, "count": 0, "disponible": false },
    "historique_catnat": {
      "total_evts": 10,
      "evts_par_type": { "inondation": 9, "mouvement_terrain": 1 },
      "nb_evt_10ans": 4
    },
    "donnees_topo": { "altitude_m": 7.35 },
    "donnees_manquantes": ["drias_meteofrance", "copernicus", "sentinel"]
  },
  "profil_bien": {
    "disponible": true,
    "annee_construction": 1965,
    "type_bien": "maison",
    "type_toiture": "tuiles",
    "isolation_toiture": "faible",
    "isolation_murs": "moyenne",
    "presence_sous_sol": true,
    "presence_cave": true,
    "installation_electrique_annee": 1988
  },
  "score": {
    "global": 43,
    "perils": {
      "infiltration": {
        "score": 82, "raw_score": 82, "max_score": 100,
        "triggered_rules": [
          { "rule_id": "INONDATION_PRESENT_INFILTRATION", "peril": "infiltration", "priority": 100, "points": 20, "justification": "Présence d'un risque d'inondation au droit de l'adresse, augmentant l'exposition à l'humidité.", "source_fields": ["georisques.rapport_risque.risquesNaturels.inondation"], "activated_by_llm": false },
          { "rule_id": "REMONTEE_NAPPE_PRESENT_INFILTRATION", "peril": "infiltration", "priority": 95, "points": 18, "justification": "Présence d'un risque de remontée de nappe, facteur direct d'humidité durable en sous-sol.", "source_fields": ["georisques.rapport_risque.risquesNaturels.remonteeNappe"], "activated_by_llm": false },
          { "rule_id": "COMPOSE_TOITURE_AGEE_ET_HUMIDITE", "peril": "infiltration", "priority": 50, "points": 12, "justification": "Toiture ancienne combinée à un contexte hydrique défavorable, augmentant le risque d'infiltration.", "source_fields": ["profil_bien.annee_construction", "profil_bien.type_toiture"], "activated_by_llm": true }
        ]
      },
      "thermique": {
        "score": 23, "raw_score": 23, "max_score": 100,
        "triggered_rules": [
          { "rule_id": "THERMIQUE_CLIMATE_ZONE_INTERMEDIAIRE", "peril": "thermique", "priority": 90, "points": 5, "justification": "Zone climatique intermédiaire, proxy modéré de stress thermique.", "source_fields": ["proxy_climatique.code"], "activated_by_llm": false },
          { "rule_id": "COMPOSE_ISOLATION_FAIBLE_ET_HUMIDITE", "peril": "thermique", "priority": 50, "points": 10, "justification": "Isolation toiture absente ou faible sur bâti ancien, augmentant la vulnérabilité thermique.", "source_fields": ["profil_bien.isolation_toiture", "profil_bien.annee_construction"], "activated_by_llm": true }
        ]
      },
      "incendie_électrique": {
        "score": 10, "raw_score": 10, "max_score": 100,
        "triggered_rules": [
          { "rule_id": "COMPOSE_INSTALLATION_ELECTRIQUE_ANCIENNE", "peril": "incendie_électrique", "priority": 50, "points": 10, "justification": "Installation électrique ancienne (1988), facteur de surcharge et défaut d'isolement.", "source_fields": ["profil_bien.installation_electrique_annee"], "activated_by_llm": true }
        ]
      },
      "aléas_naturels": {
        "score": 50, "raw_score": 50, "max_score": 100,
        "triggered_rules": [
          { "rule_id": "RADON_CLASSE_3", "peril": "aléas_naturels", "priority": 100, "points": 8, "justification": "Potentiel radon élevé, facteur sanitaire et indicateur de perméabilité des sols.", "source_fields": ["georisques.radon.classe_potentiel"], "activated_by_llm": false },
          { "rule_id": "SEISME_ZONE_MODEREE", "peril": "aléas_naturels", "priority": 100, "points": 10, "justification": "Zone sismique modérée, facteur de contrainte structurelle.", "source_fields": ["georisques.zonage_sismique.zone_code"], "activated_by_llm": false },
          { "rule_id": "CATNAT_MOINS_DE_2ANS", "peril": "aléas_naturels", "priority": 95, "points": 12, "justification": "Sinistre CatNat récent, proxy de vulnérabilité locale active.", "source_fields": ["georisques.catnat"], "activated_by_llm": false },
          { "rule_id": "CATNAT_FREQUENCE_ELEVEE", "peril": "aléas_naturels", "priority": 85, "points": 10, "justification": "Fréquence CatNat élevée, indicateur de récurrence d'aléas.", "source_fields": ["georisques.catnat"], "activated_by_llm": false }
        ]
      }
    }
  },
  "confidence": {
    "level": "medium",
    "notes": [
      { "confidence_id": "DATA_MISSING_CLIMATE", "impact": "medium", "note": "Composantes climatiques prospectives absentes; scores basés sur proxys disponibles." }
    ]
  },
  "traceability": {
    "score_engine": "deterministic_yaml_v1",
    "mistral_used": true,
    "selected_composed_rule_ids": ["COMPOSE_INSTALLATION_ELECTRIQUE_ANCIENNE", "COMPOSE_ISOLATION_FAIBLE_ET_HUMIDITE", "COMPOSE_TOITURE_AGEE_ET_HUMIDITE"]
  },
  "mistral": {
    "activated_rule_ids": ["COMPOSE_TOITURE_AGEE_ET_HUMIDITE", "COMPOSE_ISOLATION_FAIBLE_ET_HUMIDITE", "COMPOSE_INSTALLATION_ELECTRIQUE_ANCIENNE"],
    "declarative_consistency_status": "warning"
  }
};

/**
 * SAMPLE_UNIFIED_INPUT — Demo JSON combinant les 3 sources en un seul fichier
 *
 * Contient user_data + agent_data + step7 dans une seule enveloppe.
 * Parfait pour tester le pipeline sans dépendre de l'orchestrateur.
 */
export const SAMPLE_UNIFIED_INPUT: UnifiedAssessmentInput = {
  "version": "1.0",
  "generated_at": "2026-07-23T10:00:00Z",
  "user_data": {
    "adresse": "8 Allée du Port Maillard 44000 Nantes",
    "type_bien": "Maison individuelle",
    "surface": 100,
    "nb_etages": 2,
    "annee_construction": 1965,
    "annee_renovation": 2020,
    "type_structure": "Béton armé",
    "etat_structure": "Bon",
    "fissures": "Légères",
    "affaissement": "Non",
    "type_toiture": "Tuiles",
    "age_toiture": 1965,
    "etat_toiture": "Moyen",
    "infiltrations": "Non",
    "presence_sous_sol": true,
    "presence_cave": true,
    "occupation": "Occupé",
    "installation_electrique_annee": 1988,
  },
  "agent_data": {
    "adresse": "8 Allée du Port Maillard 44000 Nantes",
    "coordonnees": { "latitude": 47.214972, "longitude": -1.551503 },
    "code_insee": "44109",
    "score_geocodage": 0.5514,
    "georisques": {
      "argiles_rga": [{ "codeExposition": "1", "exposition": "Exposition faible" }],
      "zonage_sismique": [{ "zone": "3", "libelle": "MODEREE" }],
      "radon": { "classe_potentiel": "3" },
      "catnat": { "total_evts": 10 },
    },
    "bdnb": {
      "geometry": null,
    },
    "scores": {
      "score_incendie": 12,
      "score_degats_eaux": 52,
      "score_structurel": 38,
      "score_global": 36,
      "completude_donnees": 1,
    },
  },
  "step7": SAMPLE_STEP7_DATA,
};

/**
 * Default user data for demo mode — simulates a completed client form.
 */
export const DEFAULT_USER_DATA: UserDataInput = {
  adresse: '8 Allée du Port Maillard 44000 Nantes',
  type_bien: 'Maison individuelle',
  surface: 100,
  nb_etages: 2,
  occupation: 'Occupé',
  annee_construction: 1965,
  annee_renovation: 2020,
  type_structure: 'Béton armé',
  etat_structure: 'Bon',
  fissures: 'Légères',
  affaissement: 'Non',
  type_toiture: 'Tuiles',
  age_toiture: 1965,
  etat_toiture: 'Moyen',
  infiltrations: 'Non',
  presence_sous_sol: true,
  presence_cave: true,
  installation_electrique_annee: 1988,
};

/* ═══════════════════════════════════════════════════════════════
   score → couleur + helpers pour la 3D
   ═══════════════════════════════════════════════════════════════ */

export function scoreToColor(score: number): string {
  if (score >= 80) return '#dc2626';  // critique → rouge foncé
  if (score >= 60) return '#ef4444';  // élevé    → rouge
  if (score >= 45) return '#f59e0b';  // moyen    → orange
  if (score >= 25) return '#3b82f6';  // faible   → bleu
  return '#10b981';                    // très faible → vert
}

export function scoreToRiskLabel(score: number): string {
  if (score >= 80) return 'Critique';
  if (score >= 60) return 'Élevé';
  if (score >= 45) return 'Modéré';
  if (score >= 25) return 'Faible';
  return 'Très faible';
}

export function scoreToRiskClass(score: number): 'critical' | 'high' | 'medium' | 'low' {
  if (score >= 80) return 'critical';
  if (score >= 60) return 'high';
  if (score >= 45) return 'medium';
  return 'low';
}

import type { HousePartData } from './house3d.js';

/* ═══════════════════════════════════════════════════════════════
   Convert MergedAssessment → HousePartData (pour la 3D)
   ═══════════════════════════════════════════════════════════════ */

/**
 * Convertit le MergedAssessment en HousePartData pour la 3D.
 * @param assessment Le merged assessment
 * @param timeMode 'current' (2025) ou 'projected' (2050)
 */
export function mergedToHousePartData(
  assessment: MergedAssessment,
  timeMode: 'current' | 'projected' = 'current',
): Record<string, HousePartData> {
  const zones = timeMode === 'projected'
    ? assessment.projection_2050.zones
    : assessment.zones;

  // Mapping: zone id → house part id
  const zoneToPart: Record<string, string> = {
    fondations: 'ground',
    toiture: 'roof',
    murs: 'walls',
    fenetres: 'windows',
    sous_sol: 'ground', // sous-sol partage la même zone 3D que ground
  };

  const result: Record<string, HousePartData> = {};

  for (const [zoneId, zone] of Object.entries(zones)) {
    const partId = zoneToPart[zoneId] || zoneId;
    const riskClass = scoreToRiskClass(zone.risque);

    // Construire la description à partir des règles déclenchées
    const topRules = zone.triggered_rules.slice(0, 3);
    const rulesText = topRules.length > 0
      ? topRules.map(r => `• ${r.justification}`).join('\n')
      : zone.justification;

    // Coût estimé depuis les recommandations
    const avgCost = zone.recommandations.length > 0
      ? zone.recommandations[0].cout_estime
      : 'Non estimé';

    result[partId] = {
      id: partId,
      label: zoneId === 'ground' ? 'Fondations & Sous-sol' : (zoneId.charAt(0).toUpperCase() + zoneId.slice(1)),
      risk: riskClass,
      score: zone.risque,
      description: rulesText,
      cost: avgCost,
      annualSavings: `−${Math.round(zone.risque * 2.5)} €/an`,
      works: zone.recommandations.map(r => r.travaux),
      premiumAfter: `−${Math.round(zone.risque * 0.15)}%`,
      // Extended data for the side panel
      alea_principal: zone.alea_principal,
      niveau: zone.niveau,
      triggered_rules: zone.triggered_rules,
      recommandations: zone.recommandations,
      test_vulnerabilite: zone.test_vulnerabilite,
    };
  }

  return result;
}
