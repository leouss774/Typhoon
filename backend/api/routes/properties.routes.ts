import { Hono } from 'hono';
import { z } from 'zod';
import { zValidator } from '@hono/zod-validator';
import { eq, inArray } from 'drizzle-orm';
import { db } from '../../database/client.js';
import { properties } from '../../database/schema.js';
import { requireAuth, type AuthEnv } from '../middleware/auth.js';

export const propertyRoutes = new Hono<AuthEnv>();

propertyRoutes.use('*', requireAuth);

/* ═══════════════════════════════════════════════════════════════
   Schéma complet du formulaire client (30+ champs)
   Correspond au formulaire.json — version 1.0
   ═══════════════════════════════════════════════════════════════ */

const propertyInputSchema = z.object({
  // Liaison client
  clientId: z.string().min(1, 'Client requis'),

  // Adresse
  address: z.string().min(1, 'Adresse requise'),
  postalCode: z.string().optional(),
  city: z.string().optional(),

  // Général
  typeBien: z.enum(['maison', 'appartement', 'immeuble', 'local_commercial', 'autre']).optional(),
  surface: z.number().min(1).max(10000).optional(),
  nbPieces: z.number().int().min(1).max(50).optional(),
  nbEtages: z.number().int().min(0).max(50).optional(),
  anneeConstruction: z.number().int().min(1700).max(2026).optional(),
  anneeRenovation: z.number().int().min(1700).max(2026).optional(),

  // Structure
  typeStructure: z.enum(['Béton armé', 'Pierre', 'Brique', 'Bois', 'Métal', 'Mixte', 'Autre']).optional(),
  etatStructure: z.enum(['Neuf', 'Bon', 'Moyen', 'Médiocre', 'Vétuste']).optional(),
  fissures: z.enum(['Aucune', 'Légères', 'Moyennes', 'Importantes', 'Structurelles']).optional(),
  affaissement: z.enum(['non', 'leger', 'visible', 'important']).optional(),

  // Toiture & Isolation
  typeToiture: z.enum(['Tuiles', 'Ardoises', 'Zinc', 'Bac acier', 'Béton', 'Végétalisée', 'Autre']).optional(),
  ageToiture: z.number().int().min(0).max(200).optional(),
  anneeToiture: z.number().int().min(1900).max(2026).optional(),
  etatToiture: z.enum(['Neuf', 'Bon', 'Moyen', 'Médiocre', 'Vétuste']).optional(),
  isolationToiture: z.enum(['neuve', 'bonne', 'moyenne', 'faible', 'absente']).optional(),
  isolationMurs: z.enum(['neuve', 'bonne', 'moyenne', 'faible', 'absente']).optional(),
  isolationSol: z.enum(['neuve', 'bonne', 'moyenne', 'faible', 'absente']).optional(),
  infiltrations: z.enum(['Non', 'Occasionnelles', 'Récurrentes', 'Permanentes']).optional(),

  // Sous-sol & Équipements
  presenceSousSol: z.boolean().optional(),
  presenceCave: z.boolean().optional(),
  presenceGarage: z.boolean().optional(),
  occupation: z.enum(['Occupé', 'Vacant', 'Loué', 'Secondaire']).optional(),
  climatisation: z.boolean().optional(),
  chauffagePrincipal: z.enum(['Électrique', 'Gaz', 'Fioul', 'Bois', 'Pompe à chaleur', 'Réseau de chaleur', 'Solaire', 'Autre']).optional(),

  // Électricité & Sécurité
  installationElectriqueAnnee: z.number().int().min(1900).max(2026).optional(),
  presenceDetecteursFumee: z.boolean().optional(),

  // Exposition & Environnement
  expositionSolaire: z.enum(['Faible', 'Moyenne', 'Forte', 'Très forte']).optional(),
  zoneMitoyennete: z.enum(["Isolé", "Mitoyen d'un côté", "Mitoyen des deux côtés", "En bande"]).optional(),

  // Inondation
  hauteurPlancher: z.number().min(0).max(500).optional(),
  clapetAntiRetour: z.boolean().optional(),
  equipementsElecSousSol: z.boolean().optional(),

  // RGA
  profondeurFondations: z.enum(['Moins de 50 cm', '50 à 80 cm', 'Plus de 80 cm', 'Non connu']).optional(),
  arbresProches: z.boolean().optional(),
  materiauToit: z.enum(['Tuiles canal', 'Tuiles mécaniques', 'Ardoises naturelles', 'Ardoises synthétiques', 'Zinc', 'Bac acier', 'Shingle', 'Béton', 'Autre']).optional(),
  panneauxSolaires: z.boolean().optional(),

  // Assurantiel
  capitalAssure: z.number().min(0).optional(),

  // DPE & BDNB
  dpeClass: z.string().optional(),
  banId: z.string().optional(),
  longitude: z.number().optional(),
  latitude: z.number().optional(),

  // Observations
  observations: z.string().optional(),
});

