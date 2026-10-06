import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.models import (
    DnsRecord,
    DnsRecordValue,
    HostedZone,
    HostedZoneTag,
    HostedZoneVpc,
    Tag,
    User,
    Vpc,
)
from app.repositories.hosted_zone_repository import HostedZoneRepository
from app.schemas.hosted_zone import HostedZoneCreate, HostedZoneUpdate


class HostedZoneService:
    def __init__(self):
        self.repository = HostedZoneRepository()

    def create(self, db: Session, user: User, data: HostedZoneCreate) -> HostedZone:
        if data.type == "PRIVATE" and not data.vpc_ids:
            raise DomainError(
                "vpc_required", "A private hosted zone requires at least one VPC."
            )
        if data.type == "PUBLIC" and data.vpc_ids:
            raise DomainError(
                "vpc_not_allowed",
                "A public hosted zone cannot be associated with VPCs.",
            )
        vpcs = (
            list(
                db.scalars(
                    select(Vpc).where(
                        Vpc.id.in_(data.vpc_ids), Vpc.account_id == user.account_id
                    )
                )
            )
            if data.vpc_ids
            else []
        )
        if len(vpcs) != len(set(data.vpc_ids)):
            raise DomainError(
                "vpc_not_found", "One or more selected VPCs do not exist.", 404
            )
        zone = HostedZone(
            account_id=user.account_id,
            created_by_user_id=user.id,
            public_id=f"Z{secrets.token_hex(10).upper()}",
            name=data.name,
            description=data.description,
            zone_type=data.type,
        )
        db.add(zone)
        db.flush()
        zone.vpc_links.extend(HostedZoneVpc(vpc_id=vpc.id) for vpc in vpcs)
        self._replace_tags(db, zone, data.tags)
        self._create_default_records(zone)
        zone.record_count = 2
        db.commit()
        db.refresh(zone)
        return zone

    def update(
        self, db: Session, zone: HostedZone, data: HostedZoneUpdate
    ) -> HostedZone:
        if "description" in data.model_fields_set:
            zone.description = data.description
        if data.tags is not None:
            self._replace_tags(db, zone, data.tags)
        db.commit()
        db.refresh(zone)
        return zone

    def delete(self, db: Session, zone: HostedZone, confirmation: str) -> None:
        if confirmation != "delete":
            raise DomainError(
                "invalid_confirmation", "Type 'delete' to confirm hosted zone deletion."
            )
        if zone.dnssec_enabled:
            raise DomainError(
                "dnssec_enabled",
                "Disable DNSSEC before deleting this hosted zone.",
                409,
            )
        if self.repository.non_system_record_count(db, zone.id):
            raise DomainError(
                "hosted_zone_not_empty",
                "Delete non-default records before deleting this hosted zone.",
                409,
            )
        db.delete(zone)
        db.commit()

    def _replace_tags(self, db: Session, zone: HostedZone, tags) -> None:
        zone.tag_links.clear()
        db.flush()
        seen: set[str] = set()
        for item in tags:
            if item.key in seen:
                raise DomainError("duplicate_tag", f"Duplicate tag key: {item.key}")
            seen.add(item.key)
            tag = db.scalar(
                select(Tag).where(
                    Tag.account_id == zone.account_id,
                    Tag.tag_key == item.key,
                    Tag.tag_value == item.value,
                )
            )
            if not tag:
                tag = Tag(
                    account_id=zone.account_id, tag_key=item.key, tag_value=item.value
                )
                db.add(tag)
                db.flush()
            zone.tag_links.append(HostedZoneTag(tag_id=tag.id))

    def _create_default_records(self, zone: HostedZone) -> None:
        ns = DnsRecord(
            hosted_zone=zone,
            name=zone.name,
            record_type="NS",
            ttl=172800,
            is_system_record=True,
        )
        ns.values = [
            DnsRecordValue(value=f"ns-{1000 + i}.awsdns-{40 + i}.com.", position=i)
            for i in range(4)
        ]
        soa = DnsRecord(
            hosted_zone=zone,
            name=zone.name,
            record_type="SOA",
            ttl=900,
            is_system_record=True,
        )
        soa.values = [
            DnsRecordValue(
                value="ns-1000.awsdns-40.com. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400",
                position=0,
            )
        ]
        zone.records.extend([ns, soa])
