"""FOGIS API Client package.

This package provides a client for interacting with the FOGIS API.
"""

from fogis_api_client.event_types import EVENT_TYPES
from fogis_api_client.fogis_api_client import (
    FogisApiClient,
    FogisAPIRequestError,
    FogisDataError,
    FogisLoginError,
)
from fogis_api_client.types import (
    CookieDict,
    EventDict,
    MatchDict,
    MatchListResponse,
    MatchResultDict,
    OfficialActionDict,
    OfficialDict,
    PlayerDict,
    TeamPlayersResponse,
)

__all__ = [
    "FogisApiClient",
    "FogisLoginError",
    "FogisAPIRequestError",
    "FogisDataError",
    "EVENT_TYPES",
    "CookieDict",
    "EventDict",
    "MatchDict",
    "MatchListResponse",
    "MatchResultDict",
    "OfficialActionDict",
    "OfficialDict",
    "PlayerDict",
    "TeamPlayersResponse",
]
