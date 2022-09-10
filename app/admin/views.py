from aiohttp.web import HTTPForbidden
from aiohttp_apispec import request_schema, response_schema, docs
from aiohttp_session import new_session, get_session

from app.admin.models import Admin
from app.admin.schemes import AdminSchema, AdminValidationSchema
from app.web.app import View
from app.web.mixins import AuthRequiredMixin
from app.web.utils import json_response


class AdminLoginView(View):
    @docs(tags=['admin'], summary='Login admin', description='Method for login admin')
    @request_schema(AdminValidationSchema)
    @response_schema(AdminSchema)
    async def post(self):
        data = self.request['data']
        email = data['email']
        password = data['password']
        admin_from_db = await self.store.admins.get_by_email(email)

        if admin_from_db and admin_from_db.is_password_valid(password):
            session = await new_session(request=self.request)
            response = AdminSchema().dump(admin_from_db)
            session['admin'] = response
            return json_response(data=response)

        raise HTTPForbidden


class AdminCurrentView(AuthRequiredMixin, View):
    @docs(tags=['admin'], summary='Current admin', description='Method returns current admin if he already log in')
    @response_schema(AdminSchema)
    async def get(self):
        session = await get_session(self.request)
        try:
            admin_email = Admin.from_session(session).email
        except KeyError:
            return json_response()
        admin_from_db = await self.request.app.store.admins.get_by_email(admin_email)
        admin = AdminSchema().dump(admin_from_db)
        return json_response(data=admin)
