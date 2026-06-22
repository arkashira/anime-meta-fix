# STORIES.md

## Project: anime-meta-fix
**Goal:** Deliver a reliable, easy‑to‑use CLI that scans a media library, detects malformed or missing anime metadata, and automatically repairs or generates the correct files. The MVP must run on Windows, macOS, and Linux, be installable via `pip`, and provide clear logging and a dry‑run mode.

---

## Epics & Backlog

| Epic | Description |
|------|-------------|
| **E1 – Core Scanning & Detection** | Locate media folders, read existing metadata, and identify issues. |
| **E2 – Automatic Fixing** | Generate or correct metadata files based on detected problems. |
| **E3 – User Interaction & Safety** | Provide dry‑run, verbose logging, and interactive prompts. |
| **E4 – Configuration & Extensibility** | Allow users to customise paths, naming conventions, and external data sources. |
| **E5 – Packaging & Distribution** | Ensure pip‑installable package, CI/CD, and cross‑platform compatibility. |

---

### Epic E1 – Core Scanning & Detection

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E1‑01** | As a **user**, I want the tool to recursively scan a given root directory, so that all anime series folders are examined. | - CLI option `--path <dir>` accepts absolute or relative paths.<br>- The scan follows symbolic links **unless** `--no-follow-symlinks` is set.<br>- Output lists each discovered series folder with its depth. |
| **E1‑02** | As a **user**, I want the tool to recognise standard anime folder structures (`Season`, `Episode`, `metadata.xml/json`), so that it knows where to look for metadata. | - Detects folders matching patterns: `*/Season */Episode *` and `*/metadata.{xml,json}`.<br>- Ignores unrelated files (e.g., subtitles, thumbnails) unless `--include‑extras` is passed. |
| **E1‑03** | As a **user**, I want the tool to flag missing or malformed metadata files, so that I can see what needs fixing. | - Reports three states per series: **OK**, **MISSING**, **MALFORMED**.<br>- For malformed files, shows line/JSON path of the first parsing error.<br>- Results are written to stdout and to a machine‑readable JSON report (`--report <file>`). |
| **E1‑04** | As a **developer**, I want unit‑testable scanning functions, so that future changes stay safe. | - Core scanning logic lives in `anime_meta_fix/scanner.py` with pure functions.<br>- 90 %+ line coverage via pytest.<br>- Mock filesystem tests using `pyfakefs`. |

### Epic E2 – Automatic Fixing

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E2‑01** | As a **user**, I want the tool to automatically generate a missing metadata file from folder names, so that I get a valid file without manual editing. | - When `--fix` is supplied, missing `metadata.json` is created.<br>- Generated file contains required fields: `title`, `season`, `episode_count`, `source`, `tags`.<br>- Values are derived from folder names (e.g., `Season 2` → `season: 2`). |
| **E2‑02** | As a **user**, I want malformed metadata to be repaired (e.g., missing required keys, wrong data types), so that the file becomes valid. | - Parser loads JSON/XML, validates against a JSON‑Schema (`schema/metadata.schema.json`).<br>- Missing keys are added with sensible defaults; type mismatches are coerced when safe.<br>- A backup of the original file (`metadata.json.bak`) is saved before modification. |
| **E2‑03** | As a **user**, I want the tool to optionally fetch missing information (e.g., English title) from an external API (MyAnimeList), so that metadata is richer. | - `--fetch‑remote` triggers a call to the MyAnimeList public API (or a mock service in tests).<br>- API key can be supplied via env var `MAL_API_KEY`.<br>- Fetched fields are merged without overwriting existing user‑provided values. |
| **E2‑04** | As a **developer**, I want the fixing logic to be idempotent, so that re‑running the tool does not corrupt already‑fixed files. | - Running `anime_meta_fix --fix` twice on the same tree results in no changes after the first run (verified by checksum comparison). |

