from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import join, select

from .sql import models


def add_test_to_group(db: Session, test_id: int, test_group_id: int) -> None:
    cdpb_test_in_group = models.TestInTestGroup(test_group_id, test_id)
    db.add(cdpb_test_in_group)
    db.commit()
    db.refresh(cdpb_test_in_group)
    return


def id2finished(db: Session, test_group_id: int) -> bool:
    j = join(
        models.CDPBTest,
        models.TestInTestGroup,
        models.TestInTestGroup.test_id == models.CDPBTest.id,
    )
    stmt = (
        select(models.CDPBTest.result)
        .select_from(j)
        .where(models.TestInTestGroup.test_group_id == test_group_id)
    )
    tests_finished = db.execute(stmt).scalars().all()
    return all(tests_finished)


def test_group_id2test_ids(db: Session, test_group_id: int) -> List[int]:
    stmt = select(models.TestInTestGroup.test_id).where(
        models.TestInTestGroup.test_group_id == test_group_id
    )
    return db.execute(stmt).scalars().all()
