import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def uuid_id() -> str:
    return str(uuid.uuid4())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Account(TimestampMixin, Base):
    __tablename__ = "accounts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    aws_account_id: Mapped[str] = mapped_column(String(12), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    default_region: Mapped[str] = mapped_column(
        String(32), nullable=False, default="us-east-1"
    )
    users: Mapped[list["User"]] = relationship(back_populates="account")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    account: Mapped[Account] = relationship(back_populates="users")
    sessions: Mapped[list["SessionToken"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class SessionToken(Base):
    __tablename__ = "sessions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    user: Mapped[User] = relationship(back_populates="sessions")
    __table_args__ = (Index("ix_sessions_user_expiry", "user_id", "expires_at"),)


class HostedZone(TimestampMixin, Base):
    __tablename__ = "hosted_zones"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    created_by_user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    public_id: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(253), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    zone_type: Mapped[str] = mapped_column(String(10), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    dnssec_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    records: Mapped[list["DnsRecord"]] = relationship(
        back_populates="hosted_zone", cascade="all, delete-orphan"
    )
    vpc_links: Mapped[list["HostedZoneVpc"]] = relationship(
        back_populates="hosted_zone", cascade="all, delete-orphan"
    )
    tag_links: Mapped[list["HostedZoneTag"]] = relationship(
        back_populates="hosted_zone", cascade="all, delete-orphan"
    )
    __table_args__ = (
        CheckConstraint(
            "zone_type IN ('PUBLIC', 'PRIVATE')", name="ck_hosted_zone_type"
        ),
        Index("ix_hosted_zones_account_name", "account_id", "name"),
    )


class Vpc(TimestampMixin, Base):
    __tablename__ = "vpcs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    aws_vpc_id: Mapped[str] = mapped_column(String(32), nullable=False)
    region: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str | None] = mapped_column(String(120))
    __table_args__ = (
        UniqueConstraint("account_id", "aws_vpc_id", name="uq_vpc_account_aws_id"),
    )


class HostedZoneVpc(Base):
    __tablename__ = "hosted_zone_vpcs"
    hosted_zone_id: Mapped[str] = mapped_column(
        ForeignKey("hosted_zones.id", ondelete="CASCADE"), primary_key=True
    )
    vpc_id: Mapped[str] = mapped_column(
        ForeignKey("vpcs.id", ondelete="RESTRICT"), primary_key=True
    )
    hosted_zone: Mapped[HostedZone] = relationship(back_populates="vpc_links")
    vpc: Mapped[Vpc] = relationship()


class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    account_id: Mapped[str] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False
    )
    tag_key: Mapped[str] = mapped_column(String(128), nullable=False)
    tag_value: Mapped[str] = mapped_column(String(256), nullable=False)
    __table_args__ = (
        UniqueConstraint("account_id", "tag_key", "tag_value", name="uq_account_tag"),
        Index("ix_tags_account_key", "account_id", "tag_key"),
    )


class HostedZoneTag(Base):
    __tablename__ = "hosted_zone_tags"
    hosted_zone_id: Mapped[str] = mapped_column(
        ForeignKey("hosted_zones.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[str] = mapped_column(
        ForeignKey("tags.id", ondelete="RESTRICT"), primary_key=True
    )
    hosted_zone: Mapped[HostedZone] = relationship(back_populates="tag_links")
    tag: Mapped[Tag] = relationship()


class DnsRecord(TimestampMixin, Base):
    __tablename__ = "dns_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    hosted_zone_id: Mapped[str] = mapped_column(
        ForeignKey("hosted_zones.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(253), nullable=False)
    record_type: Mapped[str] = mapped_column(String(8), nullable=False)
    routing_policy: Mapped[str] = mapped_column(
        String(24), nullable=False, default="SIMPLE"
    )
    set_identifier: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    ttl: Mapped[int | None] = mapped_column(Integer)
    is_alias: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    alias_target: Mapped[str | None] = mapped_column(String(253))
    evaluate_target_health: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    health_check_id: Mapped[str | None] = mapped_column(String(64))
    is_system_record: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    hosted_zone: Mapped[HostedZone] = relationship(back_populates="records")
    values: Mapped[list["DnsRecordValue"]] = relationship(
        back_populates="record",
        cascade="all, delete-orphan",
        order_by="DnsRecordValue.position",
    )
    __table_args__ = (
        CheckConstraint(
            "record_type IN ('A','AAAA','CNAME','TXT','MX','NS','PTR','SRV','CAA','SOA')",
            name="ck_record_type",
        ),
        UniqueConstraint(
            "hosted_zone_id",
            "name",
            "record_type",
            "routing_policy",
            "set_identifier",
            name="uq_record_identity",
        ),
        Index("ix_records_zone_name_type", "hosted_zone_id", "name", "record_type"),
        Index("ix_records_zone_type", "hosted_zone_id", "record_type"),
    )


class DnsRecordValue(Base):
    __tablename__ = "dns_record_values"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_id)
    record_id: Mapped[str] = mapped_column(
        ForeignKey("dns_records.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    record: Mapped[DnsRecord] = relationship(back_populates="values")
    __table_args__ = (
        UniqueConstraint("record_id", "position", name="uq_record_value_position"),
    )
