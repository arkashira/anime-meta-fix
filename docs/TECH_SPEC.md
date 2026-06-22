# TECH_SPEC.md  

**Project:** anime-meta-fix  
**Owner:** Axentx OS – Product Engineering  
**Version:** 1.0.0 (initial release)  
**Last Updated:** 2026‑06‑22  

---  

## 1. Overview  

`anime-meta-fix` is a lightweight, cross‑platform command‑line utility that scans a media library directory tree, detects malformed or incomplete anime metadata files, and rewrites them into a canonical JSON schema.  

Key goals:  

| Goal | Success Metric |
|------|-----------------|
| **Reliability** | ≥ 99.5 % success rate on a test corpus of 10 k files |
| **Performance** | Process 1 GB of media files in ≤ 30 s on a single‑core VM |
| **Usability** | Zero‑config execution via `python -m anime_meta_fix --path <root>` |
| **Extensibility** | Plug‑in architecture for additional metadata formats (e.g., XML, YAML) |

The tool is intended for internal Ops teams and external power‑users who maintain large anime collections (e.g., Plex, Jellyfin). It is **not** a full media server; it only touches metadata files.

---  

## 2. Architecture Overview  

```
+-------------------+        +-------------------+        +-------------------+
|   CLI Entrypoint  | ----> |   Core Engine     | ----> |   Format Plugins  |
| (click / argparse) |      | (orchestrates)    |      | (JSON, XML, etc.) |
+-------------------+        +-------------------+        +-------------------+
          |                         |                           |
          v                         v                           v
   Config Loader            File Walker                Metadata Parser
          |                         |                           |
          +----------+--------------+---------------------------+
                     |
                     v
            Validation & Normalisation
                     |
                     v
               File Writer (atomic)
```

* **CLI Entrypoint** – thin wrapper built with `click`. Parses arguments, loads optional config, and forwards to the Core Engine.  
* **Core Engine** – orchestrates scanning, delegating to format plugins, applying validation rules, and writing corrected files.  
* **Format Plugins** – each plugin implements a small, well‑defined interface (`load`, `dump`, `detect`). The default plugin handles the canonical JSON schema; additional plugins can be dropped into `anime_meta_fix/plugins`.  
* **File Walker** – recursive `pathlib.Path.rglob("*")` with configurable include/exclude patterns; uses `os.scandir` for optimal directory traversal.  
* **Validation & Normalisation** – Pydantic models enforce schema, auto‑fill missing fields (e.g., `title_en`, `season_number`), and canonicalise date formats.  
* **File Writer** – writes to a temporary file then atomically renames to avoid data loss; backs up original file with `.bak` suffix (configurable).  

---  

## 3. Component Details  

### 3.1 CLI (`anime_meta_fix/__main__.py`)  

| Option | Description | Default |
|--------|-------------|---------|
| `--path <dir>` | Root of the media library (required) | – |
| `--dry-run` | Scan & report only, no writes | `False` |
| `--backup` | Keep a `.bak` copy of each modified file | `True` |
| `--threads <n>` | Number of worker threads for I/O parallelism | `4` |
| `--log-level <lvl>` | Logging verbosity (`DEBUG`, `INFO`, `WARN`, `ERROR`) | `INFO` |

Implementation uses `click.Command` with a `@click.pass_context` to inject a shared `Context` object (logger, config, thread pool).

### 3.2 Core Engine (`anime_meta_fix/engine.py`)  

* **Class:** `MetaFixEngine`
* **Public Method:** `run(root_path: Path) -> SummaryReport`
* **Internal Flow:**  

  1. Build a `ThreadPoolExecutor(max_workers=threads)`.  
  2. Submit `process_file(path)` tasks for each candidate file discovered by `FileWalker`.  
  3. Collect per‑file `FixResult` objects (status, errors, changes).  
  4. Aggregate into a `SummaryReport` printed at the end.  

* **Error handling:** All exceptions are caught, logged, and reported as `FixResult.error`. The engine never aborts the whole run because of a single bad file.

### 3.3 File Walker (`anime_meta_fix/walker.py`)  

