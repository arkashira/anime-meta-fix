# Requirements.md – Anime Meta Fix

---

## 1. Overview

Anime Meta Fix is a lightweight command‑line utility that scans a media server directory tree, identifies anime metadata files, validates their contents, and automatically corrects common errors. The tool is designed to be **fast, safe, and idempotent**, enabling media‑server operators to keep their libraries clean with minimal manual effort.

---

## 2. Functional Requirements

| ID | Description | Priority | Acceptance Criteria |
|----|-------------|----------|---------------------|
| **FR‑1** | **CLI entry point** – The tool must be executable via `python -m anime_meta_fix` or `anime_meta_fix` after installation. | P1 | Running the command without arguments displays a help message. |
| **FR‑2** | **Path argument** – Accept a `--path` (or `-p`) option pointing to the root of the media server. | P1 | The tool exits with an error if the path does not exist or is not a directory. |
| **FR‑3** | **Recursive scan** – Recursively traverse the directory tree under the supplied path. | P1 | All sub‑directories are visited; symlinks are ignored to avoid cycles. |
| **FR‑4** | **Metadata file detection** – Identify files that are likely anime metadata (e.g., `.nfo`, `.xml`, `.json`, `.txt`). | P1 | A whitelist of extensions is used; files are matched case‑insensitively. |
| **FR‑5** | **Metadata parsing** – Parse each detected file into a canonical in‑memory representation. | P1 | Unsupported formats are skipped with a warning. |
| **FR‑6** | **Validation rules** – Enforce the following rules: <br>• `title` must be non‑empty <br>• `episode` must be an integer ≥ 1 <br>• `season` must be an integer ≥ 0 <br>• `release_date` must be a valid ISO‑8601 date <br>• `source` must be one of `TV`, `OVA`, `Movie`, `Web`. | P1 | Validation failures are logged and counted. |
| **FR‑7** | **Automatic correction** – For each validation failure, attempt a corrective action: <br>• Guess missing `title` from directory name <br>• Infer `episode` from filename <br>• Set `season` to 0 if missing <br>• Convert `release_date` to ISO‑8601 if possible <br>• Replace unknown `source` with `TV`. | P2 | Corrections are applied only when a deterministic inference is possible; otherwise the file is marked for manual review. |
| **FR‑8** | **Write‑back** – Persist corrected metadata back to the original file, preserving original formatting where possible. | P1 | File permissions remain unchanged; file timestamps are updated to the current time. |
| **FR‑9** | **Dry‑run mode** – Support a `--dry-run` flag that performs all steps except writing changes. | P1 | Dry‑run outputs the same summary as a normal run but does not modify any files. |
| **FR‑10** | **Summary report** – After processing, output a concise report: <br>• Total files scanned <br>• Files corrected <br>• Files requiring manual review <br>• Errors encountered | P1 | Report is printed to stdout and optionally written to a log file if `--log` is specified. |
| **FR‑11** | **Configuration file** – Allow a YAML/JSON config file (`--config`) to override defaults (e.g., custom validation rules, log level). | P2 | Config file is optional; defaults are used if omitted. |
| **FR‑12** | **Error handling** – Fail gracefully on I/O errors, permission errors, or malformed files, logging the issue and continuing with the next file. | P1 | The tool never crashes; it exits with a non‑zero status only if the initial path is invalid. |
| **FR‑13** | **Unit tests** – Provide a comprehensive test suite covering all functional paths. | P1 | Test coverage ≥ 90% for core modules. |
| **FR‑14** | **Documentation** – Generate a `--help` message and a `README.md` that explains usage, options, and examples. | P1 | Help text is displayed when `--help` is passed. |

---

## 3. Non‑Functional Requirements

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| **NFR‑1** | **Performance** – Scanning and processing 10,000 metadata files must complete within 30 seconds on a typical consumer
