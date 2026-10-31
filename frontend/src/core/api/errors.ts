import axios from "axios";

import type { ApiErrorBody } from "./types";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly details?: Record<string, string[]>,
    readonly requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }

  /** Première erreur de chaque champ, prête à afficher sous les inputs. */
  fieldErrors(): Record<string, string> {
    const out: Record<string, string> = {};
    for (const [field, messages] of Object.entries(this.details ?? {})) {
      if (messages[0]) out[field] = messages[0];
    }
    return out;
  }
}

export function toApiError(error: unknown): ApiError {
  if (error instanceof ApiError) return error;
  if (axios.isAxiosError(error)) {
    const body = error.response?.data as ApiErrorBody | undefined;
    if (body?.error) {
      return new ApiError(
        error.response?.status ?? 0,
        body.error.code,
        body.error.message,
        body.error.details,
        body.request_id,
      );
    }
    if (!error.response) return new ApiError(0, "network_error", "Serveur injoignable.");
    return new ApiError(error.response.status, "http_error", error.message);
  }
  return new ApiError(0, "unknown_error", String(error));
}