* Uses `Path.rglob("*")` with a whitelist of extensions (`.json`, `.nfo`, `.xml`).  
* Supports an optional `.anime_meta_fixignore` file (git‑ignore‑style) for exclusion patterns.  
* Returns a generator of `Path` objects.

### 3.4 Format Plugins (`anime_meta_fix/plugins/*.py`)  

All plugins inherit from `BasePlugin`:

```python
class BasePlugin(ABC):
    @abstractmethod
    def detect(self, path: Path) -> bool: ...
    @abstractmethod
    def load(self, path: Path) -> dict: ...
    @abstractmethod
    def dump(self, data: dict, path: Path) -> None: ...
```

* **json_plugin.py** – default implementation using `json` + `orjson` for speed.  
* **xml_plugin.py** – optional, uses `defusedxml.ElementTree`.  
* **yaml_plugin.py** – optional, uses `ruamel.yaml`.  

Plugins are discovered via entry‑point `anime_meta_fix.plugins` (set in `setup.cfg`). Adding a new format is as simple as installing a package that registers the entry point.

### 3.5 Validation Model (`anime_meta_fix/schema.py`)  

Implemented with **Pydantic v2**:

```python
class AnimeMeta(BaseModel):
    id: str = Field(..., description="Unique identifier (e.g., MyAnimeList ID)")
    title: str
    title_en: Optional[str] = None
    season_number: conint(ge=1) = 1
    episode_count: conint(ge=0)
    release_date: date
    tags: List[str] = []
    description: Optional[str] = None
```

* `parse_obj` validates and coerces types.  
* Missing optional fields are filled with sensible defaults (e.g., `title_en = title`).  
* Custom validators normalise date strings (`YYYY-MM-DD`, `DD/MM/YYYY`, etc.).

### 3.6 Writer (`anime_meta_fix/writer.py`)  

* Writes to `<path>.tmp` using the same plugin’s `dump`.  
* Calls `os.replace(tmp_path, path)` for atomic replace.  
* If `backup=True`, copies original to `<path>.bak` before replace.

---  

## 4. Data Model  

| Entity | Fields | Type | Notes |
|--------|--------|------|-------|
| **AnimeMeta** | `id` | `str` | Required, external DB key |
| | `title` | `str` | Original language |
| | `title_en` | `str` | Auto‑filled if missing |
| | `season_number` | `int ≥1` | Defaults to 1 |
| | `episode_count` | `int ≥0` | |
| | `release_date` | `date` | Normalised ISO‑8601 |
| | `tags` | `list[str]` | Sorted, deduped |
| | `description` | `str` | Optional, trimmed |

All persisted files must be a JSON object matching the schema above (pretty‑printed with 2‑space indentation).  

---  

## 5. Key APIs / Interfaces  

### 5.1 Python Library API  

| Function | Signature | Description |
|----------|-----------|-------------|
| `fix_path(root: Path, *, dry_run: bool = False, backup: bool = True) -> SummaryReport` | `def fix_path(root: Path, *, dry_run: bool = False, backup: bool = True) -> SummaryReport` | High‑level entry point for programmatic use. |
| `register_plugin(plugin: BasePlugin) -> None` | `def register_plugin(plugin: BasePlugin) -> None` | Dynamically add a new format plugin at runtime. |
| `load_schema(path: Path) -> AnimeMeta` | `def load_schema(path: Path) -> AnimeMeta` | Load and validate a single metadata file. |

### 5.2 CLI Invocation  

```bash
python -m anime_meta_fix \
    --path /mnt/media/anime \
    --threads 8 \
    --log-level INFO \
    [--dry-run] [--no-backup]
```

Exit codes:  

| Code | Meaning |
|------|---------|
| 0 | All files processed, no errors |
| 1 | One or more files failed validation (non‑critical) |
| 2 | Fatal error (e.g., permission denied on root) |

---  

## 6. Technology Stack  

