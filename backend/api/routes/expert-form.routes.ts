/**
 * Expert Form Routes
 * ==================
 * POST /api/assessments/:id/expert-form  — save expert form data
 * GET  /api/assessments/:id/expert-form  — load expert form data
 */

import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { eq } from 'drizzle-orm';
import { db } from '../../database/client.js';
import { assessments, expertForms } from '../../database/schema.js';
import { requireAuth, type AuthEnv } from '../middleware/auth.js';

export const expertFormRoutes = new Hono<AuthEnv>();

expertFormRoutes.use('*', requireAuth);

const expertFormSchema = z.object({
  fields: z.record(z.string()),
  recommendations: z.array(z.string()).optional(),
});

/* ── POST — Save / upsert expert form ── */
expertFormRoutes.post('/:id/expert-form', zValidator('json', expertFormSchema), async (c) => {
  const assessmentId = c.req.param('id');
  const { fields, recommendations } = c.req.valid('json');
  const now = new Date().toISOString();

  // Verify assessment exists
  const assessment = await db.select().from(assessments).where(eq(assessments.id, assessmentId)).get();
  if (!assessment) {
    return c.json({ error: 'NOT_FOUND', message: 'Évaluation non trouvée' }, 404);
  }

  // Upsert expert form
  const existing = await db.select().from(expertForms).where(eq(expertForms.assessmentId, assessmentId)).get();

  if (existing) {
    await db.update(expertForms)
      .set({
        fields: JSON.stringify(fields),
        recommendations: recommendations ? JSON.stringify(recommendations) : null,
        updatedAt: now,
      })
      .where(eq(expertForms.assessmentId, assessmentId));
  } else {
    await db.insert(expertForms).values({
      assessmentId,
      fields: JSON.stringify(fields),
      recommendations: recommendations ? JSON.stringify(recommendations) : null,
    });
  }

  // Advance assessment status to en_expertise
  await db.update(assessments)
    .set({ status: 'en_expertise', updatedAt: now })
    .where(eq(assessments.id, assessmentId));

  return c.json({ success: true });
});

/* ── GET — Load expert form ── */
expertFormRoutes.get('/:id/expert-form', async (c) => {
  const assessmentId = c.req.param('id');

  const form = await db.select().from(expertForms).where(eq(expertForms.assessmentId, assessmentId)).get();

  if (!form) {
    return c.json({ fields: {}, recommendations: [] });
  }

  return c.json({
    fields: JSON.parse(form.fields),
    recommendations: form.recommendations ? JSON.parse(form.recommendations) : [],
    updatedAt: form.updatedAt,
  });
});
