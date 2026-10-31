import { http } from "@/core/api/http";
import type { Schemas } from "@/core/api/types";

export type AuthUser = Schemas["UserSummary"];
export type LoginResponse = Schemas["LoginResponse"];

export const authApi = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const { data } = await http.post<LoginResponse>("/auth/login/", { username, password });
    return data;
  },
  async me(): Promise<AuthUser> {
    const { data } = await http.get<AuthUser>("/auth/me/");
    return data;
  },
  async logout(refresh: string): Promise<void> {
    await http.post("/auth/logout/", { refresh });
  },
};
