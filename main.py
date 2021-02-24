import time
import logging
from tabulate import tabulate
import os
from os import path

# from starlette.middleware.gzip import GZipMiddleware
from fastapi import FastAPI
from fastapi import APIRouter
from sentry_asgi import SentryMiddleware
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import FileResponse, Response, StreamingResponse
from starlette.staticfiles import StaticFiles
import httpx

# from dispatch.conference.models import Conference  # noqa lgtm[py/unused-import]
# from dispatch.team.models import TeamContact  # noqa lgtm[py/unused-import]
# from dispatch.conversation.models import Conversation  # noqa lgtm[py/unused-import]
# from dispatch.definition.models import Definition  # noqa lgtm[py/unused-import]
# from dispatch.document.models import Document  # noqa lgtm[py/unused-import]
# from dispatch.event.models import Event  # noqa lgtm[py/unused-import]
# from dispatch.group.models import Group  # noqa lgtm[py/unused-import]
# from dispatch.incident.models import Incident  # noqa lgtm[py/unused-import]
# from dispatch.incident_priority.models import IncidentPriority  # noqa lgtm[py/unused-import]
# from dispatch.incident_type.models import IncidentType  # noqa lgtm[py/unused-import]
# from dispatch.individual.models import IndividualContact  # noqa lgtm[py/unused-import]
# from dispatch.participant.models import Participant  # noqa lgtm[py/unused-import]
# from dispatch.participant_role.models import ParticipantRole  # noqa lgtm[py/unused-import]
# from dispatch.policy.models import Policy  # noqa lgtm[py/unused-import]
# from dispatch.route.models import (
#     Recommendation,
#     RecommendationAccuracy,
# )  # noqa lgtm[py/unused-import]
# from dispatch.service.models import Service  # noqa lgtm[py/unused-import]
# from dispatch.status_report.models import StatusReport  # noqa lgtm[py/unused-import]
# from dispatch.storage.models import Storage  # noqa lgtm[py/unused-import]
# from dispatch.tag.models import Tag  # noqa lgtm[py/unused-import]
# from dispatch.task.models import Task  # noqa lgtm[py/unused-import]
# from dispatch.term.models import Term  # noqa lgtm[py/unused-import]
# from dispatch.ticket.models import Ticket  # noqa lgtm[py/unused-import]
# from dispatch.plugin.models import Plugin  # noqa lgtm[py/unused-import]

# from .api import api_router
# from .config import STATIC_DIR
# from .database import SessionLocal
# from .metrics import provider as metric_provider
# from .logging import configure_logging
# from .extensions import configure_extensions
# from .common.utils.cli import install_plugins, install_plugin_events

api_router = APIRouter()  # WARNING: Don't use this unless you want unauthenticated routes
authenticated_api_router = APIRouter()

log = logging.getLogger(__name__)

app = Starlette()
frontend = Starlette()

api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

api.include_router(api_router, prefix="/v1")

# if STATIC_DIR:
#     frontend.mount("/", StaticFiles(directory=STATIC_DIR), name="app")

app.mount("/api", app=api)
app.mount("/", app=frontend)
