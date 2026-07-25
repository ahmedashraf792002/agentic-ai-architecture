from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.models import ModelElementIndex


def upsert_model_element(
    session: Session,
    system_id: int,
    layer: str,
    archimate_type: str,
    name: str,
    git_path: str,
    current_commit: str,
) -> ModelElementIndex:
    stmt = select(ModelElementIndex).where(
        ModelElementIndex.system_id == system_id,
        ModelElementIndex.git_path == git_path,
    )
    element = session.execute(stmt).scalar_one_or_none()

    if element is None:
        element = ModelElementIndex(system_id=system_id, git_path=git_path)
        session.add(element)

    element.layer = layer
    element.archimate_type = archimate_type
    element.name = name
    element.current_commit = current_commit
    session.commit()
    session.refresh(element)
    return element


def list_model_elements(session: Session, system_id: int) -> list[ModelElementIndex]:
    stmt = select(ModelElementIndex).where(ModelElementIndex.system_id == system_id)
    return list(session.execute(stmt).scalars().all())
