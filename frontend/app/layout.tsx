import type { Metadata } from "next";
import "@/app/globals.css";
import { AuthProvider } from "@/providers/AuthProvider";
import { ColorModeProvider } from "@/providers/ColorModeProvider";
import { KeyboardShortcutsProvider } from "@/providers/KeyboardShortcutsProvider";
import { NotificationProvider } from "@/providers/NotificationProvider";

export const metadata: Metadata = { title: "Route 53 | AWS Console", description: "Route 53 console clone" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body className="aws-console-body"><ColorModeProvider><KeyboardShortcutsProvider><NotificationProvider><AuthProvider>{children}</AuthProvider></NotificationProvider></KeyboardShortcutsProvider></ColorModeProvider></body></html>;
}
