import { createPinia, setActivePinia } from "pinia";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { authApi } from "./auth.api";
import { useAuthStore } from "./auth.store";
import { tokenStorage } from "./token-storage";

vi.mock("./auth.api", () => ({ authApi: { login: vi.fn(), me: vi.fn(), logout: vi.fn() } }));

const user = {
  public_id: "1",
  username: "amina",
  first_name: "",
  last_name: "",
  email: "",
  telephone: "",
  roles: ["SECRETAIRE"],
  permissions: ["patients.view_patient"],
};

describe("auth store", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    tokenStorage.clear();
    vi.resetAllMocks();
  });

  it("connecte l'utilisateur et expose ses droits", async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access: "a", refresh: "r", user });
    const auth = useAuthStore();
    await auth.login("amina", "x");
    expect(auth.isAuthenticated).toBe(true);
    expect(auth.can("patients.view_patient")).toBe(true);
    expect(auth.can("patients.delete_patient")).toBe(false);
    expect(tokenStorage.getAccess()).toBe("a");
  });

  it("se déconnecte même si le serveur échoue", async () => {
    vi.mocked(authApi.login).mockResolvedValue({ access: "a", refresh: "r", user });
    vi.mocked(authApi.logout).mockRejectedValue(new Error("réseau"));
    const auth = useAuthStore();
    await auth.login("amina", "x");
    await auth.logout().catch(() => undefined);
    expect(auth.isAuthenticated).toBe(false);
    expect(tokenStorage.getRefresh()).toBeNull();
  });
});
