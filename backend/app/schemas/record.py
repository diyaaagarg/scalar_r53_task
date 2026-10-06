from datetime import datetime

from pydantic import Field, field_validator, model_validator

from app.schemas.common import ApiModel

RECORD_TYPES = {"A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR", "SRV", "CAA", "SOA"}


class AliasTarget(ApiModel):
    dns_name: str = Field(min_length=1, max_length=253)
    hosted_zone_id: str | None = None


class DnsRecordWrite(ApiModel):
    name: str = Field(min_length=1, max_length=253)
    record_type: str
    ttl: int | None = Field(default=300, ge=0, le=2_147_483_647)
    values: list[str] = Field(default_factory=list)
    routing_policy: str = Field(default="SIMPLE", pattern="^SIMPLE$")
    alias: AliasTarget | None = None
    evaluate_target_health: bool = False
    health_check_id: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip().lower().rstrip(".")
        if not value:
            raise ValueError("Record name is required.")
        return f"{value}."

    @field_validator("record_type")
    @classmethod
    def valid_type(cls, value: str) -> str:
        value = value.upper()
        if value not in RECORD_TYPES:
            raise ValueError("Unsupported record type.")
        return value

    @model_validator(mode="after")
    def alias_or_values(self):
        if self.alias and self.values:
            raise ValueError("Alias records cannot include values.")
        if not self.alias and not self.values:
            raise ValueError("At least one record value is required.")
        if self.alias and self.ttl is not None:
            self.ttl = None
        return self


class DnsRecordOut(ApiModel):
    id: str
    name: str
    record_type: str
    routing_policy: str
    differentiator: str | None = None
    is_alias: bool
    alias_target: str | None
    values: list[str]
    ttl: int | None
    evaluate_target_health: bool
    health_check_id: str | None
    is_system_record: bool
    created_at: datetime
    updated_at: datetime


class BulkDeleteRequest(ApiModel):
    record_ids: list[str] = Field(min_length=1, max_length=100)


class BulkDeleteResult(ApiModel):
    deleted_ids: list[str]
    failed: list[dict[str, str]]
