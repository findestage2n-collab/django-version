import type { components } from "./schema";

export type Schemas = components["schemas"];

/** Enveloppe de pagination commune à tous les endpoints de liste (web et mobile). */
export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

/** Format d'erreur unique renvoyé par le backend. */
export interface ApiErrorBody {
  error: { code: string; message: string; details?: Record<string, string[]> };
  request_id?: string;
}
