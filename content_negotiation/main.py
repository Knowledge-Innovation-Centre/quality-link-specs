import os
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, PlainTextResponse
from urllib.parse import urljoin
from accept_types import get_best_match

app = FastAPI()

SPECS_BASE_URL = os.environ.get("SPECS_BASE_URL", "https://specs.quality-link.eu/resources")

# Mapping

# Content types to resource paths for a given base name
RESOURCE_MAP = {
    "text/turtle": "{}.ttl",
    "text/plain": "{}.ttl",
    "application/rdf+xml": "{}.rdf",
    "application/xml": "{}.rdf",
    "text/xml": "{}.rdf",
    "application/ld+json": "{}.json",
    "application/json": "{}.json",
    "application/n-triples": "{}.nt",
    "text/html": "{}.html",
    "*/*": "{}.html",
}

# Path to resource mappings
PATH_MAP = {
    "ontology/v1": "ontology",
}


class NoSuitableRepresentation(Exception):
    """
    Signals that no suitable representation could be determined
    """
    pass


def negotiate_content(accept_header: str, path: str) -> str | None:
    """
    Find the best matching resource path based on Accept header.
    """
    if return_type := get_best_match(accept_header, RESOURCE_MAP.keys()):
        return RESOURCE_MAP[return_type].format(path)
    elif "*/*" in RESOURCE_MAP:
        return RESOURCE_MAP["*/*"].format(path)
    else:
        raise NoSuitableRepresentation


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.api_route("/{path:path}", methods=["GET", "OPTIONS"])
async def content_negotiation(request: Request, path: str):
    # Strip trailing slashes and default to index
    path = path.rstrip("/")
    if path == '':
        path = 'index'

    # Handle OPTIONS for CORS
    if request.method == "OPTIONS":
        return PlainTextResponse(
            "",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Accept",
            },
        )

    accept_header = request.headers.get("accept", "*/*")

    # Deny a path that might be an absolute URL
    if '//' in path:
        return PlainTextResponse(
            "No absolute URL in path allowed.",
            status_code=400,
            headers={"Access-Control-Allow-Origin": "*"},
        )

    # Determine redirect location
    try:
        location = urljoin(SPECS_BASE_URL + "/", negotiate_content(accept_header, PATH_MAP.get(path, path)))
        return RedirectResponse(
            url=location,
            status_code=303,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "content-Type, accept",
                "Vary": "accept",
            },
        )
    except NoSuitableRepresentation:
        return PlainTextResponse(
            "No agreeable content type found.",
            status_code=406,
            headers={"Access-Control-Allow-Origin": "*"},
        )

