#!/usr/bin/env python3
import sys
import os
import subprocess
import glob
import json

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
    if len(sys.argv) != 2:
        print("Usage: ./trace.py <directory>")
        sys.exit(1)

    directory = os.path.realpath(sys.argv[1])
    if not os.path.isdir(directory):
        print(f"Directory {directory} does not exist")
        sys.exit(1)

    project_id = get_project_id(directory)
    storage_base = os.path.expanduser("~/.local/share/opencode/storage")

    session_dir = os.path.join(storage_base, "session", project_id)
    if not os.path.exists(session_dir):
        print(f"No sessions found for project {project_id}")
        return

    # Find the latest assistant message across all sessions by file modification time
    assistant_messages = []
    for session_file in glob.glob(os.path.join(session_dir, "*.json")):
        session_id = os.path.splitext(os.path.basename(session_file))[0]
        message_dir = os.path.join(storage_base, "message", session_id)
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

    if not latest_msg:
        print("No messages found")
        return

    # Output the content of the latest message
    msg_id = os.path.splitext(os.path.basename(latest_msg))[0]
    part_dir = os.path.join(storage_base, "part", msg_id)
    parts = []
    if os.path.exists(part_dir):
        for part_file in glob.glob(os.path.join(part_dir, "*.json")):
            with open(part_file, 'r') as f:
                data = json.load(f)
                if data.get('type') in ('text', 'reasoning'):
                    parts.append(data.get('text', ''))

    print('\n'.join(parts))

if __name__ == "__main__":
    main()