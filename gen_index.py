#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import datetime
import html
import urllib.parse
from pathlib import Path
from typing import List, Tuple

def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def generate_index(directory: str, root_dir: str) -> None:
    """
    Generate index.html in the given directory if it does not exist.
    directory: absolute path of the current directory
    root_dir:  absolute path of the user-specified root directory
    """
    index_path = os.path.join(directory, 'index.html')
    if os.path.exists(index_path):
        return

    try:
        entries = os.listdir(directory)
    except PermissionError:
        print(f"Warning: cannot read directory {directory}, skipped")
        return

    dirs: List[str] = []
    files: List[str] = []
    for entry in entries:
        full = os.path.join(directory, entry)
        if os.path.isdir(full):
            dirs.append(entry)
        else:
            # Root directory index ignores non-directory files
            if directory == root_dir:
                continue
            # Skip any existing index.html (though it shouldn't exist by now)
            if entry.lower() == 'index.html':
                continue
            files.append(entry)

    dirs.sort(key=lambda s: s.lower())
    files.sort(key=lambda s: s.lower())

    # Build HTML content
    html_lines: List[str] = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '<meta charset="utf-8">',
        f'<title>Index of {html.escape(os.path.basename(directory))}</title>',
        '<style>',
        'body { font-family: sans-serif; margin: 2em; }',
        'table { border-collapse: collapse; width: 100%; }',
        'th, td { text-align: left; padding: 0.5em; border-bottom: 1px solid #ddd; }',
        'th { background-color: #f2f2f2; }',
        'tr:hover { background-color: #f5f5f5; }',
        'a { text-decoration: none; color: #0645ad; }',
        'a:hover { text-decoration: underline; }',
        '</style>',
        '</head>',
        '<body>',
        f'<h1>Index of {html.escape(os.path.basename(directory))}</h1>',
        '<table>',
        '<thead><tr><th>Name</th><th>Last modified</th><th>Size</th></tr></thead>',
        '<tbody>'
    ]

    # Parent directory link (skip for root)
    if directory != root_dir:
        html_lines.append(
            '<tr><td><a href="../">Parent Directory</a></td><td></td><td></td></tr>'
        )

    # Subdirectories
    for d in dirs:
        full = os.path.join(directory, d)
        try:
            mtime = os.path.getmtime(full)
            dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        except OSError:
            dt = ''
        # Escape name for display, URL-encode for href
        safe_name = html.escape(d)
        quoted_href = urllib.parse.quote(d) + '/'
        html_lines.append(
            f'<tr><td><a href="{quoted_href}">{safe_name}/</a></td><td>{dt}</td><td>-</td></tr>'
        )

    # Files
    for f in files:
        full = os.path.join(directory, f)
        try:
            mtime = os.path.getmtime(full)
            dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
            size = os.path.getsize(full)
            size_str = format_size(size)
        except OSError:
            dt = ''
            size_str = ''
        safe_name = html.escape(f)
        quoted_href = urllib.parse.quote(f)
        html_lines.append(
            f'<tr><td><a href="{quoted_href}">{safe_name}</a></td><td>{dt}</td><td>{size_str}</td></tr>'
        )

    html_lines.append('</tbody></table></body></html>')

    try:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(html_lines))
        print(f"Generated: {index_path}")
    except OSError as e:
        print(f"Error: cannot write to {index_path}: {e}")

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate directory index pages for a Maven repository')
    parser.add_argument('root', nargs='?', default='.', help='Root directory of the repository (default: current directory)')
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Error: {root} is not a valid directory")
        sys.exit(1)

    for dirpath, dirnames, filenames in os.walk(root):
        generate_index(dirpath, root)

if __name__ == '__main__':
    main()
