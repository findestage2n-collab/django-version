import type { Schemas } from "@/core/api/types";

export type Patient = Schemas["PatientDetail"];
export type PatientListItem = Schemas["PatientList"];
export type PatientInput = Schemas["PatientWriteRequest"];

export interface PatientListParams {
  page?: number;
  page_size?: number;
  q?: string;
  sexe?: "M" | "F";
  ordering?: string;
}
