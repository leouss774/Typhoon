import { Hono } from 'hono';
import { eq, desc } from 'drizzle-orm';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { db } from '../../database/client.js';
import { assessments } from '../../database/schema.js';
import { requireAuth, type AuthEnv } from '../middleware/auth.js';

export const assessmentRoutes = new Hono<AuthEnv>();

assessmentRoutes.use('*', requireAuth);

const statusSchema = z.object({
  status: z.enum(['nouveau', 'en_localisation', 'en_expertise', 'en_inspection', 'evalue']),
});

/* ── GET / — List assessments for the logged-in user ── */
assessmentRoutes.get('/', async (c) => {
  const user = c.get('user');
  const list = await db
    .select()
    .from(assessments)
    .where(eq(assessments.userId, user.sub))
    .orderBy(desc(assessments.createdAt));
  return c.json(list);
});

/* ── GET /stats — Dashboard stats (counts by status, recent activity) ── */
assessmentRoutes.get('/stats', async (c) => {
  const user = c.get('user');
  const all = await db
    .select()
    .from(assessments)
    .where(eq(assessments.userId, user.sub))
    .orderBy(desc(assessments.createdAt));

  const total = all.length;
  const nouveau = all.filter(a => a.status === 'nouveau').length;
  const enCours = all.filter(a => ['en_localisation', 'en_expertise', 'en_inspection'].includes(a.status ?? '')).length;
  const evalue = all.filter(a => a.status === 'evalue').length;

  // Recent activity (last 10)
  const recent = all.slice(0, 10).map(a => ({
    id: a.id,
    addressLabel: a.addressLabel,
    globalScore: a.globalScore,
    status: a.status,
    createdAt: a.createdAt,
  }));

  return c.json({ total, nouveau, enCours, evalue, recent });
});

/* ── GET /:id — Single assessment ── */
assessmentRoutes.get('/:id', async (c) => {
  const id = c.req.param('id');
  const record = await db.select().from(assessments).where(eq(assessments.id, id)).get();

  if (!record) {
    return c.json({ error: 'NOT_FOUND', message: 'Evaluation non trouvée' }, 404);
  }

  return c.json(record);
});

/* ── PATCH /:id/status — Update workflow status ── */
assessmentRoutes.patch('/:id/status', zValidator('json', statusSchema), async (c) => {
  const id = c.req.param('id');
  const { status } = c.req.valid('json');

  await db.update(assessments)
    .set({ status, updatedAt: new Date().toISOString() })
    .where(eq(assessments.id, id));

  return c.json({ success: true, status });
});

/* ── DELETE /:id ── */
assessmentRoutes.delete('/:id', async (c) => {
  const id = c.req.param('id');
  await db.delete(assessments).where(eq(assessments.id, id));
  return c.json({ success: true });
});
