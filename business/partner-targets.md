# partner-targets.md

> Integration roadmap for AnimeMetaFix. Ordered by **build-now → build-later**. Effort: S = <1 wk, M = 1–3 wk, L = >3 wk. Affiliate/rev-share flagged 💰.

## Strategic note
Anime metadata is a *fragmentation* problem: no single source is correct, and the canonical IDs (AniDB) are mutually inconsistent with the IDs Jellyfin/Plex actually store (TVDB/TMDB). AnimeMetaFix's defensible job is **cross-mapping + AI disambiguation of absolute-vs-seasonal episode ordering** — the #1 anime pain on self-hosted servers. So the metadata-source APIs below are not "nice integrations," they ARE the product's raw material. The affiliate money is *downstream* in infra/seedbox, not in the metadata DBs.

---

## Tier 1 — Core, ship in MVP

### 1. AniList (GraphQL API) — **S** 💰(indirect)
- **Free tier:** 90 req/min, no key required for public data; OAuth only for user lists. No hard monthly cap.
- **Value-add / user job:** "Give me the *correct* title, synonyms, season, air-date, and relations." Best-structured anime metadata with romaji/english/native + `relations` graph (sequel/prequel/side-story) — this is what drives correct **reordering**.
- **Why first:** Cleanest schema, generous limits, large fan base = goodwill. No revenue-share but partner-listing in their app directory drives free installs.
- **Effort note:** GraphQL means one query gets titles+relations+episodes; ~3 days incl. caching layer.

### 2. AniDB (HTTP/UDP API) — **L**
- **Free tier:** Hard-throttled. UDP API: 1 packet / 2 sec, 4-sec flood limit, mandatory client registration (`clientname`/`clientver`). HTTP API ~1 req/2s. Ban-happy.
- **Value-add:** The *only* DB with **per-file ED2K hash → exact episode** mapping (via the AVDump/Shoko ecosystem). Solves "which exact release/version is this file." This is the killer feature competitors lack.
- **Why critical but later:** Aggressive rate limits force a server-side queue + local cache (legally you must cache, not re-query). High effort; do it once Tier-1 cross-mapping proves demand.

### 3. TheMovieDB (TMDB) — **S** 💰(indirect)
- **Free tier:** Free API key, ~50 req/sec effective, unlimited monthly. Attribution required.
- **Value-add:** TMDB is the **default Jellyfin 10.9+ anime agent**. Most users' libraries are *already* keyed to TMDB IDs — you must read/write what they have to "fix in place" rather than force re-scan.
- **Effort:** Trivial REST, ~2 days.

### 4. TheTVDB — **M** 💰
- **Free tier:** API is now **paid/subscription** for commercial use (~$12/yr user-supported key; negotiated keys for apps). v4 API.
- **Value-add:** TVDB stores the **absolute-vs-aired ordering** that breaks long-running shonen (One Piece, Detective Conan). Reading TVDB's `seasonType` is essential to *detect* the misorder you're fixing.
- **💰 angle:** TheTVDB runs a partner/affiliate-style negotiated-key program for apps that drive subscriptions — pursue a co-marketing key; users you onboard often buy TVDB sub.

---

## Tier 2 — Write-back & ecosystem (v1.1)

### 5. Jellyfin / Emby / Plex Server APIs — **M** (Jellyfin S, Plex M)
- **Free tier:** Self-hosted, no API cap (Jellyfin/Emby fully open; Plex needs `X-Plex-Token`, Plex Pass not required for metadata writes).
- **Value-add:** This is the **write side** — push corrected metadata back without a full library rescan. Jellyfin plugin is the lowest-friction distribution channel (one-click install from repo) → make AnimeMetaFix a **Jellyfin plugin first**, SaaS second.
- **Effort:** Jellyfin REST is clean (~4 days). Plex's token+section model adds ~1 wk. Build Jellyfin first; it's the stated target and the most metadata-broken.

### 6. Shoko Server — **M**
- **Free tier:** Open-source, local, unlimited.
- **Value-add:** Shoko already does AniDB hashing + file management for hardcore anime hoarders. Integrating as a Shoko **metadata-enrichment plugin** instantly targets the highest-willingness-to-pay segment (people who already self-host a dedicated anime stack). Don't compete with Shoko — *sit on top of it*.

---

## Tier 3 — Monetization & growth infra

### 7. Lemon Squeezy (or Paddle) — **S** 💰(MoR)
- **Free tier:** No monthly fee; ~5% + 50¢ per transaction (merchant-of-record handles global VAT/sales tax).
- **Value-add:** Billing + license-key issuance for the paid tier. MoR removes tax compliance burden for a solo/small founder selling globally to anime hobbyists.
- **Why over Stripe:** MoR tax handling is worth the higher % at this scale; license-key API is built-in (Stripe needs you to build it).

### 8. Seedbox / VPS referral programs (Ultra.cc, RapidSeedbox, Hetzner, DigitalOcean) — **S** 💰(highest rev-share)
- **Free tier:** N/A — these are *affiliate* targets, not technical integrations.
- **Value-add:** Your entire user base self-hosts media. Seedbox/VPS referral programs pay **20–50% recurring** (RapidSeedbox ~20% recurring; Ultra.cc affiliate; Hetzner/DO ~$25–100 one-off credit). A "Recommended hosting for your Jellyfin + AnimeMetaFix stack" page is near-zero effort and the **only meaningful recurring affiliate revenue** in this niche.
- **💰 Prioritize this:** metadata DBs won't pay you; the infra under your users will.

---

## Build order (TL;DR)
1. **AniList + TMDB** (read) → prove cross-mapping (S, ~1 wk total)
2. **Jellyfin plugin write-back** (M) → distribution channel
3. **TheTVDB** ordering detection + negotiated 💰 key (M)
4. **Lemon Squeezy** paywall (S) + **seedbox affiliate page** 💰 (S) — ship together to monetize day 1
5. **AniDB + Shoko** (L) → moat features for power users / higher tier

**Revenue-share reality check:** the metadata APIs are cost centers (rate limits, attribution, TVDB sub). Real partner $ = **seedbox/VPS affiliates (recurring 20–50%)** + **TVDB co-marketing**. Everything else is product fuel.