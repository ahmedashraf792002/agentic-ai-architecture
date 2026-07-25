from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.models import EvidenceSource


def create_evidence_source(
    session: Session, system_id: int, source_type: str, location: str, description: str | None = None
) -> EvidenceSource:
    source = EvidenceSource(
        system_id=system_id, source_type=source_type, location=location, description=description
    )
    session.add(source)
    session.commit()
    session.refresh(source)
    return source


def list_evidence_sources(session: Session, system_id: int) -> list[EvidenceSource]:
    stmt = select(EvidenceSource).where(EvidenceSource.system_id == system_id)
    return list(session.execute(stmt).scalars().all())
