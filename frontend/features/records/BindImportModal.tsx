"use client";

import { Alert, Box, Button, Form, FormField, Modal, SpaceBetween, Textarea } from "@cloudscape-design/components";
import { type FormEvent, useState } from "react";
import { ApiClientError } from "@/lib/api/client";
import { recordsApi } from "@/lib/api/records";

type Props = { zoneId: string; visible: boolean; onDismiss: () => void; onImported: (count: number) => void; };

export function BindImportModal({ zoneId, visible, onDismiss, onImported }: Props) {
  const [content, setContent] = useState(""); const [error, setError] = useState<string>(); const [isImporting, setIsImporting] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(undefined); setIsImporting(true);
    try { const result = await recordsApi.importBind(zoneId, content); setContent(""); onImported(result.created_count); }
    catch (caught) { setError(caught instanceof ApiClientError ? caught.message : "Unable to import the BIND zone file."); }
    finally { setIsImporting(false); }
  }
  return <Modal visible={visible} onDismiss={onDismiss} size="large" header="Import BIND zone file" footer={<Box float="right"><SpaceBetween direction="horizontal" size="xs"><Button onClick={onDismiss}>Cancel</Button><Button form="bind-import-form" formAction="submit" variant="primary" loading={isImporting}>Import records</Button></SpaceBetween></Box>}><form id="bind-import-form" onSubmit={submit}><Form><SpaceBetween size="m">{error && <Alert type="error">{error}</Alert>}<Alert type="info">Paste standard BIND records. The importer supports A, AAAA, CNAME, TXT, MX, NS, PTR, SRV, and CAA records; apex SOA and NS records are kept system-managed.</Alert><FormField label="BIND zone file contents"><Textarea value={content} onChange={({ detail }) => setContent(detail.value)} placeholder={'$ORIGIN example.com.\n$TTL 300\nwww IN A 192.0.2.10'} rows={16} /></FormField></SpaceBetween></Form></form></Modal>;
}
