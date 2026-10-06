import { apiClient } from "@/lib/api/client";
import type { Paginated } from "@/lib/api/hostedZones";

export const recordTypes = ["A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR", "SRV", "CAA"] as const;
export type RecordType = (typeof recordTypes)[number];
export interface AliasTarget { dns_name: string; hosted_zone_id?: string; }
export interface DnsRecord { id: string; name: string; record_type: RecordType | "SOA"; routing_policy: string; differentiator: string | null; is_alias: boolean; alias_target: string | null; values: string[]; ttl: number | null; evaluate_target_health: boolean; health_check_id: string | null; is_system_record: boolean; created_at: string; updated_at: string; }
export interface RecordWrite { name: string; record_type: RecordType; ttl: number | null; values: string[]; routing_policy: "SIMPLE"; alias: AliasTarget | null; evaluate_target_health: boolean; health_check_id: string | null; }

export const recordsApi = {
  list: (zoneId: string, parameters: URLSearchParams) => apiClient.get<Paginated<DnsRecord>>(`/hosted-zones/${zoneId}/records?${parameters.toString()}`),
  create: (zoneId: string, data: RecordWrite) => apiClient.post<DnsRecord>(`/hosted-zones/${zoneId}/records`, data),
  update: (zoneId: string, recordId: string, data: RecordWrite) => apiClient.patch<DnsRecord>(`/hosted-zones/${zoneId}/records/${recordId}`, data),
  bulkDelete: (zoneId: string, recordIds: string[]) => apiClient.post<{ deleted_ids: string[]; failed: Array<{ id: string; reason: string }> }>(`/hosted-zones/${zoneId}/records/bulk-delete`, { record_ids: recordIds }),
  importBind: (zoneId: string, content: string) => apiClient.post<{ created_count: number }>(`/hosted-zones/${zoneId}/import`, { format: "BIND", content }),
  export: (zoneId: string, format: "json" | "bind") => apiClient.raw(`/hosted-zones/${zoneId}/export?format=${format}`),
};
