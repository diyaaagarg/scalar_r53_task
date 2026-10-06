"use client";

import { Spinner } from "@cloudscape-design/components";
import { usePathname, useRouter } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { authApi } from "@/lib/api/auth";
import type { Session } from "@/lib/api/types";

type AuthContextValue = { session: Session | null; isLoading: boolean; refresh: () => Promise<void>; signOut: () => Promise<void> };
const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [session, setSession] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();
  const refresh = useCallback(async () => {
    try { setSession(await authApi.me()); }
    catch { setSession(null); if (pathname !== "/login") router.replace("/login"); }
    finally { setIsLoading(false); }
  }, [pathname, router]);
  useEffect(() => { void refresh(); }, [refresh]);
  const signOut = useCallback(async () => { await authApi.logout(); setSession(null); router.replace("/login"); }, [router]);
  const value = useMemo(() => ({ session, isLoading, refresh, signOut }), [session, isLoading, refresh, signOut]);
  if (isLoading) return <div className="login-page"><Spinner size="large" /></div>;
  if (!session && pathname !== "/login") return null;
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue { const context = useContext(AuthContext); if (!context) throw new Error("useAuth must be used inside AuthProvider."); return context; }
