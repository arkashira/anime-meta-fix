`user-stories.md` generated at `/tmp/user-stories.md` — 13 stories across 4 epics.

# AnimeMetaFix — User Stories

**Roles:** Collector (curates large library), Admin (runs server for others), Viewer (non-technical consumer), Homelabber (automates everything).

## Epic 1 — Detection & Diagnosis
| ID | Story | Cx |
|----|-------|----|
| 1.1 | Collector → ranked list of metadata defects from a read-only scan | M |
| 1.2 | Collector → detect absolute-vs-season numbering (One Piece problem) | L |
| 1.3 | Admin → flag duplicate/version conflicts before tagging | M |

## Epic 2 — AI Correction & Enrichment
| ID | Story | Cx |
|----|-------|----|
| 2.1 | Collector → AI re-identify series from messy fansub names (romaji/EN/native) | L |
| 2.2 | Viewer → correct episode order + specials placement (broadcast/chronological) | M |
| 2.3 | Collector → enrich art, synopsis, genres, studio | M |

## Epic 3 — Integration & Automation
| ID | Story | Cx |
|----|-------|----|
| 3.1 | Homelabber → native Jellyfin API/plugin write-in-place | L |
| 3.2 | Admin → multi-server (Plex/Emby) via adapter | M |
| 3.3 | Homelabber → scheduled + watch-folder automation w/ notifications | M |

## Epic 4 — Trust, Review & Control
| ID | Story | Cx |
|----|-------|----|
| 4.1 | Collector → dry-run before/after diff | S |
| 4.2 | Collector → selective approval + field locks | M |
| 4.3 | Admin → one-click rollback w/ snapshots | M |
| 4.4 | Admin → audit log + confidence transparency | S |

**Design choices worth flagging for the next stage (PRD/architect):**
- **Epic 4 is deliberately heavy.** The differentiated risk here isn't matching accuracy — it's that an AI write-loop can silently corrupt a curated 2,000-episode library. Dry-run, field locks, and rollback are the trust moat, not nice-to-haves.
- **The absolute-vs-season numbering story (1.2, L)** is the single hardest and most defensible feature — it's the #1 unsolved pain in r/jellyfin/r/animepiracy threads and where off-the-shelf scrapers fail. Recommend it as the wedge demo.
- **Multi-server (3.2)** is scoped behind a flag so it doesn't bloat the v1 Jellyfin-only ship.

Full acceptance criteria (3–5 bullets each) are in the file. Want me to proceed to the next pack section (PRD, pricing, or GTM)?