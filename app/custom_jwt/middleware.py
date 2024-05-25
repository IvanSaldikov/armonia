from channels.auth import UserLazyObject
from channels.db import database_sync_to_async
from config.logger import get_module_logger
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

logger = get_module_logger(__name__)


class SessionWrapper:
    """Wrapper is needed to SimpleJWT authorization works with scope instead of request object"""

    META: dict

    def __init__(self, headers, cookies):
        self.META = headers
        self.COOKIES = cookies


@database_sync_to_async
def jwtauth(scope):
    auth = JWTCookieAuthentication()
    # decode headers into dict with HTTP_ and uppercase
    auth_dict = {
        "HTTP_" + h[0].decode("iso-8859-1").upper(): h[1].decode("iso-8859-1")
        for h in scope["headers"]
    }
    sw = SessionWrapper(auth_dict, cookies=scope.get("cookies"))
    return auth.authenticate(sw)


class JWTAuthMiddleware:
    """JWT Authorization middleware for JWT authorization in Websockets"""

    def __init__(self, inner):
        self.inner = inner

    def populate_scope(self, scope):
        # Make sure we have a cookies key in the scope
        if "cookies" not in scope:
            raise ValueError(
                "AuthMiddleware cannot find session in scope. "
                "CookiesMiddleware must be above it."
            )
        # Add it to the scope if it's not there already
        if "user" not in scope:
            scope["user"] = UserLazyObject()

    async def resolve_scope(self, scope):
        auth_data = await jwtauth(scope)
        if auth_data is not None:
            user = auth_data[0]
            scope["user"]._wrapped = user

    async def __call__(self, scope, receive, send):
        scope = dict(scope)
        # Scope injection/mutation per this middlewares needs.
        self.populate_scope(scope)
        try:
            # Grab the finalized/resolved scope
            await self.resolve_scope(scope)
        except InvalidToken:
            logger.info("Trying to auth with invalid token in WebSockets")

        ret = None
        try:
            ret = await self.inner(scope, receive, send)
        except ValueError:
            logger.info("Path not found")
        return ret
