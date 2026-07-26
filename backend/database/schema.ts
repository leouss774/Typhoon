/**
 * Database schema — Drizzle ORM (SQLite via libSQL)
 */
import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';
import { randomUUID } from 'node:crypto';

const uuid = () => randomUUID();
const now = () => new Date().toISOString();

/* ─────────────── Users ─────────────── */

export const users = sqliteTable('users', {
  id: text('id').primaryKey().$defaultFn(uuid),
  email: text('email').notNull().unique(),
  passwordHash: text('password_hash').notNull(),
  role: text('role', { enum: ['assureur', 'assure'] }).notNull().default('assureur'),
  firstName: text('first_name').notNull(),
  lastName: text('last_name').notNull(),
  createdAt: text('created_at').notNull().$defaultFn(now),
  updatedAt: text('updated_at').notNull().$defaultFn(now),
});

/* ─────────────── Clients ─────────────── */

export const clients = sqliteTable('clients', {
  id: text('id').primaryKey().$defaultFn(uuid),
  userId: text('user_id')
    .references(() => users.id, { onDelete: 'cascade' })
    .notNull(),
  civility: text('civility'),
  firstName: text('first_name').notNull(),
  lastName: text('last_name').notNull(),
  email: text('email'),
  phone: text('phone'),
  insuredAddress: text('insured_address'),
  insuredPostalCode: text('insured_postal_code'),
  insuredCity: text('insured_city'),
  status: text('status', { enum: ['active', 'pending', 'suspended'] }).notNull().default('active'),
  createdAt: text('created_at').notNull().$defaultFn(now),
});

/* ─────────────── Properties ─────────────── */

export const properties = sqliteTable('properties', {
  id: text('id').primaryKey().$defaultFn(uuid),
  clientId: text('client_id')
    .references(() => clients.id, { onDelete: 'cascade' })
    .notNull(),

  // Adresse
  address: text('address').notNull(),
  postalCode: text('postal_code'),
  city: text('city'),

  // Général
  typeBien: text('type_bien', { enum: ['maison', 'appartement', 'immeuble', 'local_commercial', 'autre'] }),
  surface: real('surface'),
  nbPieces: integer('nb_pieces'),
  nbEtages: integer('nb_etages'),
  anneeConstruction: integer('annee_construction'),
  anneeRenovation: integer('annee_renovation'),

  // Structure
  typeStructure: text('type_structure', { enum: ['Béton armé', 'Pierre', 'Brique', 'Bois', 'Métal', 'Mixte', 'Autre'] }),
  etatStructure: text('etat_structure', { enum: ['Neuf', 'Bon', 'Moyen', 'Médiocre', 'Vétuste'] }),
  fissures: text('fissures', { enum: ['Aucune', 'Légères', 'Moyennes', 'Importantes', 'Structurelles'] }),
  affaissement: text('affaissement', { enum: ['non', 'leger', 'visible', 'important'] }),

  // Toiture & Isolation
  typeToiture: text('type_toiture', { enum: ['Tuiles', 'Ardoises', 'Zinc', 'Bac acier', 'Béton', 'Végétalisée', 'Autre'] }),
  ageToiture: integer('age_toiture'),
  anneeToiture: integer('annee_toiture'),
  etatToiture: text('etat_toiture', { enum: ['Neuf', 'Bon', 'Moyen', 'Médiocre', 'Vétuste'] }),
  isolationToiture: text('isolation_toiture', { enum: ['neuve', 'bonne', 'moyenne', 'faible', 'absente'] }),
  isolationMurs: text('isolation_murs', { enum: ['neuve', 'bonne', 'moyenne', 'faible', 'absente'] }),
  isolationSol: text('isolation_sol', { enum: ['neuve', 'bonne', 'moyenne', 'faible', 'absente'] }),
  infiltrations: text('infiltrations', { enum: ['Non', 'Occasionnelles', 'Récurrentes', 'Permanentes'] }),

  // Sous-sol & Équipements
  presenceSousSol: integer('presence_sous_sol', { mode: 'boolean' }),
  presenceCave: integer('presence_cave', { mode: 'boolean' }),
  presenceGarage: integer('presence_garage', { mode: 'boolean' }),
  occupation: text('occupation', { enum: ['Occupé', 'Vacant', 'Loué', 'Secondaire'] }),
  climatisation: integer('climatisation', { mode: 'boolean' }),
  chauffagePrincipal: text('chauffage_principal', { enum: ['Électrique', 'Gaz', 'Fioul', 'Bois', 'Pompe à chaleur', 'Réseau de chaleur', 'Solaire', 'Autre'] }),

  // Électricité & Sécurité
  installationElectriqueAnnee: integer('installation_electrique_annee'),
  presenceDetecteursFumee: integer('presence_detecteurs_fumee', { mode: 'boolean' }),

  // Exposition & Environnement
  expositionSolaire: text('exposition_solaire', { enum: ['Faible', 'Moyenne', 'Forte', 'Très forte'] }),
  zoneMitoyennete: text('zone_mitoyennete', { enum: ['Isolé', 'Mitoyen d\'un côté', 'Mitoyen des deux côtés', 'En bande'] }),

  // Inondation
  hauteurPlancher: real('hauteur_plancher'),
  clapetAntiRetour: integer('clapet_anti_retour', { mode: 'boolean' }),
  equipementsElecSousSol: integer('equipements_elec_sous_sol', { mode: 'boolean' }),

  // RGA
  profondeurFondations: text('profondeur_fondations', { enum: ['Moins de 50 cm', '50 à 80 cm', 'Plus de 80 cm', 'Non connu'] }),
  arbresProches: integer('arbres_proches', { mode: 'boolean' }),
  materiauToit: text('materiau_toit', { enum: ['Tuiles canal', 'Tuiles mécaniques', 'Ardoises naturelles', 'Ardoises synthétiques', 'Zinc', 'Bac acier', 'Shingle', 'Béton', 'Autre'] }),
  panneauxSolaires: integer('panneaux_solaires', { mode: 'boolean' }),

  // Assurantiel
  capitalAssure: real('capital_assure'),

  // État DPE & BDNB
  dpeClass: text('dpe_class'),
  builtYear: integer('built_year'),
  banId: text('ban_id'),
  longitude: real('longitude'),
  latitude: real('latitude'),

  // Observations libres
  observations: text('observations'),

  // Form status
  formCompleted: integer('form_completed', { mode: 'boolean' }).default(false),
  createdAt: text('created_at').notNull().$defaultFn(now),
  updatedAt: text('updated_at').notNull().$defaultFn(now),
});

