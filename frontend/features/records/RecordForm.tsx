"use client";

import { Alert, Box, Button, Checkbox, Form, FormField, Input, Modal, Select, SpaceBetween, Textarea } from "@cloudscape-design/components";
import { type FormEvent, useEffect, useState } from "react";
import { ApiClientError } from "@/lib/api/client";
import { recordsApi, recordTypes, type DnsRecord, type RecordType, type RecordWrite } from "@/lib/api/records";

type Props = { zoneId: string; visible: boolean; record?: DnsRecord; zoneName: string; onDismiss: () => void; onSaved: (record: DnsRecord, created: boolean) => void; };
const typeOptions = recordTypes.map((value) => ({ value, label: value }));

export function RecordForm({ zoneId, visible, record, zoneName, onDismiss, onSaved }: Props) {
  const isEdit = Boolean(record); const [name, setName] = useState(""); const [recordType, setRecordType] = useState<RecordType>("A"); const [ttl, setTtl] = useState("300"); const [values, setValues] = useState("");
  const [isAlias, setIsAlias] = useState(false); const [aliasTarget, setAliasTarget] = useState(""); const [evaluateHealth, setEvaluateHealth] = useState(false); const [healthCheckId, setHealthCheckId] = useState("");
  const [mxPriority, setMxPriority] = useState("10"); const [mxTarget, setMxTarget] = useState(""); const [srvPriority, setSrvPriority] = useState("1"); const [srvWeight, setSrvWeight] = useState("1"); const [srvPort, setSrvPort] = useState("443"); const [srvTarget, setSrvTarget] = useState(""); const [caaFlags, setCaaFlags] = useState("0"); const [caaTag, setCaaTag] = useState("issue"); const [caaValue, setCaaValue] = useState("");
  const [error, setError] = useState<string>(); const [isSaving, setIsSaving] = useState(false);
  useEffect(() => {
    if (!visible) return;
    const current = record?.values[0] ?? "";
    setName(record?.name.replace(new RegExp(`\\.?${escapeRegExp(zoneName)}$`), "") || ""); setRecordType((record?.record_type === "SOA" ? "A" : record?.record_type) ?? "A"); setTtl(record?.ttl?.toString() ?? "300"); setValues(record?.values.join("\n") ?? ""); setIsAlias(record?.is_alias ?? false); setAliasTarget(record?.alias_target ?? ""); setEvaluateHealth(record?.evaluate_target_health ?? false); setHealthCheckId(record?.health_check_id ?? "");
    const mx = current.split(/\s+/, 2); setMxPriority(mx[0] ?? "10"); setMxTarget(mx[1] ?? "");
    const srv = current.split(/\s+/, 4); setSrvPriority(srv[0] ?? "1"); setSrvWeight(srv[1] ?? "1"); setSrvPort(srv[2] ?? "443"); setSrvTarget(srv[3] ?? "");
    const caa = current.match(/^(\d+)\s+(\S+)\s+"(.*)"$/); setCaaFlags(caa?.[1] ?? "0"); setCaaTag(caa?.[2] ?? "issue"); setCaaValue(caa?.[3] ?? ""); setError(undefined);
  }, [visible, record, zoneName]);
  function composedValues(): string[] {
    if (isAlias) return [];
    if (recordType === "MX") return [`${mxPriority} ${mxTarget.trim()}`];
    if (recordType === "SRV") return [`${srvPriority} ${srvWeight} ${srvPort} ${srvTarget.trim()}`];
    if (recordType === "CAA") return [`${caaFlags} ${caaTag.trim()} "${caaValue}"`];
    if (recordType === "TXT") return values.split("\n").map((value) => value.trim()).filter(Boolean).map((value) => value.startsWith('"') ? value : `"${value}"`);
    return values.split("\n").map((value) => value.trim()).filter(Boolean);
  }
  function validate(data: RecordWrite): string | undefined {
    if (isAlias && !data.alias?.dns_name) return "Enter an alias target.";
    if (!isAlias && !data.values.length) return "Enter at least one record value.";
    if (!isAlias && data.ttl === null) return "TTL is required for non-alias records.";
    if (data.ttl !== null && (!Number.isInteger(data.ttl) || data.ttl < 0 || data.ttl > 2_147_483_647)) return "TTL must be between 0 and 2147483647.";
    if (recordType === "A" && data.values.some((value) => !/^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$/.test(value))) return "A records require valid IPv4 addresses.";
    if (recordType === "AAAA" && data.values.some((value) => !value.includes(":"))) return "AAAA records require valid IPv6 addresses.";
    if ((recordType === "MX" || recordType === "SRV") && data.values.some((value) => value.includes("undefined") || value.endsWith(" "))) return `Complete every ${recordType} field.`;
    return undefined;
  }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const recordName = name.trim() ? (name.includes(".") ? name.trim() : `${name.trim()}.${zoneName.replace(/\.$/, "")}`) : zoneName;
    const data: RecordWrite = { name: recordName, record_type: recordType, ttl: isAlias ? null : Number(ttl), values: composedValues(), routing_policy: "SIMPLE", alias: isAlias ? { dns_name: aliasTarget.trim() } : null, evaluate_target_health: evaluateHealth, health_check_id: healthCheckId.trim() || null };
    const message = validate(data); if (message) { setError(message); return; }
    setError(undefined); setIsSaving(true);
    try { onSaved(isEdit && record ? await recordsApi.update(zoneId, record.id, data) : await recordsApi.create(zoneId, data), !isEdit); }
    catch (caught) { setError(caught instanceof ApiClientError ? caught.message : "Unable to save this record."); }
    finally { setIsSaving(false); }
  }
  const selectedType = typeOptions.find((option) => option.value === recordType) ?? typeOptions[0];
  return <Modal visible={visible} onDismiss={onDismiss} size="large" header={isEdit ? "Edit record" : "Create record"} footer={<Box float="right"><SpaceBetween direction="horizontal" size="xs"><Button onClick={onDismiss}>Cancel</Button><Button variant="primary" form="record-form" formAction="submit" loading={isSaving}>{isEdit ? "Save changes" : "Create records"}</Button></SpaceBetween></Box>}><form id="record-form" onSubmit={submit}><Form><SpaceBetween size="l">{error && <Alert type="error">{error}</Alert>}<FormField label="Record name" description={`Leave the domain blank to create a record at ${zoneName}`}><Input value={name} onChange={({ detail }) => setName(detail.value)} placeholder="www" /></FormField><FormField label="Record type"><Select selectedOption={selectedType} options={typeOptions} onChange={({ detail }) => { setRecordType(detail.selectedOption.value as RecordType); setIsAlias(false); }} /></FormField>{(recordType === "A" || recordType === "AAAA") && <Checkbox checked={isAlias} onChange={({ detail }) => setIsAlias(detail.checked)}>Alias</Checkbox>}{isAlias ? <><FormField label="Route traffic to"><Input value={aliasTarget} onChange={({ detail }) => setAliasTarget(detail.value)} placeholder="target.example.com" /></FormField><Checkbox checked={evaluateHealth} onChange={({ detail }) => setEvaluateHealth(detail.checked)}>Evaluate target health</Checkbox></> : <><RecordValueFields recordType={recordType} values={values} setValues={setValues} mxPriority={mxPriority} setMxPriority={setMxPriority} mxTarget={mxTarget} setMxTarget={setMxTarget} srvPriority={srvPriority} setSrvPriority={setSrvPriority} srvWeight={srvWeight} setSrvWeight={setSrvWeight} srvPort={srvPort} setSrvPort={setSrvPort} srvTarget={srvTarget} setSrvTarget={setSrvTarget} caaFlags={caaFlags} setCaaFlags={setCaaFlags} caaTag={caaTag} setCaaTag={setCaaTag} caaValue={caaValue} setCaaValue={setCaaValue} /><FormField label="TTL (seconds)"><Input value={ttl} type="number" onChange={({ detail }) => setTtl(detail.value)} /></FormField></>}<FormField label="Health check ID (optional)"><Input value={healthCheckId} onChange={({ detail }) => setHealthCheckId(detail.value)} placeholder="Health check ID" /></FormField></SpaceBetween></Form></form></Modal>;
}

