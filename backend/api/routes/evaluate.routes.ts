/**
 * Evaluate Routes — Scoring + Mistral Report Generation
 * ======================================================
 * POST /api/assessments/:id/evaluate  — compute scores + generate Mistral report
 * GET  /api/assessments/:id/report    — retrieve stored report
 */

import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { eq } from 'drizzle-orm';
import { db } from '../../database/client.js';
import { assessments, evaluationReports, expertForms } from '../../database/schema.js';
import { requireAuth, type AuthEnv } from '../middleware/auth.js';
import { generateMistralReport } from '../../services/mistral.service.js';

export const evaluateRoutes = new Hono<AuthEnv>();

evaluateRoutes.use('*', requireAuth);

const evaluateSchema = z.object({
  scores: z.object({
    global: z.number(),
    inondation: z.number(),
    rga: z.number(),
    tempete: z.number(),
    incendie: z.number(),
    seisme: z.number(),
  }),
});

/* ── POST — Generate evaluation report ── */
evaluateRoutes.post('/:id/evaluate', zValidator('json', evaluateSchema), async (c) => {
  const assessmentId = c.req.param('id');
  const { scores } = c.req.valid('json');
  const now = new Date().toISOString();

  // Load assessment
  const assessment = await db.select().from(assessments).where(eq(assessments.id, assessmentId)).get();
  if (!assessment) {
    return c.json({ error: 'NOT_FOUND', message: 'Évaluation non trouvée' }, 404);
  }

  // Load expert form (optional — may not exist yet)
  const expertForm = await db.select().from(expertForms).where(eq(expertForms.assessmentId, assessmentId)).get();
  const expertFields = expertForm ? JSON.parse(expertForm.fields) : {};

  try {
    // Generate Mistral report (deterministic fallback if no API key)
    const report = await generateMistralReport({
      addressLabel: assessment.addressLabel,
      buildingData: assessment.buildingData,
      risksData: assessment.risksData,
      geographyData: assessment.geographyData,
      expertFields,
      scores,
    });

    // Upsert evaluation report in DB
    const existing = await db.select().from(evaluationReports)
      .where(eq(evaluationReports.assessmentId, assessmentId)).get();

    if (existing) {
      await db.update(evaluationReports)
        .set({
          globalScore: scores.global,
          subScores: JSON.stringify(scores),
          reportContent: JSON.stringify(report),
          generatedAt: now,
        })
        .where(eq(evaluationReports.assessmentId, assessmentId));
    } else {
      await db.insert(evaluationReports).values({
        assessmentId,
        globalScore: scores.global,
        subScores: JSON.stringify(scores),
        reportContent: JSON.stringify(report),
      });
    }

    // Advance assessment status to evalue
    await db.update(assessments)
      .set({
        status: 'evalue',
        globalScore: scores.global,
        inondationScore: scores.inondation,
        rgaScore: scores.rga,
        tempeteScore: scores.tempete,
        incendieScore: scores.incendie,
        seismeScore: scores.seisme,
        updatedAt: now,
      })
      .where(eq(assessments.id, assessmentId));

    return c.json({ success: true, report });
  } catch (err) {
    console.error('[evaluate] Mistral error:', err);
    return c.json({ error: 'MISTRAL_ERROR', message: String(err) }, 502);
  }
});

/* ── GET — Retrieve stored report ── */
evaluateRoutes.get('/:id/report', async (c) => {
  const assessmentId = c.req.param('id');

  const report = await db.select().from(evaluationReports)
    .where(eq(evaluationReports.assessmentId, assessmentId)).get();

  if (!report) {
    return c.json({ error: 'NOT_FOUND', message: 'Rapport non trouvé' }, 404);
  }

  return c.json({
    globalScore: report.globalScore,
    subScores: report.subScores ? JSON.parse(report.subScores) : null,
    report: report.reportContent ? JSON.parse(report.reportContent) : null,
    generatedAt: report.generatedAt,
  });
});
