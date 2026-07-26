/**
 * Database seed — populates the SQLite database with demo data
 *
 * Usage: npm run db:seed
 * Or:    tsx database/seed.ts
 */
import { db } from './client.js';
import { users, clients, properties, assessments, documents } from './schema.js';
import bcrypt from 'bcryptjs';
import { randomUUID } from 'node:crypto';

const uuid = () => randomUUID();
const now = () => new Date().toISOString();

async function seed(): Promise<void> {
  console.log('🌱 Seeding database...');

  // ── Clear existing data ──
  await db.delete(assessments);
  await db.delete(documents);
  await db.delete(properties);
  await db.delete(clients);
  await db.delete(users);
  console.log('  ✓ Cleared existing data');

  // ── Users ──
  const passwordHash = await bcrypt.hash('password123', 10);
  console.log('  (using bcrypt async hash)');

  const userIds = {
    assureur: uuid(),
    assure: uuid(),
    admin: uuid(),
  };

  await db.insert(users).values([
    {
      id: userIds.assureur,
      email: 'assureur@previa.fr',
      passwordHash,
      role: 'assureur',
      firstName: 'Jean',
      lastName: 'Dupont',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: userIds.assure,
      email: 'assure@previa.fr',
      passwordHash,
      role: 'assure',
      firstName: 'Marie',
      lastName: 'Martin',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: userIds.admin,
      email: 'admin@previa.fr',
      passwordHash,
      role: 'assureur',
      firstName: 'Admin',
      lastName: 'Prévia',
      createdAt: now(),
      updatedAt: now(),
    },
  ]);
  console.log('  ✓ Users created (password: password123)');

  // ── Clients (6 clients from data.ts) ──
  const clientIds = {
    c1: uuid(),
    c2: uuid(),
    c3: uuid(),
    c4: uuid(),
    c5: uuid(),
    c6: uuid(),
  };

  await db.insert(clients).values([
    {
      id: clientIds.c1,
      userId: userIds.assureur,
      civility: 'M.',
      firstName: 'Jean',
      lastName: 'Dupont',
      email: 'jean.dupont@email.fr',
      phone: '+33 6 12 34 56 78',
      insuredAddress: '8 Rue de la Paix',
      insuredPostalCode: '75002',
      insuredCity: 'Paris',
      status: 'active',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: clientIds.c2,
      userId: userIds.assureur,
      civility: 'Mme',
      firstName: 'Marie',
      lastName: 'Bernard',
      email: 'marie.bernard@email.fr',
      phone: '+33 6 98 76 54 32',
      insuredAddress: '15 Bd Haussmann',
      insuredPostalCode: '75009',
      insuredCity: 'Paris',
      status: 'active',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: clientIds.c3,
      userId: userIds.assureur,
      civility: 'M.',
      firstName: 'Pierre',
      lastName: 'Lefèvre',
      email: 'pierre.lefevre@email.fr',
      phone: '+33 6 45 67 89 01',
      insuredAddress: '34 Rue de Rivoli',
      insuredPostalCode: '75004',
      insuredCity: 'Paris',
      status: 'pending',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: clientIds.c4,
      userId: userIds.assureur,
      civility: 'Mme',
      firstName: 'Sophie',
      lastName: 'Nguyen',
      email: 'sophie.nguyen@email.fr',
      phone: '+33 6 23 45 67 89',
      insuredAddress: '5 Rue de Rennes',
      insuredPostalCode: '33000',
      insuredCity: 'Bordeaux',
      status: 'active',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: clientIds.c5,
      userId: userIds.assureur,
      civility: 'M.',
      firstName: 'Lucas',
      lastName: 'Richard',
      email: 'lucas.richard@email.fr',
      phone: '+33 6 34 56 78 90',
      insuredAddress: '12 Rue Matabiau',
      insuredPostalCode: '31000',
      insuredCity: 'Toulouse',
      status: 'suspended',
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: clientIds.c6,
      userId: userIds.assureur,
      civility: 'Mme',
      firstName: 'Claire',
      lastName: 'Petit',
      email: 'claire.petit@email.fr',
      phone: '+33 6 56 78 90 12',
      insuredAddress: '7 Rue du Bac',
      insuredPostalCode: '59000',
      insuredCity: 'Lille',
      status: 'pending',
      createdAt: now(),
      updatedAt: now(),
    },
  ]);
  console.log('  ✓ 6 clients created');

  // ── Properties (8 properties from data.ts) ──
  const propertyIds = {
    p1: uuid(),
    p2: uuid(),
    p3: uuid(),
    p4: uuid(),
    p5: uuid(),
    p6: uuid(),
    p7: uuid(),
    p8: uuid(),
  };

  await db.insert(properties).values([
    {
      id: propertyIds.p1,
      clientId: clientIds.c1,
      address: '8 Rue de la Paix, 75002 Paris',
      postalCode: '75002',
      city: 'Paris',
      typeBien: 'maison',
      nbPieces: 5,
      anneeConstruction: 1978,
      dpeClass: 'D',
      banId: '75102_6998_00008',
      longitude: 2.330992,
      latitude: 48.868831,
      formCompleted: true,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p2,
      clientId: clientIds.c2,
      address: '15 Bd Haussmann, 75009 Paris',
      postalCode: '75009',
      city: 'Paris',
      typeBien: 'appartement',
      nbPieces: 3,
      anneeConstruction: 1985,
      dpeClass: 'C',
      longitude: 2.332,
      latitude: 48.871,
      formCompleted: true,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p3,
      clientId: clientIds.c3,
      address: '2 Place de la Bourse, 69002 Lyon',
      postalCode: '69002',
      city: 'Lyon',
      typeBien: 'appartement',
      nbPieces: 4,
      anneeConstruction: 2005,
      dpeClass: 'A',
      longitude: 4.842,
      latitude: 45.764,
      formCompleted: true,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p4,
      clientId: clientIds.c1,
      address: '12 Av. Champs-Élysées, 75008 Paris',
      postalCode: '75008',
      city: 'Paris',
      typeBien: 'appartement',
      nbPieces: 6,
      anneeConstruction: 1965,
      dpeClass: 'E',
      longitude: 2.311,
      latitude: 48.870,
      formCompleted: false,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p5,
      clientId: clientIds.c2,
      address: '5 Rue de Rennes, 75006 Paris',
      postalCode: '75006',
      city: 'Paris',
      typeBien: 'appartement',
      nbPieces: 3,
      anneeConstruction: 1990,
      dpeClass: 'D',
      longitude: 2.326,
      latitude: 48.852,
      formCompleted: false,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p6,
      clientId: clientIds.c3,
      address: '34 Rue de Rivoli, 75004 Paris',
      postalCode: '75004',
      city: 'Paris',
      typeBien: 'immeuble',
      nbPieces: 8,
      anneeConstruction: 1960,
      dpeClass: 'E',
      longitude: 2.356,
      latitude: 48.857,
      formCompleted: false,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p7,
      clientId: clientIds.c1,
      address: '18 Rue Lafayette, 75009 Paris',
      postalCode: '75009',
      city: 'Paris',
      typeBien: 'appartement',
      nbPieces: 2,
      anneeConstruction: 2015,
      dpeClass: 'B',
      longitude: 2.345,
      latitude: 48.878,
      formCompleted: false,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: propertyIds.p8,
      clientId: clientIds.c2,
      address: '7 Rue du Bac, 75007 Paris',
      postalCode: '75007',
      city: 'Paris',
      typeBien: 'appartement',
      nbPieces: 4,
      anneeConstruction: 1975,
      dpeClass: 'D',
      longitude: 2.320,
      latitude: 48.858,
      formCompleted: false,
      createdAt: now(),
      updatedAt: now(),
    },
  ]);
  console.log('  ✓ 8 properties created');

  // ── Assessments (3 completed from data.ts) ──
  await db.insert(assessments).values([
    {
      id: uuid(),
      propertyId: propertyIds.p1,
      userId: userIds.assureur,
      addressLabel: '8 Rue de la Paix, 75002 Paris',
      longitude: 2.330992,
      latitude: 48.868831,
      status: 'evalue',
      globalScore: 66,
      inondationScore: 60,
      rgaScore: 72,
      tempeteScore: 30,
      incendieScore: 15,
      seismeScore: 10,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: uuid(),
      propertyId: propertyIds.p2,
      userId: userIds.assureur,
      addressLabel: '15 Bd Haussmann, 75009 Paris',
      longitude: 2.332,
      latitude: 48.871,
      status: 'evalue',
      globalScore: 48,
      inondationScore: 10,
      rgaScore: 55,
      tempeteScore: 25,
      incendieScore: 10,
      seismeScore: 5,
      createdAt: now(),
      updatedAt: now(),
    },
    {
      id: uuid(),
      propertyId: propertyIds.p6,
      userId: userIds.assureur,
      addressLabel: '34 Rue de Rivoli, 75004 Paris',
      longitude: 2.356,
      latitude: 48.857,
      status: 'evalue',
      globalScore: 81,
      inondationScore: 85,
      rgaScore: 90,
      tempeteScore: 45,
      incendieScore: 30,
      seismeScore: 20,
      createdAt: now(),
      updatedAt: now(),
    },
  ]);
  console.log('  ✓ 3 assessments created');

  console.log('✅ Database seeded successfully!');
  console.log('');
  console.log('Users:');
  console.log('  assureur@previa.fr / password123  →  role: assureur');
  console.log('  assure@previa.fr / password123    →  role: assure');
  console.log('  admin@previa.fr / password123     →  role: assureur');
  console.log('');
  console.log('Login via POST /api/auth/login');
}

seed()
  .catch((err) => {
    console.error('❌ Seed failed:', err);
    process.exit(1);
  })
  .then(() => process.exit(0));
