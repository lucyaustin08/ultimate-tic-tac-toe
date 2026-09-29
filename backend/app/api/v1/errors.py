"""Translate domain and validation errors into the project's error envelope."""

from collections.abc import Awaitable, Callable, Mapping, Sequence
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import ConcurrentWriteError, DomainError, NotFoundError, RuleViolationError

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: 404,
    RuleViolationError: 409,
    ConcurrentWriteError: 409,
}


def _envelope(status_code: int, code: str, detail: str) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "detail": detail})


def _domain_handler(status_code: int) -> Callable[[Request, Exception], Awaitable[JSONResponse]]:
    async def handle(_request: Request, exc: Exception) -> JSONResponse:
        assert isinstance(exc, DomainError)
        return _envelope(status_code, exc.code, exc.detail)

    return handle


def _describe_validation_error(error: Mapping[str, Any]) -> str:
    location: Sequence[object] = error.get("loc", ())
    path = [str(part) for part in location if part not in ("body", "path", "query")]
    field = ".".join(path) or "request"
    return f"{field}: {error.get('msg', 'is invalid')}"


async def _validation_handler(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    messages = [_describe_validation_error(error) for error in exc.errors()]
    return _envelope(422, "validation_error", "; ".join(messages) + ".")


async def _http_handler(_request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")
    return _envelope(exc.status_code, code, str(exc.detail))


def register_exception_handlers(app: FastAPI) -> None:
    for error_type, status_code in STATUS_BY_ERROR.items():
        app.add_exception_handler(error_type, _domain_handler(status_code))
    app.add_exception_handler(RequestValidationError, _validation_handler)
    app.add_exception_handler(StarletteHTTPException, _http_handler)
