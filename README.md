# OpenCode Local Storage Tools

> **Summary**: Scripts for accessing OpenCode's local storage on macOS and Linux to retrieve sessions, messages, and assistant responses. This repository contains scripts for interacting with OpenCode's local storage on macOS and Linux (stored in `~/.local/share/opencode/storage/`). These tools help retrieve session data, messages, and assistant responses without needing the GUI.

## Setup

1. Ensure OpenCode is installed and running. Start the server if needed (e.g., via `opencode serve` or equivalent).
2. For `run.ts`: Install dependencies with `npm install`.
3. For `trace.py`: No additional dependencies (uses Python stdlib).

## Scripts

- **`local/trace.py`**: Retrieves and prints the latest assistant message for a given directory or specific session, or lists sessions/messages in YAML format. Outputs reasoning and text parts with newlines for readability.
- **`run.ts`**: Lists all sessions for a directory using the OpenCode SDK.
- **`Makefile`**: Provides `make run FOLDER=<dir>` to execute `run.ts` easily.

## Usage

### Get Latest Assistant Message
```bash
./local/trace.py /path/to/project
```
Outputs the most recent assistant response across all sessions in the project.

```bash
./local/trace.py /path/to/project --session-id <session_id>
```
Outputs the latest assistant response from the specified session.

```bash
./local/trace.py /path/to/project --max-lines 10
```
Limits output to the last 10 lines of user and assistant text.

```bash
./local/trace.py /path/to/project --single-line
```
Outputs text as a single line with newlines escaped (e.g., "line1\nline2").

### List Sessions
```bash
./local/trace.py /path/to/project --list-sessions
```
Lists all session IDs for the project directory, sorted by modified date (oldest first, like `ls -ltr`).

### List Messages
```bash
./local/trace.py /path/to/project --list-messages
```
Lists all messages and their parts for the project directory in YAML format, with sessions sorted by most recent message (oldest first, like `ls -ltr`), and messages within sessions sorted by modified date (oldest first).

```bash
./local/trace.py /path/to/project --list-messages --session-id <session_id>
```
Lists all messages and their parts for the specified session in YAML format, sorted by modified date (oldest first).

### List Sessions
```bash
make run FOLDER=/path/to/project
```
Or directly:
```bash
npx tsx run.ts /path/to/project
```

## Requirements

- Python 3 for `trace.py` (requires `pyyaml`: `pip install pyyaml`).
- Node.js and OpenCode SDK for `run.ts`.
- macOS or Linux with OpenCode installed.

## Notes

- Project ID is derived from the Git initial commit SHA or "global" for non-Git directories.
- Scripts access JSON files in `~/.local/share/opencode/storage/` directly for offline use.
- Ensure OpenCode server is running for SDK-based scripts.