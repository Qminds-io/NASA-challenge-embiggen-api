from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import models


class UserRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_token_hash(self, token_hash: str) -> Optional[models.UserModel]:
        stmt = select(models.UserModel).where(models.UserModel.api_token_hash == token_hash)
        return self.session.execute(stmt).scalar_one_or_none()

    def ensure_users(self, *users: models.UserModel) -> None:
        if not users:
            return
        for user in users:
            exists = (
                self.session.execute(
                    select(models.UserModel.id).where(models.UserModel.username == user.username)
                ).scalar_one_or_none()
            )
            if exists is None:
                self.session.add(user)
        self.session.commit()
