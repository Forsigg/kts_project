import typing as tp
from hashlib import sha256

from sqlalchemy import select, insert

from app.admin.models import Admin, AdminModel
from app.base.base_accessor import BaseAccessor

if tp.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def get_by_email(self, email: str) -> tp.Optional[Admin]:
        async with self.app.database.session.begin() as session:
            query = select(AdminModel).where(AdminModel.email == email)
            admin = await session.execute(query)
            admin = admin.fetchone()

        if admin:
            return admin[0]
        else:
            return None

    async def create_admin(self, email: str, password: str) -> Admin:
        async with self.app.database.session.begin() as session:
            passw = sha256(password.encode()).hexdigest()
            admin = Admin(email=email, password=passw)
            await session.execute(insert(AdminModel).values(email=admin.email, password=admin.password))
            await session.commit()

        return admin



