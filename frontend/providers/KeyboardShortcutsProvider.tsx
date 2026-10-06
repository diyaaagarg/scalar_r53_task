"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { useColorMode } from "@/providers/ColorModeProvider";

export function KeyboardShortcutsProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const router = useRouter(); const pathname = usePathname(); const { toggleColorMode } = useColorMode();
  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null;
      if (target?.matches("input, textarea, select, [contenteditable='true']") || !event.altKey) return;
      if (event.key.toLowerCase() === "h") { event.preventDefault(); router.push("/hosted-zones"); }
      if (event.key.toLowerCase() === "m") { event.preventDefault(); toggleColorMode(); }
      if (event.key.toLowerCase() === "n") { event.preventDefault(); window.dispatchEvent(new CustomEvent(pathname.startsWith("/hosted-zones/") ? "route53:create-record" : "route53:create-zone")); }
    };
    window.addEventListener("keydown", onKeyDown); return () => window.removeEventListener("keydown", onKeyDown);
  }, [pathname, router, toggleColorMode]);
  return children;
}
