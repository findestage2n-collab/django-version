import { http } from "@/core/api/http";
import type { Paginated } from "@/core/api/types";

import type { Patient, PatientInput, PatientListItem, PatientListParams } from "../types";

const BASE = "/patients/";

export const patientsApi = {
  async list(params: PatientListParams = {}): Promise<Paginated<PatientListItem>> {
    const { data } = await http.get<Paginated<PatientListItem>>(BASE, { params });
    return data;
  },
  async get(id: string): Promise<Patient> {
    const { data } = await http.get<Patient>(`${BASE}${id}/`);
    return data;
  },
  async create(input: PatientInput): Promise<Patient> {
    const { data } = await http.post<Patient>(BASE, input);
    return data;
  },
  async update(id: string, input: Partial<PatientInput>): Promise<Patient> {
    const { data } = await http.patch<Patient>(`${BASE}${id}/`, input);
    return data;
  },
  async archive(id: string): Promise<void> {
    await http.delete(`${BASE}${id}/`);
  },
};
