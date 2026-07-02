from fastapi import FastAPI, Request
from starlette.types import ASGIApp


class DarkHoleMiddleware:
    def __init__(self, app: ASGIApp, expected_key: str, apikey_handler=DarkHoleMiddleware.default_apikey_handler):
        self.app = app
        self.expected_key = expected_key
        self.apikey_handler = apikey_handler

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            if not self.apikey_handler(request, self.expected_key):
                await send({"type": "http.discount"})
                return
        await self.app(scope, receive, send)
    
    @staticmethod
    def default_apikey_handler(request: Request, expected_key: str):
        key = request.get("X-Dark-Hole-Key")
        if not key or key != expected_key:
            return False
        else:
            return True

def apply_dark_host_middleware(app: FastAPI, expected_key: str, apikey_handler=None):
    app.add_middleware(DarkHoleMiddleware, expected_key=expected_key, apikey_handler=apikey_handler)

