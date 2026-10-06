from datetime import datetime

from pydantic import Field, field_validator

from app.schemas.common import ApiModel, TagIn


class VpcOut(ApiModel):
    id: str
    aws_vpc_id: str
    region: str
    name: str | None


class HostedZoneCreate(ApiModel):
    name: str = Field(min_length=1, max_length=253)
    description: str | None = Field(default=None, max_length=1000)
    type: str = Field(pattern="^(PUBLIC|PRIVATE)$")
    vpc_ids: list[str] = Field(default_factory=list)
    tags: list[TagIn] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip().lower().rstrip(".")
        if (
            not value
            or ".." in value
            or any(not label or len(label) > 63 for label in value.split("."))
        ):
            raise ValueError("Enter a valid domain name.")
        return f"{value}."


class HostedZoneUpdate(ApiModel):
    description: str | None = Field(default=None, max_length=1000)
    tags: list[TagIn] | None = None


class HostedZoneSummary(ApiModel):
    id: str
    hosted_zone_id: str
    name: str
    type: str
    created_by: str
    record_count: int
    description: str | None
    created_at: datetime


class HostedZoneDetail(HostedZoneSummary):
    dnssec_enabled: bool
    vpcs: list[VpcOut]
    tags: list[TagIn]
    updated_at: datetime


class DeleteHostedZoneRequest(ApiModel):
    confirmation: str
