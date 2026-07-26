/**
 * Mistral AI Service — Structured risk report generation
 * ======================================================
 *
 * Builds a structured prompt from the risk assessment data and expert
 * form fields, then calls the Mistral Chat Completions API requesting
 * a deterministic JSON output.
 *
 * Output schema:
 * {
 *   niveauRisque: 'faible' | 'modere' | 'eleve' | 'critique',
 *   resume: string,
 *   pointsVigilance: string[],
 *   recommandations: Array<{ priorite: 'haute'|'moyenne'|'faible', action: string, impact: string }>,
 *   syntheseTexte: string,
 *   scoreJustification: string
 * }
 */

import { env } from '../config/env.js';

export interface MistralReport {
  niveauRisque: 'faible' | 'modere' | 'eleve' | 'critique';
  resume: string;
  pointsVigilance: string[];
  recommandations: Array<{
    priorite: 'haute' | 'moyenne' | 'faible';
    action: string;
    impact: string;
  }>;
  syntheseTexte: string;
  scoreJustification: string;
}

interface MistralMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

const SYSTEM_PROMPT = `Tu es un expert en évaluation de risques immobiliers pour une compagnie d'assurance française.
Tu analyses des données structurées (BDNB, Géorisques, formulaire expert) et génères un rapport de risque structuré.
Tu réponds UNIQUEMENT en JSON valide, sans markdown, sans backticks, sans texte avant ou après le JSON.
La langue est le français. Sois précis, concis et professionnel.`;

function buildUserPrompt(params: {
  addressLabel: string;
  buildingData: any;
  risksData: any;
  geographyData: any;
  expertFields: Record<string, string>;
  scores: { global: number; inondation: number; rga: number; tempete: number; incendie: number; seisme: number };
}): string {
  const { addressLabel, buildingData, risksData, geographyData, expertFields, scores } = params;

  const building = typeof buildingData === 'string' ? JSON.parse(buildingData) : (buildingData || {});
  const risks = typeof risksData === 'string' ? JSON.parse(risksData) : (risksData || {});

  return `Analyse ce bien immobilier et génère un rapport de risque structuré.

## Bien analysé
Adresse: ${addressLabel}
Année construction: ${building.builtYear ?? 'Inconnue'}
Surface: ${building.surfaceUtile ?? 'Inconnue'} m²
Niveaux: ${building.levels ?? 'Inconnu'}
Matériaux murs: ${building.wallMaterial ?? 'Inconnu'}
Toiture: ${building.roofMaterial ?? 'Inconnue'}
DPE: ${building.dpeClass ?? 'Inconnu'}

## Scores de risque calculés (0-100, 100 = risque maximal)
- Score global: ${scores.global}/100
- Inondation: ${scores.inondation}/100
- Retrait-Gonflement Argiles: ${scores.rga}/100
- Tempête/Vent: ${scores.tempete}/100
- Incendie/Feux de forêt: ${scores.incendie}/100
- Séisme: ${scores.seisme}/100

## Données Géorisques
- Zone inondation: ${risks?.naturels?.inondation?.present ? `Oui (${risks.naturels.inondation.level ?? 'niveau inconnu'})` : 'Non'}
- RGA: ${risks?.naturels?.retraitGonflementArgile?.present ? `Oui (${risks.naturels.retraitGonflementArgile.level ?? 'niveau inconnu'})` : 'Non'}
- Séisme: ${risks?.naturels?.seisme?.present ? `Oui (${risks.naturels.seisme.level ?? 'niveau inconnu'})` : 'Non'}
- Feu de forêt: ${risks?.naturels?.feuForet?.present ? 'Oui' : 'Non'}
- CATNAT 10 dernières années: ${risks?.catnatLast10Years ?? 0} événements

## Formulaire expert (déclaratif)
- Type bien: ${expertFields.type_bien ?? 'Non renseigné'}
- Sous-sol: ${expertFields.sous_sol ?? 'Non renseigné'}
- Hauteur plancher: ${expertFields.hauteur_plancher ?? 'Non renseigné'} cm
- Clapet anti-retour: ${expertFields.clapet ?? 'Non renseigné'}
- Équipements élec. sous-sol: ${expertFields.equip_elec ?? 'Non renseigné'}
- Profondeur fondations: ${expertFields.prof_fondations ?? 'Non renseigné'}
- Fissures: ${expertFields.fissures ?? 'Non renseigné'}
- Arbres proches: ${expertFields.arbres ?? 'Non renseigné'}
- Âge toiture: ${expertFields.age_toiture ?? 'Non renseigné'} ans
- Matériau toiture: ${expertFields.materiau_toit ?? 'Non renseigné'}
- Panneaux solaires: ${expertFields.panneaux ?? 'Non renseigné'}
- Capital assuré: ${expertFields.capital_assure ?? 'Non renseigné'} €

Génère un JSON avec exactement cette structure (sans markdown):
{
  "niveauRisque": "faible" | "modere" | "eleve" | "critique",
  "resume": "Résumé en 2-3 phrases",
  "pointsVigilance": ["point 1", "point 2", "point 3"],
  "recommandations": [
    { "priorite": "haute" | "moyenne" | "faible", "action": "action à entreprendre", "impact": "réduction de risque attendue" }
  ],
  "syntheseTexte": "Paragraphe de synthèse complet (5-8 phrases) pour le rapport d'assurance",
  "scoreJustification": "Explication concise du score global de ${scores.global}/100"
}

Fournis exactement 3 points de vigilance et entre 3 et 5 recommandations, classées par priorité décroissante.`;
}

