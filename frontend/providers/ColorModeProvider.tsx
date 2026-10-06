"use client";

import { Mode, applyMode } from "@cloudscape-design/global-styles";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

type ColorMode = "dark" | "light";
type ColorModeContextValue = { colorMode: ColorMode; toggleColorMode: () => void };
const ColorModeContext = createContext<ColorModeContextValue | null>(null);

export function ColorModeProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [colorMode, setColorMode] = useState<ColorMode>("dark");
  useEffect(() => { const saved = window.localStorage.getItem("route53-color-mode") as ColorMode | null; if (saved === "light" || saved === "dark") setColorMode(saved); }, []);
  useEffect(() => { applyMode(colorMode === "dark" ? Mode.Dark : Mode.Light); window.localStorage.setItem("route53-color-mode", colorMode); }, [colorMode]);
  const toggleColorMode = useCallback(() => setColorMode((current) => current === "dark" ? "light" : "dark"), []);
  const value = useMemo(() => ({ colorMode, toggleColorMode }), [colorMode, toggleColorMode]);
  return <ColorModeContext.Provider value={value}>{children}</ColorModeContext.Provider>;
}

export function useColorMode(): ColorModeContextValue { const context = useContext(ColorModeContext); if (!context) throw new Error("useColorMode must be used inside ColorModeProvider."); return context; }
