from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from core.models.base import Base, TimestampMixin


class Tenant(TimestampMixin, Base):
    __tablename__ = "tenants"
    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'suspended', 'canceled', 'pending_deletion')", name="status"
        ),
        CheckConstraint("plan IN ('trial', 'basic', 'pro', 'enterprise')", name="plan"),
        CheckConstraint("isolation IN ('pool', 'silo')", name="isolation"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str]
    slug: Mapped[str] = mapped_column(unique=True)
    document: Mapped[str | None]
    segment: Mapped[str]
    metric_pack: Mapped[str]
    plan: Mapped[str] = mapped_column(server_default="trial")
    status: Mapped[str] = mapped_column(server_default="active")
    timezone: Mapped[str] = mapped_column(server_default="America/Sao_Paulo")
    currency: Mapped[str] = mapped_column(String(3), server_default="BRL")
    isolation: Mapped[str] = mapped_column(server_default="pool")
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
