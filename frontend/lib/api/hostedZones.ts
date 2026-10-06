import { apiClient } from "@/lib/api/client";

export type ZoneType = "PUBLIC" | "PRIVATE";
export interface Tag { key: string; value: string; }
export interface Vpc { id: string; aws_vpc_id: string; region: string; name: string | null; }
export interface HostedZone { id: string; hosted_zone_id: string; name: string; type: ZoneType; created_by: string; record_count: number; description: string | null; created_at: string; }
export interface HostedZoneDetail extends HostedZone { dnssec_enabled: boolean; vpcs: Vpc[]; tags: Tag[]; updated_at: string; }
export interface Paginated<T> { items: T[]; pagination: { page: number; page_size: number; total: number; total_pages: number; }; }
export interface HostedZoneCreate { name: string; description?: string; type: ZoneType; vpc_ids?: string[]; tags?: Tag[]; }

export const hostedZonesApi = {
  list: (parameters: URLSearchParams) => apiClient.get<Paginated<HostedZone>>(`/hosted-zones?${parameters.toString()}`),
  get: (zoneId: string) => apiClient.get<HostedZoneDetail>(`/hosted-zones/${zoneId}`),
  create: (data: HostedZoneCreate) => apiClient.post<HostedZoneDetail>("/hosted-zones", data),
  update: (zoneId: string, data: Pick<HostedZoneCreate, "description" | "tags">) => apiClient.patch<HostedZoneDetail>(`/hosted-zones/${zoneId}`, data),
  remove: (zoneId: string) => apiClient.delete<void>(`/hosted-zones/${zoneId}`, { confirmation: "delete" }),
  listVpcs: () => apiClient.get<{ items: Vpc[] }>("/vpcs"),
};
