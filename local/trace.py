#!/usr/bin/env python3
import sys
import os
import subprocess
import glob
import json
import argparse
try:
    import yaml
except ImportError:
    print("pyyaml is required. Install with: pip install pyyaml")
    sys.exit(1)
from mini_logger import getLogger
logger = getLogger(__name__)

def get_project_id(directory):
    try:
        # Change to the directory
        os.chdir(directory)
        # Run git rev-list to get initial commit
        result = subprocess.run(
            ["git", "rev-list", "--max-parents=0", "--all"],
            capture_output=True, text=True, check=True
        )
        commits = result.stdout.strip().split('\n')
        if commits:
            return commits[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "global"

def main():
    parser = argparse.ArgumentParser(description="Retrieve latest assistant message or list sessions for a directory.")
    parser.add_argument("directory", help="Path to the project directory")
    parser.add_argument("--session-id", help="Specific session ID to retrieve from (optional)")
    parser.add_argument("--list-sessions", action="store_true", help="List all sessions for the directory and exit")
    parser.add_argument("--list-messages", action="store_true", help="List all messages for the directory or session and exit")
    args = parser.parse_args()

    directory = os.path.realpath(args.directory)
    if not os.path.isdir(directory):
        print(f"Directory {directory} does not exist")
        sys.exit(1)

    storage_base = os.path.expanduser("~/.local/share/opencode/storage")
    project_id = get_project_id(directory)

    if args.list_sessions:
        session_dir = os.path.join(storage_base, "session", project_id)
        if not os.path.exists(session_dir):
            print(f"No sessions found for project {project_id}")
            return
        sessions = []
        home = os.path.expanduser("~")
        for f in glob.glob(os.path.join(session_dir, "*.json")):
            sid = os.path.splitext(os.path.basename(f))[0]
            path = f
            if path.startswith(home):
                path = "~" + path[len(home):]
            mtime = os.path.getmtime(f)
            sessions.append((mtime, f"{sid} {path}"))
        if sessions:
            sessions.sort(key=lambda x: x[0], reverse=True)
            print("\n".join([item[1] for item in sessions]))
        return

    if args.list_messages:
        sessions_to_check = [args.session_id] if args.session_id else []
        if not sessions_to_check:
            session_dir = os.path.join(storage_base, "session", project_id)
            if not os.path.exists(session_dir):
                print(f"No sessions found for project {project_id}")
                return
            sessions_to_check = [os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(session_dir, "*.json"))]
        sessions_data = {}
        home = os.path.expanduser("~")
        for sid in sessions_to_check:
            session_mtime = os.path.getmtime(os.path.join(storage_base, "session", project_id, f"{sid}.json"))
            sessions_data[sid] = {"mtime": session_mtime, "messages": {}}
            message_dir = os.path.join(storage_base, "message", sid)
            if os.path.exists(message_dir):
                messages = []
                for f in glob.glob(os.path.join(message_dir, "*.json")):
                    mid = os.path.splitext(os.path.basename(f))[0]
                    path = f
                    if path.startswith(home):
                        path = "~" + path[len(home):]
                    mtime = os.path.getmtime(f)
                    parts = {}
                    part_dir = os.path.join(storage_base, "part", mid)
                    if os.path.exists(part_dir):
                        for pf in glob.glob(os.path.join(part_dir, "*.json")):
                            pid = os.path.splitext(os.path.basename(pf))[0]
                            ppath = pf
                            if ppath.startswith(home):
                                ppath = "~" + ppath[len(home):]
                            parts[pid] = ppath
                    messages.append((mtime, mid, path, parts))
                messages.sort(key=lambda x: x[0], reverse=True)
                for mtime, mid, path, parts in messages:
                    sessions_data[sid]["messages"][mid] = {"path": path, "parts": parts}
        # Sort sessions by mtime
        sorted_sessions = sorted(sessions_data.items(), key=lambda x: x[1]["mtime"], reverse=True)
        output = {"sessions": {sid: {"messages": data["messages"]} for sid, data in sorted_sessions}}
        print(yaml.dump(output, default_flow_style=False, sort_keys=False))
        return

    session_dir = os.path.join(storage_base, "session", project_id)

    if args.session_id:
        session_id = args.session_id
        session_file = os.path.join(session_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            print(f"Session {session_id} not found")
            return
    else:
        if not os.path.exists(session_dir):
            print(f"No sessions found for project {project_id}")
            return
        session_id = None  # Will scan all sessions

    # Find the latest assistant message
    assistant_messages = []
    sessions_to_check = [session_id] if session_id else []
    if not session_id:
        for session_file in glob.glob(os.path.join(session_dir, "*.json")):
            sessions_to_check.append(os.path.splitext(os.path.basename(session_file))[0])

    for sid in sessions_to_check:
        message_dir = os.path.join(storage_base, "message", sid)
        if os.path.exists(message_dir):
            for msg_file in glob.glob(os.path.join(message_dir, "*.json")):
                with open(msg_file, 'r') as f:
                    data = json.load(f)
                    if data.get('role') == 'assistant':
                        mtime = os.path.getmtime(msg_file)
                        assistant_messages.append((mtime, msg_file))

    if not assistant_messages:
        print("No assistant messages found")
        return

    # Sort by mtime descending
    assistant_messages.sort(key=lambda x: x[0], reverse=True)
    latest_msg = assistant_messages[0][1]

    # Output the content of the latest message
    msg_id = os.path.splitext(os.path.basename(latest_msg))[0]
    part_dir = os.path.join(storage_base, "part", msg_id)
    logger.info('part_dir:', part_dir)
    parts = []
    if os.path.exists(part_dir):
        for part_file in glob.glob(os.path.join(part_dir, "*.json")):
            with open(part_file, 'r') as f:
                data = json.load(f)
                if data.get('type') in ('text', 'reasoning'):
                    parts.append(data.get('text', ''))

    logger.info('the last message:')
    print('\n'.join(parts))

if __name__ == "__main__":
    main()