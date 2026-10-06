import { apiClient } from "@/lib/api/client";
import type { Session } from "@/lib/api/types";

export const authApi = {
  login: (email: string, password: string) => apiClient.post<Session>("/auth/login", { email, password }),
  logout: () => apiClient.post<void>("/auth/logout"),
  me: () => apiClient.get<Session>("/auth/me"),
};
