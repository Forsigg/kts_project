from dataclasses import dataclass
from hashlib import sha256
from typing import Optional

from sqlalchemy import Column, BigInteger, String

from app.store.database.sqlalchemy_base import db


@dataclass
class Admin:
    email: str
    id: Optional[int] = None
    password: Optional[str] = None

    def is_password_valid(self, password: str):
        return self.password == sha256(password.encode()).hexdigest()

    @classmethod
    def from_session(cls, session: Optional[dict]) -> Optional["Admin"]:
        return cls(id=session["admin"]["id"], email=session["admin"]["email"])


class AdminModel(db):
    __tablename__ = "admins"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)

    def to_dc(self):
        return Admin(id=self.id, email=self.email, password=self.password)

    def __str__(self):
        return f"Admin: id={self.id}, email={self.email}, password={self.password}"