/**
 * Generate a structured risk report using Mistral AI.
 * Falls back to a deterministic report if the API key is not configured.
 */
export async function generateMistralReport(params: {
  addressLabel: string;
  buildingData: any;
  risksData: any;
  geographyData: any;
  expertFields: Record<string, string>;
  scores: { global: number; inondation: number; rga: number; tempete: number; incendie: number; seisme: number };
}): Promise<MistralReport> {
  // Fallback when no API key is configured
  if (!env.MISTRAL_API_KEY) {
    return buildFallbackReport(params.scores, params.addressLabel);
  }

  const messages: MistralMessage[] = [
    { role: 'system', content: SYSTEM_PROMPT },
    { role: 'user', content: buildUserPrompt(params) },
  ];

  const response = await fetch('https://api.mistral.ai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${env.MISTRAL_API_KEY}`,
    },
    body: JSON.stringify({
      model: env.MISTRAL_MODEL || 'mistral-large-latest',
      messages,
      temperature: 0.2, // Low temperature for consistent, structured output
      max_tokens: 1500,
      response_format: { type: 'json_object' },
    }),
    signal: AbortSignal.timeout(30_000),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Mistral API error ${response.status}: ${err}`);
  }

  const data: any = await response.json();
  const content = data.choices?.[0]?.message?.content;
  if (!content) throw new Error('Empty response from Mistral');

  const parsed = JSON.parse(content) as MistralReport;

  // Validate required fields
  if (!parsed.niveauRisque || !parsed.syntheseTexte) {
    throw new Error('Invalid Mistral response structure');
  }

  return parsed;
}

/** Deterministic fallback when no Mistral key is configured */
function buildFallbackReport(
  scores: { global: number; inondation: number; rga: number; tempete: number; incendie: number; seisme: number },
  addressLabel: string,
): MistralReport {
  const niveau: MistralReport['niveauRisque'] =
    scores.global >= 70 ? 'critique' : scores.global >= 50 ? 'eleve' : scores.global >= 30 ? 'modere' : 'faible';

  const niveauLabel = { faible: 'faible', modere: 'modéré', eleve: 'élevé', critique: 'critique' }[niveau];

  return {
    niveauRisque: niveau,
    resume: `Le bien situé à ${addressLabel} présente un profil de risque ${niveauLabel} avec un score global de ${scores.global}/100. L'analyse couvre 5 périls principaux : inondation (${scores.inondation}), RGA (${scores.rga}), tempête (${scores.tempete}), incendie (${scores.incendie}) et séisme (${scores.seisme}).`,
    pointsVigilance: [
      scores.inondation >= 50 ? `Risque inondation élevé (${scores.inondation}/100) — vérifier le PPRI local` : `Risque inondation maîtrisé (${scores.inondation}/100)`,
      scores.rga >= 40 ? `Exposition aux argiles significative (${scores.rga}/100) — surveiller les fissures` : `Exposition aux argiles modérée (${scores.rga}/100)`,
      scores.tempete >= 40 ? `Vulnérabilité tempête notable (${scores.tempete}/100) — état de la toiture à vérifier` : `Résistance tempête correcte (${scores.tempete}/100)`,
    ],
    recommandations: [
      { priorite: 'haute', action: 'Vérification de l\'état de la toiture et de l\'étanchéité', impact: 'Réduction du risque tempête de 15 à 20%' },
      { priorite: 'moyenne', action: 'Installation d\'un clapet anti-retour sur les canalisations', impact: 'Réduction du risque inondation de 10%' },
      { priorite: 'faible', action: 'Réalisation d\'un diagnostic des fondations', impact: 'Meilleure évaluation du risque RGA' },
    ],
    syntheseTexte: `Ce bien immobilier présente un profil de risque ${niveauLabel} selon notre analyse multi-périls. Le score composite de ${scores.global}/100 a été calculé à partir de données issues de Géorisques, de la BDNB et du formulaire déclaratif expert. Les principaux facteurs de risque identifiés sont l'exposition au risque inondation (score ${scores.inondation}/100), au retrait-gonflement des argiles (score ${scores.rga}/100) et aux tempêtes (score ${scores.tempete}/100). Ce profil justifie une attention particulière lors de la souscription et potentiellement l'application de clauses spécifiques ou de franchises modulées. Les recommandations de travaux préventifs, si réalisées, pourraient améliorer significativement le score de risque et permettre une révision des conditions tarifaires. Note : rapport généré en mode dégradé (clé API Mistral non configurée).`,
    scoreJustification: `Score de ${scores.global}/100 calculé selon la pondération réglementaire : inondation 30% + RGA 25% + tempête 20% + incendie 15% + séisme 10%.`,
  };
}
