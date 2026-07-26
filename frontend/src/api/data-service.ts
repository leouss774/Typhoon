/**
 * Data Service — loads data from backend API with fallback to mock DataStore.
 *
 * All views should use this service instead of directly calling data.ts or
 * hardcoding mock data.
 */

import { store } from '../data.js';
import type { Client, Property, Assessment } from '../data.js';

/* ── Cache ───────────────────────────────────────────── */

let clientsCache: Client[] | null = null;
let propertiesCache: Property[] | null = null;
let assessmentsCache: Assessment[] | null = null;
let apiAvailable = true;

/* ── API availability check ────────────────────────── */

export function isApiAvailable(): boolean {
  return apiAvailable;
}

function markApiUnavailable(): void {
  apiAvailable = false;
}

/* ── Helpers ─────────────────────────────────────────── */

function mapApiClientToClient(api: any): Client {
  return {
    id: api.id,
    civility: api.civility || 'M.',
    firstName: api.firstName,
    lastName: api.lastName,
    dateOfBirth: '',
    nationality: '',
    email: api.email || '',
    phone: api.phone || '',
    profession: '',
    avatar: (api.firstName?.[0] || '') + (api.lastName?.[0] || ''),
    status: api.status || 'active',
    insuredAddress: api.insuredAddress || '',
    insuredAddressComplement: '',
    insuredPostalCode: api.insuredPostalCode || '',
    insuredCity: api.insuredCity || '',
    correspondenceAddress: '',
    correspondencePostalCode: '',
    correspondenceCity: '',
    contractType: 'mrh',
    contractTypeLabel: '',
    policyNumber: '',
    clientRef: api.id?.substring(0, 8) || '',
    effectiveDate: '',
    expiryDate: '',
    annualPremium: 0,
    paymentFrequency: 'annuel',
    depositGuarantee: 0,
    paymentMethod: 'prelevement',
    iban: '',
    bic: '',
    ribDeposited: false,
    identityDeposited: false,
    sepaMandateStatus: 'pending',
    propertyIds: api.properties?.map((p: any) => p.id) || [],
    assessmentIds: [],
  };
}

function mapApiPropertyToProperty(api: any): Property {
  return {
    id: api.id,
    address: api.address || '',
    addressShort: api.address?.split(',')[0] || '',
    city: api.city || '',
    clientId: api.clientId || '',
    riskScore: 0,
    riskLevel: 'low',
    dpeClass: api.dpeClass || '',
    builtYear: api.anneeConstruction || 0,
    assessmentIds: [],
  };
}

/* ── Load all data ───────────────────────────────────── */

export async function loadAllData(): Promise<void> {
  try {
    const [clientsRes, propsRes] = await Promise.all([
      fetch('/api/clients').then(r => r.ok ? r.json() : Promise.reject('API unavailable')),
      fetch('/api/properties').then(r => r.ok ? r.json() : Promise.reject('API unavailable')),
    ]);

    clientsCache = (clientsRes as any[]).map(mapApiClientToClient);
    propertiesCache = (propsRes as any[]).map(mapApiPropertyToProperty);
    apiAvailable = true;
  } catch {
    // API unavailable — fall back to mock store
    console.warn('[DataService] API unavailable, using mock DataStore');
    apiAvailable = false;
    clientsCache = null;
    propertiesCache = null;
  }
}

/* ── Clients ─────────────────────────────────────────── */

export async function fetchClientsFromApi(): Promise<Client[]> {
  if (clientsCache) return clientsCache;

  try {
    const res = await fetch('/api/clients');
    if (!res.ok) throw new Error('API unavailable');
    const data = await res.json();
    clientsCache = data.map(mapApiClientToClient);
    apiAvailable = true;
    return clientsCache;
  } catch {
    markApiUnavailable();
    return store.getAllClients();
  }
}

export function getCachedClients(): Client[] {
  return clientsCache || store.getAllClients();
}

export function getCachedClient(id: string): Client | undefined {
  if (clientsCache) return clientsCache.find(c => c.id === id);
  return store.getClient(id);
}

/* ── Properties ──────────────────────────────────────── */

export async function fetchPropertiesFromApi(): Promise<Property[]> {
  if (propertiesCache) return propertiesCache;

  try {
    const res = await fetch('/api/properties');
    if (!res.ok) throw new Error('API unavailable');
    const data = await res.json();
    propertiesCache = data.map(mapApiPropertyToProperty);
    apiAvailable = true;
    return propertiesCache;
  } catch {
    markApiUnavailable();
    return store.getAllProperties();
  }
}

export function getCachedProperties(): Property[] {
  return propertiesCache || store.getAllProperties();
}