export type PropertyInput = z.infer<typeof propertyInputSchema>;

/* ── Helper: keep optional booleans nullable for Drizzle boolean-mode columns ── */
function b(v: boolean | undefined): boolean | null {
  return v === undefined ? null : v;
}

/* ═══════════════════════════════════════════════════════════════
   Routes
   ═══════════════════════════════════════════════════════════════ */

propertyRoutes.get('/', async (c) => {
  const list = await db.select().from(properties);
  return c.json(list);
});

/* ── GET /pending — Properties with formCompleted=true that have no assessment yet ── */
propertyRoutes.get('/pending', async (c) => {
  const { eq, isNull } = await import('drizzle-orm');
  const { assessments } = await import('../../database/schema.js');
  const { clients } = await import('../../database/schema.js');

  // Get all properties with formCompleted
  const allProps = await db.select().from(properties).where(eq(properties.formCompleted, true));

  // Get all assessed property IDs
  const allAssessments = await db.select({ propertyId: assessments.propertyId }).from(assessments);
  const assessedIds = new Set(allAssessments.map(a => a.propertyId).filter(Boolean));

  // Filter: completed but not assessed
  const pending = allProps.filter(p => !assessedIds.has(p.id));

  // Single query for all client names (avoids N+1)
  const clientIds = pending.map(p => p.clientId).filter(Boolean);
  let clientMap = new Map<string, { firstName: string; lastName: string }>();
  if (clientIds.length > 0) {
    const allClients = await db.select({
      id: clients.id,
      firstName: clients.firstName,
      lastName: clients.lastName,
    }).from(clients).where(inArray(clients.id, clientIds));
    clientMap = new Map(allClients.map(c => [c.id, c]));
  }

  const result = pending.map(p => {
    const client = clientMap.get(p.clientId);
    return {
      id: p.id,
      clientId: p.clientId,
      clientName: client ? `${client.firstName} ${client.lastName}` : 'Client inconnu',
      address: p.address || '',
      city: p.city || '',
      createdAt: p.createdAt || '',
      propertyType: p.typeBien || 'Non renseigné',
    };
  });

  return c.json(result);
});

propertyRoutes.get('/:id', async (c) => {
  const id = c.req.param('id');
  const record = await db.select().from(properties).where(eq(properties.id, id)).get();
  if (!record) {
    return c.json({ error: 'NOT_FOUND', message: 'Propriété non trouvée' }, 404);
  }
  return c.json(record);
});

