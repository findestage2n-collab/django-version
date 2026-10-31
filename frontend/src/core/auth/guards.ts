import type { Router } from "vue-router";

import { useAuthStore } from "./auth.store";

declare module "vue-router" {
  interface RouteMeta {
    /** La route exige une session (vrai par défaut, faux pour /login). */
    public?: boolean;
    /** Permission Django requise, ex. "patients.view_patient". */
    permission?: string;
  }
}

export function installAuthGuard(router: Router): void {
  router.beforeEach(async (to) => {
    const auth = useAuthStore();
    await auth.restoreSession();

    if (to.meta.public) {
      return auth.isAuthenticated && to.name === "login" ? { name: "dashboard" } : true;
    }
    if (!auth.isAuthenticated) {
      return { name: "login", query: { redirect: to.fullPath } };
    }
    if (to.meta.permission && !auth.can(to.meta.permission)) {
      return { name: "dashboard" };
    }
    return true;
  });
}
