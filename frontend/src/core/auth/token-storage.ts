/**
 * Stockage des jetons côté web.
 * - accès : en mémoire seulement (durée de vie courte, 15 min) ;
 * - rafraîchissement : sessionStorage (effacé à la fermeture de l'onglet).
 * Voir docs/adr/0003 pour les compromis et l'évolution vers un cookie httpOnly.
 */
const REFRESH_KEY = "hms.refresh";
let access: string | null = null;

export const tokenStorage = {
  getAccess: (): string | null => access,
  getRefresh(): string | null {
    try {
      return sessionStorage.getItem(REFRESH_KEY);
    } catch {
      return null;
    }
  },
  setTokens(accessToken: string, refreshToken: string): void {
    access = accessToken;
    try {
      sessionStorage.setItem(REFRESH_KEY, refreshToken);
    } catch {
      /* stockage indisponible : la session durera le temps de la page */
    }
  },
  clear(): void {
    access = null;
    try {
      sessionStorage.removeItem(REFRESH_KEY);
    } catch {
      /* ignoré */
    }
  },
};
