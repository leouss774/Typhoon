import { apiFetch } from './client.js';
export interface AssessRequest {
  latitude: number;
  longitude: number;
  address: string;
  banId?: string;
  communeCode?: string;
  communeName?: string;
  departmentCode?: string;
  propertyId?: string;
}

export interface AssessResponse {
  assessmentId: string;
  scores: {
    inondation: number;
    rga: number;
    tempete: number;
    incendie: number;
    seisme: number;
    global: number;
  };
  [key: string]: any;
}

export async function runAssessment(params: AssessRequest): Promise<AssessResponse> {
  return apiFetch<AssessResponse>('/api/risk/assess', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}
