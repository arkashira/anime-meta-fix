# dataflow.md — AnimeMetaFix System Dataflow Architecture

## Top-level block diagram

```
                         ┌─────────────────────────── AUTH BOUNDARY: Public Internet ───────────────────────────┐
                         │                                                                                       │
 ┌──────────────────┐   │   ┌──────────────────┐                                                                │
 │ EXTERNAL SOURCES │   │   │  INGESTION LAYER  │                                                                │
 ├──────────────────┤   │   ├──────────────────┤                                                                │
 │ Jellyfin/Emby/   │───┼──▶│ Agent (LAN-side)  │── mTLS ──┐                                                     │
 │ Plex REST APIs   │   │   │ + Webhook listener │          │                                                     │
 │ (user's server)  │   │   └──────────────────┘          │                                                     │
 │                  │   │                                   ▼                                                     │
 │ AniDB / AniList /│   │   ┌──────────────────────────────────────┐   ┌─────────────────────────────────────┐ │
 │ TMDB / TVDB /    │───┼──▶│  API Gateway + AuthN/AuthZ (OAuth2/   │   │      PROCESSING / TRANSFORM         │ │
 │ Kitsu metadata   │   │   │  API-key, rate-limit, tenant routing) │──▶│ ┌─────────────────────────────────┐ │ │
 │                  │   │   └──────────────────────────────────────┘   │ │ Match resolver (fuzzy + embed)  │ │ │
 │ Filename / NFO / │   │                  │                            │ │ LLM disambiguator (season/order)│ │ │
 │ folder structure │───┼──────────────────┘                            │ │ Anitomy filename parser         │ │ │
 └──────────────────┘   │                                               │ │ Conflict/confidence scorer      │ │ │
                         │   ╔═══════════ AUTH BOUNDARY: VPC ═══════════╗ │ │ Human-in-loop gate (<thresh)    │ │ │
                         │   ║                                          ║ │ └─────────────────────────────────┘ │ │
                         │   ║  ┌────────────────┐  ┌────────────────┐ ║ └─────────────────────────────────────┘ │
                         │   ║  │  STORAGE TIER  │  │ QUERY / SERVING │ ║                  │                      │
                         │   ║  ├────────────────┤  ├────────────────┤ ║◀─────────────────┘                      │
                         │   ║  │ Postgres(meta) │  │ REST/GraphQL    │ ║                                         │
                         │   ║  │ pgvector(embed)│◀▶│ Diff/preview API│ ║── signed writes ──▶ back to Jellyfin    │
                         │   ║  │ S3(NFO/artwork)│  │ Job status SSE  │ ║                     (EGRESS)            │
                         │   ║  │ Redis(queue)   │  └────────────────┘ ║                       │                 │
                         │   ║  └────────────────┘                     ║                       ▼                 │
                         │   ╚══════════════════════════════════════════╝              ┌──────────────┐         │
                         │                                                              │ EGRESS / USER│         │
                         └──────────────────────────────────────────────────────────▶ │ Web dashboard│         │
                                                                                        │ + Agent apply│         │
                                                                                        └──────────────┘         │
```

## 1. External data sources
- **User media servers** — Jellyfin (primary), Emby, Plex, Kodi: library items, existing metadata, file paths, season/episode mappings. Pulled via server REST API + optional webhooks (`library.new`, `item.updated`).
- **Canonical anime metadata providers** — AniDB (gold for episode ordering), AniList GraphQL, Kitsu, TMDB, TheTVDB. Used for title canonicalization, alt-titles, airing order vs. DVD vs. absolute numbering.
- **Local filesystem signals** — filenames (release-group tags, `[SubsPlease] Show - 01v2`), folder hierarchy, existing `.nfo`/`movie.nfo`/`tvshow.nfo`, embedded container tags (MKV chapters/titles).
- **User feedback corpus** — accepted/rejected corrections (becomes training signal; see Processing).
- **Auth note:** all provider calls go out from the VPC egress, never from the LAN agent — keeps third-party API keys server-side, off the user's box.

## 2. Ingestion layer
- **LAN-side Agent** (Docker sidecar / binary): the only component with network access to the user's Jellyfin. Reads library, streams candidate items, writes approved changes back. Holds a short-lived per-tenant token, never the upstream provider keys.
- **Webhook listener**: receives Jellyfin library events for incremental sync; falls back to scheduled full-scan (default 24h).
- **API Gateway + AuthN/AuthZ**: terminates TLS, validates OAuth2 (dashboard users) or scoped API key (agent), enforces per-tenant rate limits, routes to tenant-isolated queue partition.
- **Normalizer**: collapses each source item into a canonical `MediaItem` envelope (provider-agnostic schema) and Anitomy-parses filenames at intake.
- **Auth boundary:** Internet → Gateway is the **first trust boundary**. mTLS pins the Agent↔Gateway channel so a leaked dashboard token can't impersonate an agent.

## 3. Processing / transform layer
- **Match resolver**: hybrid fuzzy string match (RapidFuzz) + semantic similarity over title embeddings (pgvector cosine) to map local item → canonical anime ID.
- **Order/season disambiguator (LLM)**: resolves the hard cases — split-cours, absolute vs. seasonal numbering, OVAs/specials, recaps — using AniDB ordering as ground truth, LLM only for ambiguous tie-breaks (bounded, cached prompts).
- **Confidence/conflict scorer**: assigns 0–1 confidence per field; ≥0.92 auto-apply, 0.70–0.92 → human-in-loop queue, <0.70 → flag/skip.
- **Human-in-loop gate**: low-confidence corrections held for dashboard approval; decisions feed the feedback corpus.
- **Artwork/NFO generator**: builds corrected `.nfo`, fetches/normalizes posters & banners.
- **Auth note:** LLM and provider calls run inside the VPC under a service identity; user PII (paths, server IP) is hashed before any LLM call — no raw library paths leave the boundary.

## 4. Storage tier *(inside VPC trust boundary)*
- **Postgres** — canonical `MediaItem`, proposed corrections, audit log, tenant config, per-field provenance.
- **pgvector** — title/synopsis embeddings for semantic match + dedup of near-identical entries.
- **Object store (S3-compatible)** — generated NFOs, artwork, dry-run diffs (lifecycle-expired after apply).
- **Redis** — per-tenant job queue, rate-limit counters, SSE pub/sub for live job status.
- **Auth boundary:** storage reachable only from Processing/Serving service roles via IAM/least-privilege; row-level tenant isolation enforced in Postgres (RLS) so one tenant's query can never read another's.

## 5. Query / serving layer
- **REST/GraphQL API**: dashboard reads corrections, library state, history.
- **Diff/preview API**: returns before→after per item (dry-run is the default; nothing is written without explicit accept or auto-apply policy).
- **Job status (SSE)**: streams scan/correction progress to dashboard and agent.
- **Auth boundary:** every serving call re-validated at Gateway against tenant scope; no direct DB exposure.

## 6. Egress to user
- **Write-back to media server**: approved corrections pushed by the LAN Agent via signed, idempotent change-sets (rollback bundle stored before write).
- **Web dashboard**: review queue, diffs, accept/reject/bulk-apply, history & undo.
- **Notifications**: webhook/email/Discord on batch completion or conflicts needing review.
- **Auth boundary:** write-back leaves the VPC only as a signed instruction to the **already-authenticated Agent** — the cloud never holds direct write credentials to the user's Jellyfin, preserving the self-hosted trust model.