# OpenCode Local Storage Tools

This repository contains scripts for interacting with OpenCode's local storage on macOS and Linux (stored in `~/.local/share/opencode/storage/`). These tools help retrieve session data, messages, and assistant responses without needing the GUI.

## Setup

1. Ensure OpenCode is installed and running. Start the server if needed (e.g., via `opencode serve` or equivalent).
2. For `run.ts`: Install dependencies with `npm install`.
3. For `trace.py`: No additional dependencies (uses Python stdlib).

## Scripts

- **`local/trace.py`**: Retrieves and prints the latest assistant message for a given directory. Outputs reasoning and text parts with newlines for readability.
- **`run.ts`**: Lists all sessions for a directory using the OpenCode SDK.
- **`Makefile`**: Provides `make run FOLDER=<dir>` to execute `run.ts` easily.

## Usage

### Get Latest Assistant Message
```bash
./local/trace.py /path/to/project
```
Outputs the most recent assistant response across all sessions in the project.

### List Sessions
```bash
make run FOLDER=/path/to/project
```
Or directly:
```bash
npx tsx run.ts /path/to/project
```

## Requirements

- Python 3 for `trace.py`.
- Node.js and OpenCode SDK for `run.ts`.
- macOS or Linux with OpenCode installed.

## Notes

- Project ID is derived from the Git initial commit SHA or "global" for non-Git directories.
- Scripts access JSON files in `~/.local/share/opencode/storage/` directly for offline use.
- Ensure OpenCode server is running for SDK-based scripts.