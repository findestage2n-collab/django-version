import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { tokenStorage } from "@/core/auth/token-storage";
import { API_BASE_URL } from "@/core/config/env";

import { toApiError } from "./errors";

/** Client HTTP unique : tous les appels à l'API passent par lui. */
export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: { "Accept-Language": "fr", "X-Client": "web" },
});

let onAuthFailure: () => void = () => {};
export function setAuthFailureHandler(handler: () => void): void {
  onAuthFailure = handler;
}

let refreshing: Promise<string> | null = null;

async function refreshAccessToken(): Promise<string> {
  const refresh = tokenStorage.getRefresh();
  if (!refresh) throw new Error("Aucun jeton de rafraîchissement");
  // axios « nu » : pas d'intercepteurs, pour éviter toute boucle.
  const { data } = await axios.post<{ access: string; refresh?: string }>(
    `${API_BASE_URL}/auth/refresh/`,
    { refresh },
  );
  tokenStorage.setTokens(data.access, data.refresh ?? refresh);
  return data.access;
}

http.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) config.headers.set("Authorization", `Bearer ${token}`);
  return config;
});

type RetriableConfig = InternalAxiosRequestConfig & { _retried?: boolean };

http.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const isAuthCall = original?.url?.startsWith("/auth/") ?? false;
    if (
      error.response?.status === 401 &&
      original &&
      !original._retried &&
      !isAuthCall &&
      tokenStorage.getRefresh()
    ) {
      original._retried = true;
      try {
        // « single-flight » : une seule requête de rafraîchissement même si plusieurs échouent.
        refreshing ??= refreshAccessToken().finally(() => {
          refreshing = null;
        });
        const token = await refreshing;
        original.headers.set("Authorization", `Bearer ${token}`);
        return http(original);
      } catch {
        tokenStorage.clear();
        onAuthFailure();
      }
    }
    return Promise.reject(toApiError(error));
  },
);
