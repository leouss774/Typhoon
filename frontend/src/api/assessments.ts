/**
 * Frontend Assessments API Client
 * ================================
 * Typed wrappers for all assessment-related backend endpoints.
 */

import { apiFetch } from './client.js';

export type AssessmentStatus = 'nouveau' | 'en_localisation' | 'en_expertise' | 'en_inspection' | 'evalue';

export interface Assessment {
  id: string;
  addressLabel: string;
  longitude: number;
  latitude: number;
  status: AssessmentStatus;
  globalScore: number | null;
  inondationScore: number | null;
  rgaScore: number | null;
  tempeteScore: number | null;
  incendieScore: number | null;
  seismeScore: number | null;
  createdAt: string;
  updatedAt: string;
}

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

/* ── List assessments ── */
export async function getAssessments(): Promise<Assessment[]> {
  return apiFetch<Assessment[]>('/api/assessments');
}

/* ── Update workflow status ── */
export async function updateAssessmentStatus(id: string, status: AssessmentStatus): Promise<void> {
  await apiFetch(`/api/assessments/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

/* ── Save expert form ── */
export async function saveExpertForm(
  assessmentId: string,
  fields: Record<string, string>,
  recommendations?: string[],
): Promise<void> {
  await apiFetch(`/api/assessments/${assessmentId}/expert-form`, {
    method: 'POST',
    body: JSON.stringify({ fields, recommendations }),
  });
}

/* ── Load expert form ── */
export async function loadExpertForm(
  assessmentId: string,
): Promise<{ fields: Record<string, string>; recommendations: string[]; updatedAt?: string }> {
  return apiFetch(`/api/assessments/${assessmentId}/expert-form`);
}

/* ── Generate evaluation report (calls Mistral) ── */
export async function generateEvaluationReport(
  assessmentId: string,
  scores: { global: number; inondation: number; rga: number; tempete: number; incendie: number; seisme: number },
): Promise<{ success: boolean; report: MistralReport }> {
  return apiFetch(`/api/assessments/${assessmentId}/evaluate`, {
    method: 'POST',
    body: JSON.stringify({ scores }),
  });
}

/* ── Get stored report ── */
export async function getEvaluationReport(assessmentId: string): Promise<{
  globalScore: number;
  subScores: Record<string, number>;
  report: MistralReport;
  generatedAt: string;
} | null> {
  try {
    return await apiFetch(`/api/assessments/${assessmentId}/report`);
  } catch {
    return null;
  }
}