### Epic E3 – User Interaction & Safety

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E3‑01** | As a **user**, I want a dry‑run mode, so that I can see what would be changed without touching files. | - `--dry‑run` prints a summary of actions (e.g., “Would create metadata.json in /path/SeriesX”).<br>- No files are written or backed up. |
| **E3‑02** | As a **user**, I want verbose logging, so that I can troubleshoot issues. | - `--verbose` outputs step‑by‑step logs to stdout.<br>- Logs include timestamps, file paths, and action types.<br>- Log level can be set (`--log-level debug|info|warning|error`). |
| **E3‑03** | As a **user**, I want an interactive confirmation prompt before any write operation, so that I avoid accidental overwrites. | - When `--interactive` is set, the tool asks “Proceed with fixing X files? (y/N)”.<br>- Accepts `y`, `yes`, `n`, `no` (case‑insensitive). |
| **E3‑04** | As a **user**, I want the final summary to include counts of processed, fixed, and unchanged items, so I know the overall impact. | - After execution, prints: `Processed: N, Fixed: M, Skipped: K, Errors: E`. |
| **E3‑05** | As a **developer**, I want the CLI to return appropriate exit codes, so CI pipelines can react. | - `0` – success, no errors.<br>- `1` – validation errors that could not be auto‑fixed.<br>- `2` – unexpected runtime error (exception). |

### Epic E4 – Configuration & Extensibility

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E4‑01** | As a **user**, I want to store default options in a config file (`~/.anime_meta_fix.yaml`), so I don’t repeat flags each run. | - CLI reads the YAML file if present and merges with command‑line args (CLI overrides). |
| **E4‑02** | As a **user**, I want to customise the metadata schema (e.g., add `studio` field), so the tool fits my workflow. | - `--schema <path>` points to an alternate JSON‑Schema file.<br>- Validation uses the supplied schema. |
| **E4‑03** | As a **developer**, I want a plugin hook for additional data sources, so future contributors can add new APIs without touching core code. | - Plugins are Python entry‑points under `anime_meta_fix.plugins`.<br>- Example stub plugin provided in `plugins/example.py`. |
| **E4‑04** | As a **user**, I want the tool to respect a global exclude pattern (e.g., `*_old`), so unwanted folders are ignored. | - `--exclude <glob>` can be repeated; patterns are applied during scanning. |

### Epic E5 – Packaging & Distribution

| # | User Story | Acceptance Criteria |
|---|------------|----------------------|
| **E5‑01** | As a **developer**, I want the project to be installable via `pip install .`, so users can get the tool easily. | - `setup.cfg`/`pyproject.toml` defines entry‑point `anime_meta_fix = anime_meta_fix.__main__:main`.<br>- `pip install -e .` works in a virtualenv. |
| **E5‑02** | As a **devops engineer**, I want CI pipelines to run tests on Linux, macOS, and Windows, so cross‑platform quality is guaranteed. | - GitHub Actions workflow with matrix jobs for `ubuntu-latest`, `macos-latest`, `windows-latest`.<br>- Runs `pytest --cov=anime_meta_fix`. |
| **E5‑03** | As a **user**, I want the tool to display its version (`--version`) and help (`--help`), so I can verify installation. | - `--version` prints `anime-meta-fix X.Y.Z` from `__init__.__version__`.<br>- `--help` shows all options with descriptions. |
| **E5‑04** | As a **maintainer**, I want automated releases to publish wheels to PyPI, so users get binary distributions. | - Release workflow tags a commit, builds `sdist` and `wheel`, and uploads via `twine`. |

---

## MVP Scope (Stories to implement first)

1. **E1‑01**, **E1‑02**, **E1‑03** – Core scanning & detection.  
2. **E2‑01**, **E2‑02** – Automatic creation & repair of metadata.  
3. **E3‑01**, **E3‑04**, **E3‑05** – Dry‑run, summary, exit codes.  
4. **E5‑01**, **E5‑03** – Packaging, version/help.  

These eight stories deliver a functional, safe CLI that can be shipped and validated with real media libraries. Subsequent stories (E2‑03, E3‑02/03, E4‑01‑04, E5‑02/04) will be added in later sprints.
