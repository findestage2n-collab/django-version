import { defineStore } from "pinia";
import { computed, ref } from "vue";

import { authApi, type AuthUser } from "./auth.api";
import { tokenStorage } from "./token-storage";

export const useAuthStore = defineStore("auth", () => {
  const user = ref<AuthUser | null>(null);
  const ready = ref(false);

  const isAuthenticated = computed(() => user.value !== null);
  const permissions = computed(() => new Set(user.value?.permissions ?? []));

  /** Affichage conditionnel uniquement : le serveur reste l'autorité sur chaque endpoint. */
  function can(permission: string): boolean {
    return permissions.value.has(permission);
  }

  async function login(username: string, password: string): Promise<void> {
    const data = await authApi.login(username, password);
    tokenStorage.setTokens(data.access, data.refresh);
    user.value = data.user;
  }

  async function restoreSession(): Promise<void> {
    if (ready.value) return;
    try {
      if (tokenStorage.getRefresh()) user.value = await authApi.me();
    } catch {
      reset();
    } finally {
      ready.value = true;
    }
  }

  async function logout(): Promise<void> {
    const refresh = tokenStorage.getRefresh();
    try {
      if (refresh) await authApi.logout(refresh);
    } finally {
      reset();
    }
  }

  function reset(): void {
    tokenStorage.clear();
    user.value = null;
  }

  return { user, ready, isAuthenticated, can, login, logout, restoreSession, reset };
});