export function getCachedClientProperties(clientId: string): Property[] {
  if (propertiesCache) return propertiesCache.filter(p => p.clientId === clientId);
  return store.getClientProperties(clientId);
}

/* ── Assessments ─────────────────────────────────────── */

export async function fetchAssessmentsFromApi(): Promise<Assessment[]> {
  try {
    const res = await fetch('/api/assessments');
    if (!res.ok) throw new Error('API unavailable');
    return await res.json();
  } catch {
    return store.getAllAssessments();
  }
}

/* ── Assessment Stats (dashboard) ────────────────────── */

export interface AssessmentStats {
  total: number;
  nouveau: number;
  enCours: number;
  evalue: number;
  recent: Array<{
    id: string;
    addressLabel: string;
    globalScore: number | null;
    status: string | null;
    createdAt: string;
  }>;
}

export async function fetchAssessmentStats(): Promise<AssessmentStats> {
  try {
    const res = await fetch('/api/assessments/stats');
    if (!res.ok) throw new Error('API unavailable');
    return await res.json();
  } catch {
    // Fallback: use mock store directly (skip extra fetch that will also fail)
    const all = store.getAllAssessments();
    return {
      total: all.length,
      nouveau: all.filter(a => a.status === 'nouveau').length,
      enCours: all.filter(a => ['en_localisation', 'en_expertise', 'en_inspection'].includes(a.status || '')).length,
      evalue: all.filter(a => a.status === 'evalue').length,
      recent: all.slice(0, 10).map(a => ({
        id: a.id || '',
        addressLabel: a.address || '',
        globalScore: (a as any).globalScore || null,
        status: a.status || null,
        createdAt: a.createdAt || '',
      })),
    };
  }
}

/* ── Pending Submissions ─────────────────────────────── */

export interface PendingSubmission {
  id: string;
  clientId: string;
  clientName: string;
  address: string;
  city: string;
  createdAt: string;
  propertyType: string;
}

export async function fetchPendingSubmissions(): Promise<PendingSubmission[]> {
  try {
    // Try dedicated backend endpoint first
    const res = await fetch('/api/properties/pending');
    if (res.ok) {
      return await res.json();
    }
  } catch {}

  // Fallback: client-side computation
  try {
    const [propsRes, clients] = await Promise.all([
      fetch('/api/properties').then(r => r.ok ? r.json() : Promise.reject('API unavailable')),
      fetchClientsFromApi(),
    ]);
    const props = (propsRes as any[]) || [];

    const assessments = await fetchAssessmentsFromApi();
    const assessedPropertyIds = new Set(assessments.map(a => (a as any).propertyId).filter(Boolean));

    const clientMap = new Map(clients.map(c => [c.id, c]));
    const pending: PendingSubmission[] = [];
    for (const p of props) {
      if (p.formCompleted && !assessedPropertyIds.has(p.id)) {
        const client = clientMap.get(p.clientId);
        pending.push({
          id: p.id,
          clientId: p.clientId,
          clientName: client ? `${client.firstName} ${client.lastName}` : 'Client inconnu',
          address: p.address || '',
          city: p.city || '',
          createdAt: p.createdAt || '',
          propertyType: p.typeBien || 'Non renseigné',
        });
      }
    }

    return pending;
  } catch {
    return [];
  }
}

/* ── Update sidebar badge globally ─────────────────── */

export async function refreshSidebarBadge(): Promise<void> {
  try {
    const pending = await fetchPendingSubmissions();
    const count = pending.length;
    const badge = document.getElementById('clientNotificationBadge');
    if (!badge) return;
    if (count > 0) {
      badge.style.display = 'flex';
      badge.textContent = String(count > 99 ? '99+' : count);
    } else {
      badge.style.display = 'none';
    }
  } catch {
    // Silent
  }
}

/* ── Dashboard Stats ─────────────────────────────────── */

export interface DashboardStats {
  totalClients: number;
  activeClients: number;
  pendingClients: number;
  totalProperties: number;
  totalAssessments: number;
  avgScore: number;
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const clients = await fetchClientsFromApi();
  const properties = await fetchPropertiesFromApi();
  const assessments = await fetchAssessmentsFromApi();

  return {
    totalClients: clients.length,
    activeClients: clients.filter(c => c.status === 'active').length,
    pendingClients: clients.filter(c => c.status === 'pending').length,
    totalProperties: properties.length,
    totalAssessments: assessments.length,
    avgScore: assessments.length > 0
      ? Math.round(assessments.reduce((s, a) => s + ((a as any).globalScore || (a as any).score || 0), 0) / assessments.length)
      : 0,
  };
}
