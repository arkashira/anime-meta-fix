Generated `tech-spec.md`:

# AnimeMetaFix — Technical Specification (v1)

> Scope: self-hosted media-server metadata correction for anime collections. v1 targets **Jellyfin** first (largest self-host anime overlap), with a Plex adapter behind the same interface for v1.1. Single-tenant agent + hosted control plane.

---

## 1. Stack

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.12** | Best ecosystem for AniDB/AniList/TMDB clients, `guessit`/`anitopy` filename parsers, LLM SDKs. |
| API framework | **FastAPI 0.115 + Uvicorn** | Async (heavy I/O against external metadata APIs), auto OpenAPI, Pydantic v2. |
| Background jobs | **arq** (Redis-backed) | Scan/match/write are long-running; lighter than Celery, async-native. |
| Local agent | **Python single binary** (PyInstaller) + Docker image | Runs beside Jellyfin, holds the only Jellyfin API key, outbound-only. |
| LLM | **Claude Haiku 4.5** for disambiguation; escalate to **Sonnet 4.6** on confidence <0.6 | Haiku handles 90%+ at ~1/10th cost. |
| Matching core | `anitopy` → AniList GraphQL + AniDB → pgvector similarity → LLM tiebreak | Deterministic-first, LLM-last. |
| Frontend | **Next.js 14 + Tailwind + shadcn/ui** | Review/approve dashboard. |
| DB | **Postgres 16 + pgvector** | Reuse company BRAIN pattern. |
| Cache/queue | **Redis 7** | arq queue + external-API response cache. |

**Hard rule:** writes never auto-apply without a dry-run diff the user approves, unless opted into auto-apply per-library.

## 2. Hosting (free-tier-first)

| Component | Platform | Free tier |
|---|---|---|
| Control-plane API | **Fly.io** (shared-cpu-1x, 256MB) | 3 VMs free |
| Postgres + pgvector | **Neon** | 0.5GB, autosuspend |
| Redis | **Upstash** | 256MB, 500K cmd/day |
| Dashboard | **Vercel** Hobby | yes |
| Local agent | **Self-hosted (user's Docker)** | $0 to us |
| Artwork storage | **Cloudflare R2** | 10GB, no egress |
| Email | **Resend** | 3K/mo |

Cost at 0–50 users: **$0/mo**. First paid line: Vercel Pro ($20) at commercial launch.

## 3. Data Model

Tables: `users`, `agents`, `agent_tokens` (argon2), `libraries` (auto_apply, confidence_threshold default 0.85), `media_items` (current_meta jsonb, detected_issues, status), `corrections` (field/old/new/source/confidence/state), `match_cache` (TTL-aware), `title_embeddings` (vector(1024)), `audit_log`.

**Invariant:** control plane stores `path_hash` (SHA-256) + metadata only — never raw paths or media bytes.

## 4. API Surface

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/agents/enroll` | One-time code → agent token |
| POST | `/v1/agents/heartbeat` | Liveness + version; returns pending commands |
| POST | `/v1/scan/batch` | Agent uploads items for matching |
| GET | `/v1/items/{id}/corrections` | Proposed corrections + confidence |
| POST | `/v1/items/{id}/corrections/resolve` | Approve/reject |
| GET | `/v1/libraries/{id}/diff` | Dry-run diff before apply |
| POST | `/v1/libraries/{id}/apply` | Mark approved corrections ready |
| GET | `/v1/agents/{id}/commands` | Long-poll write queue for agent |
| POST | `/v1/match/resolve` | Stateless single-title resolution |
| GET | `/v1/libraries/{id}/report` | Scan/flag/fix summary |

Matching is server-side; **writes happen agent-side** (control plane never holds the Jellyfin key).

## 5. Security Model

- **Agent auth:** enrollment-code → argon2-hashed long-lived token, scoped + revocable.
- **Dashboard auth:** magic-link → 15-min JWT + httpOnly refresh cookie. No passwords.
- **Trust boundary:** Jellyfin key never leaves user's machine; agent is outbound-only (no inbound ports, NAT-friendly).
- **Secrets:** Fly/Vercel env; agent token in OS keyring or `0600` file.
- **IAM:** Neon role split (`app_rw` no-DDL / `migrations` DDL-only); R2 token scoped to one bucket.
- **Data minimization:** no media bytes, hashed paths, no server-side credentials.
- **Rate-limit:** per-agent 60 req/min; external calls gated through `match_cache` to honor AniDB ToS (1 req/2s).

## 6. Observability

- **Logs:** `structlog` JSON → Better Stack free (1GB/mo); correlation ID per scan batch.
- **Metrics** (`/metrics`, Grafana Cloud free): `match_confidence_histogram`, `corrections_proposed_total{source}`, `llm_escalation_ratio` (alert >15%), `external_api_errors_total{provider}` (AniDB-ban detector), `agent_heartbeat_age_seconds`.
- **Traces:** OTel → Grafana Tempo; spans `scan → match → llm_tiebreak → propose`; 100% sampling <1K req/day, then 10%.
- **Alerts:** escalation-ratio breach, AniDB error spike, agent offline >24h.

## 7. Build / CI

- **Monorepo:** `/control-plane`, `/agent`, `/dashboard` (uv + pnpm workspaces).
- **GitHub Actions:** `lint` (ruff/mypy/eslint/tsc) → `test` (pytest ≥80% on matching core, Vitest, ephemeral Neon branch DB) → `build` (Docker + PyInstaller matrix incl. arm64 for Raspberry Pi) → `migrate-check` (alembic dry-run).
- **Release:** tag → GH Release with agent binaries + `docker pull`; control plane auto-deploys to Fly on `main`, dashboard to Vercel.
- **Security:** Dependabot + `pip-audit`/`npm audit` gate; Trivy scan on agent image.
- **Versioning:** agent reports `agent_version` on heartbeat; control plane rejects incompatible majors and returns an upgrade command.

---

Saved to `/tmp/tech-spec.md`. The architecturally load-bearing decision here: a **split agent/control-plane** model where the Jellyfin API key and all writes stay on the user's box — this dodges the inbound-networking and credential-custody problems that kill most "managed self-hosted" tools, and keeps us at $0 infra until commercial launch.