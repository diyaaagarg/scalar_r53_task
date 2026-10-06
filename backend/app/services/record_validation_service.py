import ipaddress
import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import DomainError
from app.models import DnsRecord
from app.schemas.record import DnsRecordWrite

FQDN_RE = re.compile(
    r"^(?=.{1,253}\.?$)(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\.?$"
)


class RecordValidationService:
    def validate(
        self,
        db: Session,
        zone_id: str,
        data: DnsRecordWrite,
        replacing_id: str | None = None,
    ) -> None:
        if data.record_type == "SOA":
            raise DomainError(
                "system_record", "SOA records are system managed and read-only.", 403
            )
        if data.alias and data.record_type not in {"A", "AAAA"}:
            raise DomainError(
                "invalid_alias",
                "Alias records are supported only for A and AAAA records.",
            )
        if data.record_type == "CNAME":
            clashes = db.scalar(
                select(DnsRecord).where(
                    DnsRecord.hosted_zone_id == zone_id,
                    DnsRecord.name == data.name,
                    DnsRecord.id != replacing_id,
                )
            )
            if clashes:
                raise DomainError(
                    "cname_conflict",
                    "A CNAME record cannot coexist with another record at the same name.",
                    409,
                )
        else:
            cname = db.scalar(
                select(DnsRecord).where(
                    DnsRecord.hosted_zone_id == zone_id,
                    DnsRecord.name == data.name,
                    DnsRecord.record_type == "CNAME",
                    DnsRecord.id != replacing_id,
                )
            )
            if cname:
                raise DomainError(
                    "cname_conflict",
                    "A record cannot coexist with a CNAME at the same name.",
                    409,
                )
        for value in data.values:
            self._validate_value(data.record_type, value)

    def _fqdn(self, value: str) -> bool:
        return bool(FQDN_RE.fullmatch(value.strip()))

    def _validate_value(self, record_type: str, value: str) -> None:
        value = value.strip()
        try:
            if record_type == "A":
                ipaddress.IPv4Address(value)
                return
            if record_type == "AAAA":
                ipaddress.IPv6Address(value)
                return
        except ValueError:
            raise DomainError(
                "invalid_record_value", f"{record_type} requires a valid IP address."
            )
        if record_type in {"CNAME", "NS", "PTR"} and not self._fqdn(value):
            raise DomainError(
                "invalid_record_value",
                f"{record_type} requires a fully qualified domain name.",
            )
        if record_type == "MX":
            parts = value.split(maxsplit=1)
            if (
                len(parts) != 2
                or not parts[0].isdigit()
                or not 0 <= int(parts[0]) <= 65535
                or not self._fqdn(parts[1])
            ):
                raise DomainError(
                    "invalid_record_value",
                    "MX must be '<priority> <fully-qualified-domain>'.",
                )
        if record_type == "SRV":
            parts = value.split(maxsplit=3)
            if (
                len(parts) != 4
                or any(not part.isdigit() for part in parts[:3])
                or not self._fqdn(parts[3])
                or any(not 0 <= int(part) <= 65535 for part in parts[:3])
            ):
                raise DomainError(
                    "invalid_record_value",
                    "SRV must be '<priority> <weight> <port> <fully-qualified-domain>'.",
                )
        if record_type == "CAA" and not re.fullmatch(
            r"(?:0|128) [A-Za-z0-9]+ \".*\"", value
        ):
            raise DomainError(
                "invalid_record_value", "CAA must be '<flags> <tag> \"value\"'."
            )
        if record_type == "TXT" and not (value.startswith('"') and value.endswith('"')):
            raise DomainError("invalid_record_value", "TXT values must be quoted.")
