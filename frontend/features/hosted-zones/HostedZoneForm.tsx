"use client";

import { Alert, Box, Button, Form, FormField, Input, Modal, Multiselect, RadioGroup, SpaceBetween, Textarea } from "@cloudscape-design/components";
import { type FormEvent, useEffect, useState } from "react";
import { ApiClientError } from "@/lib/api/client";
import { hostedZonesApi, type HostedZoneDetail, type Tag, type Vpc, type ZoneType } from "@/lib/api/hostedZones";

type Props = { visible: boolean; zone?: HostedZoneDetail; onDismiss: () => void; onSaved: (zone: HostedZoneDetail, created: boolean) => void; };
const emptyTag: Tag = { key: "", value: "" };

export function HostedZoneForm({ visible, zone, onDismiss, onSaved }: Props) {
  const isEdit = Boolean(zone);
  const [name, setName] = useState(""); const [description, setDescription] = useState(""); const [zoneType, setZoneType] = useState<ZoneType>("PUBLIC");
  const [tags, setTags] = useState<Tag[]>([]); const [vpcs, setVpcs] = useState<Vpc[]>([]); const [vpcIds, setVpcIds] = useState<string[]>([]); const [error, setError] = useState<string>(); const [isSaving, setIsSaving] = useState(false);
  useEffect(() => { if (visible && !isEdit) void hostedZonesApi.listVpcs().then(({ items }) => setVpcs(items)).catch(() => setVpcs([])); }, [visible, isEdit]);
  useEffect(() => { if (visible) { setName(zone?.name.replace(/\.$/, "") ?? ""); setDescription(zone?.description ?? ""); setZoneType(zone?.type ?? "PUBLIC"); setTags(zone?.tags ?? []); setVpcIds(zone?.vpcs.map((vpc) => vpc.id) ?? []); setError(undefined); } }, [visible, zone]);
  function updateTag(index: number, property: keyof Tag, value: string) { setTags((current) => current.map((tag, currentIndex) => currentIndex === index ? { ...tag, [property]: value } : tag)); }
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(undefined); setIsSaving(true);
    const usableTags = tags.filter((tag) => tag.key.trim()).map((tag) => ({ key: tag.key.trim(), value: tag.value.trim() }));
    try { if (isEdit && zone) onSaved(await hostedZonesApi.update(zone.id, { description: description || undefined, tags: usableTags }), false); else onSaved(await hostedZonesApi.create({ name, description: description || undefined, type: zoneType, vpc_ids: zoneType === "PRIVATE" ? vpcIds : [], tags: usableTags }), true); }
    catch (caught) { setError(caught instanceof ApiClientError ? caught.message : "Unable to save the hosted zone."); }
    finally { setIsSaving(false); }
  }
  const selectedVpcs = vpcs.filter((vpc) => vpcIds.includes(vpc.id)).map(asOption);
  return <Modal visible={visible} onDismiss={onDismiss} size="large" header={isEdit ? "Edit hosted zone" : "Create hosted zone"} footer={<Box float="right"><SpaceBetween direction="horizontal" size="xs"><Button onClick={onDismiss}>Cancel</Button><Button variant="primary" form="hosted-zone-form" formAction="submit" loading={isSaving}>{isEdit ? "Save changes" : "Create hosted zone"}</Button></SpaceBetween></Box>}><form id="hosted-zone-form" onSubmit={submit}><Form><SpaceBetween size="l">{error && <Alert type="error">{error}</Alert>}{!isEdit && <><FormField label="Domain name" description="Enter the domain name for this hosted zone."><Input value={name} onChange={({ detail }) => setName(detail.value)} placeholder="example.com" /></FormField><FormField label="Type"><RadioGroup value={zoneType} onChange={({ detail }) => { setZoneType(detail.value as ZoneType); if (detail.value === "PUBLIC") setVpcIds([]); }} items={[{ value: "PUBLIC", label: "Public hosted zone", description: "Routes traffic on the internet." }, { value: "PRIVATE", label: "Private hosted zone", description: "Routes traffic within one or more VPCs." }]} /></FormField>{zoneType === "PRIVATE" && <FormField label="VPCs" description="Choose the VPCs associated with this private hosted zone."><Multiselect selectedOptions={selectedVpcs} options={vpcs.map(asOption)} onChange={({ detail }) => setVpcIds(detail.selectedOptions.map((option) => option.value ?? "").filter(Boolean))} placeholder="Choose VPCs" /></FormField>}</>}<FormField label="Description" description="An optional description for this hosted zone."><Textarea value={description} onChange={({ detail }) => setDescription(detail.value)} placeholder="Describe this hosted zone" /></FormField><FormField label="Tags" description="Add tags to organize hosted zones."><SpaceBetween size="xs">{tags.map((tag, index) => <SpaceBetween key={`${index}-${tag.key}`} direction="horizontal" size="xs"><Input value={tag.key} onChange={({ detail }) => updateTag(index, "key", detail.value)} placeholder="Key" /><Input value={tag.value} onChange={({ detail }) => updateTag(index, "value", detail.value)} placeholder="Value" /><Button iconName="remove" variant="icon" ariaLabel="Remove tag" onClick={() => setTags((current) => current.filter((_, currentIndex) => currentIndex !== index))} /></SpaceBetween>)}<Button iconName="add-plus" onClick={() => setTags((current) => [...current, emptyTag])}>Add tag</Button></SpaceBetween></FormField></SpaceBetween></Form></form></Modal>;
}

function asOption(vpc: Vpc) { return { label: `${vpc.aws_vpc_id}${vpc.name ? ` — ${vpc.name}` : ""}`, value: vpc.id, description: vpc.region }; }
