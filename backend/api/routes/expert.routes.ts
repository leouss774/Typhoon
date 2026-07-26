import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';

const router = new Hono();

// In-memory store for expert assignments (replace with DB in production)
let assignments: Array<{
  id: string;
  clientId: string;
  clientName: string;
  propertyId: string;
  address: string;
  city: string;
  assignedTo: string;
  assignedByName: string;
  status: 'pending' | 'in_progress' | 'completed';
  createdAt: string;
  notes: string;
}> = [];

/**
 * POST /api/expert/assign
 * Assign an expert to a client/property for inspection.
 */
router.post('/assign', async (c) => {
  try {
    const body = await c.req.json();
    const { clientId, clientName, propertyId, address, city, assignedTo, assignedByName, notes } = body;

    if (!clientId || !assignedTo) {
      return c.json({ error: 'clientId et assignedTo requis' }, 400);
    }

    const assignment = {
      id: `assign-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      clientId,
      clientName: clientName || 'Client inconnu',
      propertyId: propertyId || '',
      address: address || '',
      city: city || '',
      assignedTo,
      assignedByName: assignedByName || 'Assureur',
      status: 'pending' as const,
      createdAt: new Date().toISOString(),
      notes: notes || '',
    };

    assignments.push(assignment);

    return c.json({ success: true, assignment }, 201);
  } catch (err: any) {
    return c.json({ error: err.message || 'Erreur lors de l\'assignation' }, 500);
  }
});

/**
 * GET /api/expert/missions/:expertId
 * Get missions assigned to a specific expert (by email or ID).
 */
router.get('/missions/:expertId', async (c) => {
  const expertId = c.req.param('expertId');
  const expertMissions = assignments.filter(a => a.assignedTo === expertId);

  // If no assignments yet, return empty array
  return c.json(expertMissions);
});

/**
 * GET /api/expert/missions
 * Get ALL missions (for admin overview).
 */
router.get('/missions', async (c) => {
  return c.json(assignments);
});

/**
 * PATCH /api/expert/missions/:id/status
 * Update mission status (pending → in_progress → completed).
 */
router.patch('/missions/:id/status', async (c) => {
  try {
    const id = c.req.param('id');
    const body = await c.req.json();
    const { status } = body;

    if (!['pending', 'in_progress', 'completed'].includes(status)) {
      return c.json({ error: 'Statut invalide' }, 400);
    }

    const idx = assignments.findIndex(a => a.id === id);
    if (idx < 0) {
      return c.json({ error: 'Mission non trouvée' }, 404);
    }

    assignments[idx].status = status;
    return c.json({ success: true, assignment: assignments[idx] });
  } catch (err: any) {
    return c.json({ error: err.message }, 500);
  }
});

export { router as expertRoutes };
