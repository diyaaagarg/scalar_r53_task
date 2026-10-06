import re
from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import DomainError
from app.models import DnsRecord, DnsRecordValue, HostedZone
from app.schemas.record import DnsRecordWrite
from app.services.record_validation_service import RecordValidationService

SUPPORTED_TYPES = {"A", "AAAA", "CNAME", "TXT", "MX", "NS", "PTR", "SRV", "CAA"}


class ZoneTransferService:
    def __init__(self) -> None:
        self.validator = RecordValidationService()

    def export_json(self, db: Session, zone: HostedZone) -> dict:
        records = self._records(db, zone.id)
        return {
            "version": 1,
            "hosted_zone": {
                "id": zone.public_id,
                "name": zone.name,
                "type": zone.zone_type,
                "description": zone.description,
                "tags": [
                    {"key": link.tag.tag_key, "value": link.tag.tag_value}
                    for link in zone.tag_links
                ],
            },
            "records": [self._record_dict(record) for record in records],
        }

    def export_bind(self, db: Session, zone: HostedZone) -> str:
        lines = [f"$ORIGIN {zone.name}", "$TTL 300", ""]
        for record in self._records(db, zone.id):
            for value in record.values:
                name = (
                    "@"
                    if record.name == zone.name
                    else record.name.removesuffix(zone.name).rstrip(".")
                )
                lines.append(
                    f"{name:<24} {record.ttl or 300:<6} IN {record.record_type:<6} {value.value}"
                )
        return "\n".join(lines) + "\n"

    def import_bind(self, db: Session, zone: HostedZone, content: str) -> int:
        parsed = list(self._parse_bind(zone.name, content))
        if not parsed:
            raise DomainError(
                "bind_empty", "No supported records were found in this BIND zone file."
            )
        try:
            for data in parsed:
                self.validator.validate(db, zone.id, data)
                record = DnsRecord(
                    hosted_zone_id=zone.id,
                    name=data.name,
                    record_type=data.record_type,
                    ttl=data.ttl,
                    is_alias=False,
                    evaluate_target_health=False,
                )
                record.values = [
                    DnsRecordValue(value=value, position=index)
                    for index, value in enumerate(data.values)
                ]
                db.add(record)
            zone.record_count += len(parsed)
            db.commit()
        except Exception:
            db.rollback()
            raise
        return len(parsed)

    def _records(self, db: Session, zone_id: str) -> list[DnsRecord]:
        return list(
            db.scalars(
                select(DnsRecord)
                .where(DnsRecord.hosted_zone_id == zone_id)
                .options(selectinload(DnsRecord.values))
            )
        )

    def _record_dict(self, record: DnsRecord) -> dict:
        return {
            "name": record.name,
            "type": record.record_type,
            "ttl": record.ttl,
            "values": [value.value for value in record.values],
            "routing_policy": record.routing_policy,
            "alias": record.alias_target,
            "evaluate_target_health": record.evaluate_target_health,
            "health_check_id": record.health_check_id,
            "system": record.is_system_record,
        }

    def _parse_bind(self, origin: str, content: str) -> Iterable[DnsRecordWrite]:
        current_origin = origin
        default_ttl = 300
        for raw_line in content.splitlines():
            line = raw_line.split(";", 1)[0].strip()
            if not line:
                continue
            if line.upper().startswith("$ORIGIN"):
                value = line.split(maxsplit=1)[1].strip().rstrip(".")
                current_origin = f"{value}."
                continue
            if line.upper().startswith("$TTL"):
                try:
                    default_ttl = int(line.split(maxsplit=1)[1].strip())
                except ValueError:
                    raise DomainError(
                        "bind_invalid", "Invalid $TTL directive in BIND file."
                    )
                continue
            parts = re.split(r"\s+", line)
            if len(parts) < 4:
                raise DomainError("bind_invalid", f"Invalid BIND record: {raw_line}")
            name, index = parts[0], 1
            ttl = default_ttl
            if parts[index].upper() != "IN":
                try:
                    ttl = int(parts[index])
                except ValueError:
                    raise DomainError(
                        "bind_invalid", f"Invalid TTL in record: {raw_line}"
                    )
                index += 1
            if len(parts) <= index + 1 or parts[index].upper() != "IN":
                raise DomainError(
                    "bind_invalid", f"Only IN records are supported: {raw_line}"
                )
            index += 1
            record_type, value = parts[index].upper(), " ".join(parts[index + 1 :])
            if not value:
                raise DomainError("bind_invalid", f"Invalid BIND record: {raw_line}")
            if record_type in {"SOA", "NS"} and name in {
                "@",
                current_origin,
                current_origin.rstrip("."),
            }:
                continue
            if record_type not in SUPPORTED_TYPES:
                continue
            fqdn = (
                current_origin
                if name == "@"
                else name
                if name.endswith(".")
                else f"{name}.{current_origin}"
            )
            yield DnsRecordWrite(
                name=fqdn,
                record_type=record_type,
                ttl=ttl,
                values=[value],
                routing_policy="SIMPLE",
                alias=None,
                evaluate_target_health=False,
                health_check_id=None,
            )
