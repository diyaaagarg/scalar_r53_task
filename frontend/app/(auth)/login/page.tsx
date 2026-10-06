"use client";

import { Alert, Box, Button, Container, Form, FormField, Header, Input, SpaceBetween } from "@cloudscape-design/components";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { authApi } from "@/lib/api/auth";
import { ApiClientError } from "@/lib/api/client";
import { useAuth } from "@/providers/AuthProvider";
import { useNotifications } from "@/providers/NotificationProvider";

export default function LoginPage() {
  const router = useRouter(); const { refresh } = useAuth(); const { notify } = useNotifications();
  const [email, setEmail] = useState("student@example.com"); const [password, setPassword] = useState("Password123!"); const [error, setError] = useState<string>(); const [isLoading, setIsLoading] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(undefined); setIsLoading(true);
    try { await authApi.login(email, password); await refresh(); notify({ type: "success", content: "Signed in successfully.", dismissLabel: "Dismiss notification" }); router.replace("/dashboard"); }
    catch (caught) { setError(caught instanceof ApiClientError ? caught.message : "Unable to sign in. Please try again."); }
    finally { setIsLoading(false); }
  }
  return <main className="login-page"><div className="login-card"><Container header={<Header variant="h1" description="Sign in to the Route 53 console clone"><Image className="aws-wordmark" src="/aws-logo.png" alt="AWS" width={112} height={81} priority /></Header>}><form onSubmit={submit}><Form actions={<Button variant="primary" loading={isLoading} formAction="submit">Sign in</Button>}><SpaceBetween size="l">{error && <Alert type="error">{error}</Alert>}<FormField label="Email"><Input value={email} onChange={({ detail }) => setEmail(detail.value)} type="email" autoComplete="email" /></FormField><FormField label="Password"><Input value={password} onChange={({ detail }) => setPassword(detail.value)} type="password" autoComplete="current-password" /></FormField><Box color="text-body-secondary" fontSize="body-s">Demo account: student@example.com / Password123!</Box></SpaceBetween></Form></form></Container></div></main>;
}
