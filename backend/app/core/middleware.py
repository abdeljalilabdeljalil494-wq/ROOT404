"""HTTP hardening middleware: response security headers + request body cap.

* ``SecurityHeadersMiddleware`` — defence-in-depth headers on every response.
* ``BodySizeLimitMiddleware`` — rejects oversized request bodies (413) based
  on Content-Length before the handler reads them.
"""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

#: Applied to every API response. CSP for the HTML app lives in
#: frontend/nginx.conf (different surface, different policy).
SECURITY_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cache-Control": "no-store",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        for header, value in SECURITY_HEADERS.items():
            response.headers.setdefault(header, value)
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_body_bytes: int):
        super().__init__(app)
        self.max_body_bytes = max_body_bytes

    async def dispatch(self, request: Request, call_next) -> Response:
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            if int(content_length) > self.max_body_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": (
                            f"Request body too large (limit: {self.max_body_bytes} bytes)."
                        )
                    },
                )
        return await call_next(request)