| Layer | Technology | Reason |
|-------|------------|--------|
| **Language** | Python 3.12 | Modern syntax, excellent stdlib, wide ecosystem |
| **CLI** | click 8.1 | Declarative, auto‑generated help |
| **Concurrency** | concurrent.futures.ThreadPoolExecutor | I/O‑bound workload, simple API |
| **Parsing / Validation** | Pydantic v2 | Fast, type‑safe, built‑in JSON support |
| **JSON Engine** | orjson (fallback to std `json`) | Highest throughput for large files |
| **XML (optional)** | defusedxml | Secure parsing |
| **YAML (optional)** | ruamel.yaml | Preserve comments if needed |
| **Logging** | structlog + standard logging | Structured logs for observability |
| **Packaging** | setuptools + pyproject.toml (PEP 517) | Standard pip install |
| **Testing** | pytest, hypothesis | Property‑based tests for schema |
| **CI/CD** | GitHub Actions (lint, test, build wheels) | Automated quality gate |
| **Documentation** | MkDocs (Material theme) | Human‑readable docs site |

---  

## 7. External Dependencies  

| Package | Version | License |
|---------|---------|---------|
| click | >=8.1,<9.0 | BSD‑3 |
| pydantic | >=2.5,<3.0 | MIT |
| orjson | >=3.9,<4.0 | Apache‑2.0 |
| defusedxml | >=0.7,<1.0 | Python‑2.0 |
| ruamel.yaml | >=0.18,<0.19 | MIT |
| structlog | >=24.1,<25.0 | MIT |
| pytest | >=8.0,<9.0 | MIT |
| hypothesis | >=6.100,<7.0 | BSD‑3 |

All dependencies are compatible with the **Apache‑2.0** license of the overall project.

---  

## 8. Deployment & Distribution  

1. **Packaging** – `setup.cfg` defines a `console_scripts` entry point (`anime-meta-fix=anime_meta_fix.__main__:cli`).  
2. **Distribution** – Build wheels for `cp311` and `cp312` on Linux/macOS/Windows; upload to internal PyPI (`pypi.axentx.internal`).  
3. **Container (optional)** – Dockerfile for isolated execution:  

```Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir .
ENTRYPOINT ["python", "-m", "anime_meta_fix"]
```

4. **Runtime** – No external services required; runs entirely on the host filesystem.  

---  

## 9. Testing Strategy  

* **Unit Tests** – 100% coverage on `engine`, `walker`, `plugins`, and `schema`.  
* **Integration Tests** – End‑to‑end runs on a synthetic media tree (≈5 k files) verifying:  
  * Correct detection of malformed files  
  * Atomic writes and backup creation  
  * Thread‑safety under high concurrency  
* **Performance Benchmark** – `pytest-benchmark` target ≤ 30 s for 1 GB of media on a single‑core CI runner.  

All tests run on every PR via GitHub Actions; failures block merges.

---  

## 10. Future Enhancements (Post‑Launch)  

| Feature | Priority | Notes |
|---------|----------|-------|
| **Batch mode** – read list of paths from a file | Medium | Useful for scheduled jobs |
| **Metadata source sync** – pull missing fields from MyAnimeList API | Low | Requires API key handling |
| **GUI wrapper** – optional Qt/Tkinter front‑end | Low | For non‑technical users |
| **Parallel multi‑process mode** – for SSD‑heavy workloads | Medium | Switchable via `--processes` flag |

---  

## 11. Risks & Mitigations  

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Data loss** – accidental overwrite | High | Atomic replace + optional backup; dry‑run mode |
| **Unsupported format** – plugin fails silently | Medium | Core engine logs `detect=False` and skips; plugin registration validation |
| **Performance regression** with many threads | Medium | Benchmark suite caps threads to `min(8, cpu_count)` by default |
| **Dependency security** – vulnerable transitive libs | Low | Dependabot auto‑updates; CI runs `pip-audit` |

---  

## 12. Glossary  

* **Metadata file** – JSON, XML, or YAML file describing a single anime title (commonly `metadata.json` or `info.nfo`).  
* **Plugin** – Python module that knows how to read/write a specific file format.  
* **Dry‑run** – Execution mode that reports fixes without writing to disk.  

---  

*Prepared by the Axentx OS Product Engineering Team.*
