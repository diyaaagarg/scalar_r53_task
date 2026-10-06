"use client";

import { Flashbar, type FlashbarProps } from "@cloudscape-design/components";
import { createContext, useCallback, useContext, useMemo, useState } from "react";

type NotificationInput = Omit<FlashbarProps.MessageDefinition, "id" | "dismissible" | "onDismiss">;
type NotificationContextValue = { notify: (message: NotificationInput) => void };
const NotificationContext = createContext<NotificationContextValue | null>(null);

export function NotificationProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [items, setItems] = useState<FlashbarProps.MessageDefinition[]>([]);
  const notify = useCallback((message: NotificationInput) => {
    const id = crypto.randomUUID();
    setItems((current) => [...current, { ...message, id, dismissible: true, onDismiss: () => setItems((visible) => visible.filter((item) => item.id !== id)) }]);
  }, []);
  const value = useMemo(() => ({ notify }), [notify]);
  return <NotificationContext.Provider value={value}><Flashbar items={items} stackItems />{children}</NotificationContext.Provider>;
}

export function useNotifications(): NotificationContextValue {
  const context = useContext(NotificationContext);
  if (!context) throw new Error("useNotifications must be used inside NotificationProvider.");
  return context;
}
