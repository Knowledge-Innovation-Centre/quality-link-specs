# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Specifications for the EU [QualityLink](https://quality-link.eu/) project. Three artifact kinds live side-by-side:

1. **Bikeshed-authored specs** at the repo root (`.bs` → `.html`) — the actual deliverables.
2. **QualityLink ontology and application profile** are contained in `resources/ontology-shacl.ttl`
2. **`content_negotiation/`** — a small FastAPI service deployed separately (Coolify, via its `Dockerfile`/`docker-compose.yml`). It redirects requests to the static `specs.quality-link.eu/resources/<base>.<ext>` URLs based on the `Accept` header. Not part of the spec build.

## Building specs locally

```sh
python3 -m venv venv && . venv/bin/activate && pip install bikeshed
make                       # build all specs listed in the Makefile
bikeshed spec foo.bs       # build a single spec
```

`make` opens the generated HTML via `open`. Generated `*.html` and `*.pdf` are gitignored — never commit them; the CI workflow publishes them to the `gh-pages` branch.

## Specs and shared includes

Each `.bs` file (`template.bs`, `data_exchange.bs`, `discovery.bs`, `policy.bs`, `course_identifier.bs`) is a standalone spec but pulls in:

- `defaults.include` — shared Bikeshed metadata (logo, repo link, warning text, version label, text macros like `[HEI]`). **Bump the alpha version string and warning text here**, not per-spec.
- `header.include` — HTML `<head>` boilerplate including the Matomo analytics snippet.
- `concepts.include` — shared term definitions (`<dfn>`s like `learning opportunity`, `HEI`, `aggregator`) referenced via `[=term=]` across specs. New cross-spec terminology goes here.
- `biblio.json` — custom bibliography entries (cross-spec refs use shortnames like `QL-EXCH`, `QL-DISCO`, `QL-ONT`).
- `copyright.include` — copyright boilerplate.

When adding a new spec: register it in the `Makefile` and in `.github/workflows/auto-publish.yml`'s matrix, and add a `biblio.json` entry if other specs will reference it.

## Ontology and SHACL (`resources/`)

`resources/ontology-shacl.ttl` is the authoring source for the QualityLink ontology + SHACL application profile (extends ELM/LOQ). Only the Turtle is hand-edited. CI derives everything else:

- `rdflib` converts `*.ttl` → `.json` (JSON-LD), `.rdf` (RDF/XML), `.nt` (N-Triples).
- [SHACL Play](https://github.com/sparna-git/shacl-play) generates `*.html` SHACL documentation (with Graphviz diagrams).
- [WIDOCO](https://github.com/dgarijo/Widoco) generates ontology HTML docs, published as `resources/ontology.html` (plus `ontology.{ttl,json,jsonld,owl,xml,nt}` aliases of `ontology-shacl.*`).

Do not commit derived artifacts — they're regenerated on every push to `main`.

`reference/` (gitignored) holds upstream LOQ/ELM Turtle/RDF files for local reference only.

## Publishing pipeline (`.github/workflows/auto-publish.yml`)

Runs on push to `main` (touching specs/includes/ontology) and on PRs. Two jobs:

1. **main** — builds each `.bs` with `w3c/spec-prod@v2`, deploys to `gh-pages`. Sets each spec's displayed date to the last commit date of its `.bs` file (not the build date).
2. **copy-resources** — runs the rdflib/SHACL Play/WIDOCO conversions above and commits the outputs to `gh-pages` under `resources/`.

The published `specs.quality-link.eu` site is the `gh-pages` branch fronted by the content-negotiation service for clean URLs like `/ontology/v1` (mapped in `content_negotiation/main.py`'s `PATH_MAP`).