/* ── POST /api/properties/input — Full formulaire client ── */
propertyRoutes.post('/input', zValidator('json', propertyInputSchema), async (c) => {
  const data = c.req.valid('json');
  const userId = c.get('user')?.sub;

  // Check if property already exists for this client
  const existing = await db.select()
    .from(properties)
    .where(eq(properties.clientId, data.clientId))
    .get();

  if (existing) {
    // UPDATE existing property
    const [updated] = await db.update(properties)
      .set({
        address: data.address,
        postalCode: data.postalCode ?? null,
        city: data.city ?? null,
        typeBien: data.typeBien ?? null,
        surface: data.surface ?? null,
        nbPieces: data.nbPieces ?? null,
        nbEtages: data.nbEtages ?? null,
        anneeConstruction: data.anneeConstruction ?? null,
        anneeRenovation: data.anneeRenovation ?? null,
        typeStructure: data.typeStructure ?? null,
        etatStructure: data.etatStructure ?? null,
        fissures: data.fissures ?? null,
        affaissement: data.affaissement ?? null,
        typeToiture: data.typeToiture ?? null,
        ageToiture: data.ageToiture ?? null,
        anneeToiture: data.anneeToiture ?? null,
        etatToiture: data.etatToiture ?? null,
        isolationToiture: data.isolationToiture ?? null,
        isolationMurs: data.isolationMurs ?? null,
        isolationSol: data.isolationSol ?? null,
        infiltrations: data.infiltrations ?? null,
        presenceSousSol: b(data.presenceSousSol),
        presenceCave: b(data.presenceCave),
        presenceGarage: b(data.presenceGarage),
        occupation: data.occupation ?? null,
        climatisation: b(data.climatisation),
        chauffagePrincipal: data.chauffagePrincipal ?? null,
        installationElectriqueAnnee: data.installationElectriqueAnnee ?? null,
        presenceDetecteursFumee: b(data.presenceDetecteursFumee),
        expositionSolaire: data.expositionSolaire ?? null,
        zoneMitoyennete: data.zoneMitoyennete ?? null,
        hauteurPlancher: data.hauteurPlancher ?? null,
        clapetAntiRetour: b(data.clapetAntiRetour),
        equipementsElecSousSol: b(data.equipementsElecSousSol),
        profondeurFondations: data.profondeurFondations ?? null,
        arbresProches: b(data.arbresProches),
        materiauToit: data.materiauToit ?? null,
        panneauxSolaires: b(data.panneauxSolaires),
        capitalAssure: data.capitalAssure ?? null,
        dpeClass: data.dpeClass ?? null,
        banId: data.banId ?? null,
        longitude: data.longitude ?? null,
        latitude: data.latitude ?? null,
        observations: data.observations ?? null,
        formCompleted: true,
        updatedAt: new Date().toISOString(),
      })
      .where(eq(properties.id, existing.id))
      .returning();
    return c.json(updated, 200);
  }

  // CREATE new property
  const [newProp] = await db.insert(properties).values({
    clientId: data.clientId,
    address: data.address,
    postalCode: data.postalCode ?? null,
    city: data.city ?? null,
    typeBien: data.typeBien ?? null,
    surface: data.surface ?? null,
    nbPieces: data.nbPieces ?? null,
    nbEtages: data.nbEtages ?? null,
    anneeConstruction: data.anneeConstruction ?? null,
    anneeRenovation: data.anneeRenovation ?? null,
    typeStructure: data.typeStructure ?? null,
    etatStructure: data.etatStructure ?? null,
    fissures: data.fissures ?? null,
    affaissement: data.affaissement ?? null,
    typeToiture: data.typeToiture ?? null,
    ageToiture: data.ageToiture ?? null,
    anneeToiture: data.anneeToiture ?? null,
    etatToiture: data.etatToiture ?? null,
    isolationToiture: data.isolationToiture ?? null,
    isolationMurs: data.isolationMurs ?? null,
    isolationSol: data.isolationSol ?? null,
    infiltrations: data.infiltrations ?? null,
    presenceSousSol: b(data.presenceSousSol),
    presenceCave: b(data.presenceCave),
    presenceGarage: b(data.presenceGarage),
    occupation: data.occupation ?? null,
    climatisation: b(data.climatisation),
    chauffagePrincipal: data.chauffagePrincipal ?? null,
    installationElectriqueAnnee: data.installationElectriqueAnnee ?? null,
    presenceDetecteursFumee: b(data.presenceDetecteursFumee),
    expositionSolaire: data.expositionSolaire ?? null,
    zoneMitoyennete: data.zoneMitoyennete ?? null,
    hauteurPlancher: data.hauteurPlancher ?? null,
    clapetAntiRetour: b(data.clapetAntiRetour),
    equipementsElecSousSol: b(data.equipementsElecSousSol),
    profondeurFondations: data.profondeurFondations ?? null,
    arbresProches: b(data.arbresProches),
    materiauToit: data.materiauToit ?? null,
    panneauxSolaires: b(data.panneauxSolaires),
    capitalAssure: data.capitalAssure ?? null,
    dpeClass: data.dpeClass ?? null,
    banId: data.banId ?? null,
    longitude: data.longitude ?? null,
    latitude: data.latitude ?? null,
    observations: data.observations ?? null,
    formCompleted: true,
  }).returning();

  return c.json(newProp, 201);
});



propertyRoutes.delete('/:id', async (c) => {
  const id = c.req.param('id');
  await db.delete(properties).where(eq(properties.id, id));
  return c.json({ success: true });
});