/* ─────────────── Assessments ─────────────── */

export const assessments = sqliteTable('assessments', {
  id: text('id').primaryKey().$defaultFn(uuid),
  propertyId: text('property_id').references(() => properties.id),
  userId: text('user_id').references(() => users.id),
  addressLabel: text('address_label').notNull(),
  longitude: real('longitude').notNull(),
  latitude: real('latitude').notNull(),
  // Workflow status
  status: text('status', {
    enum: ['nouveau', 'en_localisation', 'en_expertise', 'en_inspection', 'evalue'],
  }).notNull().default('nouveau'),
  // Raw API snapshots (JSON strings — immutable after creation)
  buildingData: text('building_data'),
  geographyData: text('geography_data'),
  risksData: text('risks_data'),
  climateData: text('climate_data'),
  valuationData: text('valuation_data'),
  metadataData: text('metadata_data'),
  // Individual peril scores — queryable/indexable columns
  inondationScore: integer('inondation_score'),
  rgaScore: integer('rga_score'),
  tempeteScore: integer('tempete_score'),
  incendieScore: integer('incendie_score'),
  seismeScore: integer('seisme_score'),
  globalScore: integer('global_score'),
  createdAt: text('created_at').notNull().$defaultFn(now),
  updatedAt: text('updated_at').notNull().$defaultFn(now),
});

/* ─────────────── Expert Forms ─────────────── */

export const expertForms = sqliteTable('expert_forms', {
  id: text('id').primaryKey().$defaultFn(uuid),
  assessmentId: text('assessment_id')
    .references(() => assessments.id, { onDelete: 'cascade' })
    .notNull(),
  // All form fields as JSON (15-field actuarial form)
  fields: text('fields').notNull(), // JSON string
  // Recommendations entered/computed by expert
  recommendations: text('recommendations'), // JSON string array
  createdAt: text('created_at').notNull().$defaultFn(now),
  updatedAt: text('updated_at').notNull().$defaultFn(now),
});

/* ─────────────── Evaluation Reports ─────────────── */

export const evaluationReports = sqliteTable('evaluation_reports', {
  id: text('id').primaryKey().$defaultFn(uuid),
  assessmentId: text('assessment_id')
    .references(() => assessments.id, { onDelete: 'cascade' })
    .notNull(),
  // Deterministic scores (computed locally)
  globalScore: integer('global_score'),
  subScores: text('sub_scores'), // JSON: { inondation, rga, tempete, incendie, seisme }
  // Mistral-generated report content (JSON)
  reportContent: text('report_content'), // JSON: { resume, pointsVigilance, recommandations, syntheseTexte, niveauRisque }
  generatedAt: text('generated_at').notNull().$defaultFn(now),
});

/* ─────────────── Documents ─────────────── */

export const documents = sqliteTable('documents', {
  id: text('id').primaryKey().$defaultFn(uuid),
  clientId: text('client_id')
    .references(() => clients.id, { onDelete: 'cascade' })
    .notNull(),
  name: text('name').notNull(),
  type: text('type', {
    enum: ['contrat', 'cni', 'rib', 'mandat', 'photo', 'facture', 'autre'],
  }).notNull(),
  url: text('url').notNull(),
  sizeBytes: integer('size_bytes'),
  status: text('status', { enum: ['complete', 'pending'] }).default('pending'),
  uploadedAt: text('uploaded_at').notNull().$defaultFn(now),
});

/* ─────────────── Inferred Types ─────────────── */

export type User = typeof users.$inferSelect;
export type NewUser = typeof users.$inferInsert;
export type Client = typeof clients.$inferSelect;
export type NewClient = typeof clients.$inferInsert;
export type Property = typeof properties.$inferSelect;
export type NewProperty = typeof properties.$inferInsert;
export type Assessment = typeof assessments.$inferSelect;
export type NewAssessment = typeof assessments.$inferInsert;
export type ExpertForm = typeof expertForms.$inferSelect;
export type NewExpertForm = typeof expertForms.$inferInsert;
export type EvaluationReport = typeof evaluationReports.$inferSelect;
export type NewEvaluationReport = typeof evaluationReports.$inferInsert;
export type Document = typeof documents.$inferSelect;
export type NewDocument = typeof documents.$inferInsert;
