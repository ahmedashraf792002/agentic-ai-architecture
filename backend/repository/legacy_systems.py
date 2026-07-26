from sqlalchemy.orm import Session

from backend.models import LegacySystem


def create_legacy_system(
    session: Session, name: str, description: str | None = None
) -> LegacySystem:
    system = LegacySystem(name=name, description=description)
    session.add(system)
    session.commit()
    session.refresh(system)
    return system


def get_legacy_system(session: Session, system_id: int) -> LegacySystem | None:
    return session.get(LegacySystem, system_id)