type FieldProps = { recordType: RecordType; values: string; setValues: (value: string) => void; mxPriority: string; setMxPriority: (value: string) => void; mxTarget: string; setMxTarget: (value: string) => void; srvPriority: string; setSrvPriority: (value: string) => void; srvWeight: string; setSrvWeight: (value: string) => void; srvPort: string; setSrvPort: (value: string) => void; srvTarget: string; setSrvTarget: (value: string) => void; caaFlags: string; setCaaFlags: (value: string) => void; caaTag: string; setCaaTag: (value: string) => void; caaValue: string; setCaaValue: (value: string) => void; };
function RecordValueFields(props: FieldProps) {
  if (props.recordType === "MX") return <SpaceBetween direction="horizontal" size="s"><FormField label="Priority"><Input value={props.mxPriority} onChange={({ detail }) => props.setMxPriority(detail.value)} /></FormField><FormField label="Mail server"><Input value={props.mxTarget} onChange={({ detail }) => props.setMxTarget(detail.value)} placeholder="mail.example.com." /></FormField></SpaceBetween>;
  if (props.recordType === "SRV") return <SpaceBetween direction="horizontal" size="s"><FormField label="Priority"><Input value={props.srvPriority} onChange={({ detail }) => props.setSrvPriority(detail.value)} /></FormField><FormField label="Weight"><Input value={props.srvWeight} onChange={({ detail }) => props.setSrvWeight(detail.value)} /></FormField><FormField label="Port"><Input value={props.srvPort} onChange={({ detail }) => props.setSrvPort(detail.value)} /></FormField><FormField label="Target"><Input value={props.srvTarget} onChange={({ detail }) => props.setSrvTarget(detail.value)} placeholder="server.example.com." /></FormField></SpaceBetween>;
  if (props.recordType === "CAA") return <SpaceBetween direction="horizontal" size="s"><FormField label="Flags"><Input value={props.caaFlags} onChange={({ detail }) => props.setCaaFlags(detail.value)} /></FormField><FormField label="Tag"><Input value={props.caaTag} onChange={({ detail }) => props.setCaaTag(detail.value)} placeholder="issue" /></FormField><FormField label="Value"><Input value={props.caaValue} onChange={({ detail }) => props.setCaaValue(detail.value)} placeholder="letsencrypt.org" /></FormField></SpaceBetween>;
  const label = props.recordType === "TXT" ? "Value (one per line; quotes optional)" : "Value (one per line)";
  const placeholder = props.recordType === "A" ? "192.0.2.1" : props.recordType === "AAAA" ? "2001:db8::1" : props.recordType === "TXT" ? "Example text" : "target.example.com.";
  return <FormField label={label}><Textarea value={props.values} onChange={({ detail }) => props.setValues(detail.value)} placeholder={placeholder} /></FormField>;
}
function escapeRegExp(value: string) { return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
