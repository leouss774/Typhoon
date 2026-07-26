import { apiFetch } from './client.js';
export interface ClientRecord {
  id: string;
  firstName: string;
  lastName: string;
  email?: string | null;
  phone?: string | null;
  insuredAddress?: string | null;
  insuredPostalCode?: string | null;
  insuredCity?: string | null;
  status: 'active' | 'pending' | 'suspended';
  createdAt: string;
}

export type CreateClientRequest = Partial<ClientRecord>;
export type UpdateClientRequest = Partial<ClientRecord>;

export async function fetchClients(): Promise<ClientRecord[]> {
  return apiFetch<ClientRecord[]>('/api/clients');
}

export async function fetchClientById(id: string): Promise<ClientRecord & { properties?: any[] }> {
  return apiFetch<ClientRecord & { properties?: any[] }>(`/api/clients/${id}`);
}

export async function createClient(data: CreateClientRequest): Promise<ClientRecord> {
  return apiFetch<ClientRecord>('/api/clients', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function updateClient(id: string, data: UpdateClientRequest): Promise<ClientRecord> {
  return apiFetch<ClientRecord>(`/api/clients/${id}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function deleteClient(id: string): Promise<{ success: boolean }> {
  return apiFetch<{ success: boolean }>(`/api/clients/${id}`, {
    method: 'DELETE',
  });
}
