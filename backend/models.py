from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class LegacySystem(Base):
    __tablename__ = "legacy_systems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class ModelElementIndex(Base):
    __tablename__ = "model_element_index"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    system_id: Mapped[int] = mapped_column(
        ForeignKey("legacy_systems.id"),
        nullable=False,
    )

    layer: Mapped[str] = mapped_column(String(100), nullable=False)
    archimate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    git_path: Mapped[str] = mapped_column(String(500), nullable=False)
    current_commit: Mapped[str] = mapped_column(String(100), nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class ArtifactVersion(Base):
    __tablename__ = "artifact_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    system_id: Mapped[int] = mapped_column(
        ForeignKey("legacy_systems.id"),
        nullable=False,
    )

    commit_sha: Mapped[str] = mapped_column(String(100), nullable=False)

    phase: Mapped[str] = mapped_column(String(100), nullable=False)
    tag: Mapped[str | None] = mapped_column(String(100))

    author_type: Mapped[str] = mapped_column(String(100), nullable=False)

    run_id: Mapped[str | None] = mapped_column(String(255))
    pr_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        unique=True,
    )
    approval_status: Mapped[str] = mapped_column(
        String(100),
        default="pending",
    )
    
    approved_by: Mapped[str | None] = mapped_column(String(255))

    approved_at: Mapped[datetime | None] = mapped_column(DateTime)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    system_id: Mapped[int] = mapped_column(
        ForeignKey("legacy_systems.id"),
        nullable=False,
    )

    phase: Mapped[str] = mapped_column(String(100), nullable=False)

    status: Mapped[str] = mapped_column(String(100), nullable=False)

    run_id: Mapped[str | None] = mapped_column(String(255))

    error_message: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime | None] = mapped_column(DateTime)

    finished_at: Mapped[datetime | None] = mapped_column(DateTime)


class EvidenceSource(Base):
    __tablename__ = "evidence_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    system_id: Mapped[int] = mapped_column(
        ForeignKey("legacy_systems.id"),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(String(100), nullable=False)

    location: Mapped[str] = mapped_column(String(500), nullable=False)

    description: Mapped[str | None] = mapped_column(Text)

    added_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
