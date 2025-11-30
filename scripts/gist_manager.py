#!/usr/bin/env python3
"""GitHub Gist Management Tool

Create, update, list, and manage GitHub gists from local files.

Usage:
    python scripts/gist_manager.py create <file> [--description "Description"] [--public]
    python scripts/gist_manager.py update <gist_id> <file> [--description "Description"]
    python scripts/gist_manager.py list
    python scripts/gist_manager.py delete <gist_id>
    python scripts/gist_manager.py get <gist_id>
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / ".env")

console = Console()

GITHUB_API_BASE = "https://api.github.com"
GIST_ENDPOINT = f"{GITHUB_API_BASE}/gists"


def get_github_token() -> str:
    """Get GitHub token from environment variable."""
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token:
        console.print(
            "[red]Error: GITHUB_TOKEN or GITHUB_PERSONAL_ACCESS_TOKEN environment variable not set[/red]"
        )
        console.print(
            "[yellow]Please set it in your .env file or export it:\n"
            "  export GITHUB_TOKEN=your_token_here[/yellow]"
        )
        sys.exit(1)
    return token


def get_headers() -> dict[str, str]:
    """Get API headers with authentication."""
    return {
        "Authorization": f"token {get_github_token()}",
        "Accept": "application/vnd.github.v3+json",
    }


def read_file_content(file_path: Path) -> str:
    """Read file content, handling encoding issues."""
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        console.print(f"[yellow]Warning: {file_path} is not UTF-8, trying with errors='replace'[/yellow]")
        return file_path.read_text(encoding="utf-8", errors="replace")


def create_gist(
    files: dict[str, Path],
    description: str = "",
    public: bool = False,
) -> dict[str, Any]:
    """Create a new GitHub gist.

    Args:
        files: Dictionary mapping filename to file path
        description: Gist description
        public: Whether gist should be public (default: False)

    Returns:
        Gist data from API response
    """
    gist_files = {}
    for filename, file_path in files.items():
        if not file_path.exists():
            console.print(f"[red]Error: File not found: {file_path}[/red]")
            sys.exit(1)
        gist_files[filename] = {"content": read_file_content(file_path)}

    payload = {
        "description": description,
        "public": public,
        "files": gist_files,
    }

    response = requests.post(GIST_ENDPOINT, headers=get_headers(), json=payload)
    response.raise_for_status()
    return response.json()


def update_gist(
    gist_id: str,
    files: dict[str, Path | None],
    description: str | None = None,
) -> dict[str, Any]:
    """Update an existing GitHub gist.

    Args:
        gist_id: Gist ID to update
        files: Dictionary mapping filename to file path (None to delete file)
        description: New description (optional)

    Returns:
        Updated gist data from API response
    """
    gist_files = {}
    for filename, file_path in files.items():
        if file_path is None:
            # Delete file
            gist_files[filename] = None
        else:
            if not file_path.exists():
                console.print(f"[red]Error: File not found: {file_path}[/red]")
                sys.exit(1)
            gist_files[filename] = {"content": read_file_content(file_path)}

    payload: dict[str, Any] = {"files": gist_files}
    if description is not None:
        payload["description"] = description

    response = requests.patch(
        f"{GIST_ENDPOINT}/{gist_id}",
        headers=get_headers(),
        json=payload,
    )
    response.raise_for_status()
    return response.json()


def list_gists() -> list[dict[str, Any]]:
    """List all gists for the authenticated user.

    Returns:
        List of gist data
    """
    response = requests.get(GIST_ENDPOINT, headers=get_headers())
    response.raise_for_status()
    return response.json()


def get_gist(gist_id: str) -> dict[str, Any]:
    """Get a specific gist by ID.

    Args:
        gist_id: Gist ID

    Returns:
        Gist data
    """
    response = requests.get(f"{GIST_ENDPOINT}/{gist_id}", headers=get_headers())
    response.raise_for_status()
    return response.json()


def delete_gist(gist_id: str) -> None:
    """Delete a gist.

    Args:
        gist_id: Gist ID to delete
    """
    response = requests.delete(f"{GIST_ENDPOINT}/{gist_id}", headers=get_headers())
    response.raise_for_status()


def format_gist_info(gist: dict[str, Any]) -> str:
    """Format gist information for display."""
    files = list(gist["files"].keys())
    visibility = "Public" if gist["public"] else "Private"
    created = gist["created_at"][:10]  # Just the date
    return (
        f"[bold]{gist['description'] or '(no description)'}[/bold]\n"
        f"ID: {gist['id']}\n"
        f"Visibility: {visibility}\n"
        f"Files: {', '.join(files)}\n"
        f"Created: {created}\n"
        f"URL: {gist['html_url']}"
    )


def main() -> None:
    """Main CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Manage GitHub gists from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new gist")
    create_parser.add_argument("file", type=Path, help="File to create gist from")
    create_parser.add_argument(
        "--filename",
        type=str,
        help="Filename in gist (default: same as source file)",
    )
    create_parser.add_argument(
        "--description",
        type=str,
        default="",
        help="Gist description",
    )
    create_parser.add_argument(
        "--public",
        action="store_true",
        help="Make gist public (default: private)",
    )

    # Update command
    update_parser = subparsers.add_parser("update", help="Update an existing gist")
    update_parser.add_argument("gist_id", help="Gist ID to update")
    update_parser.add_argument("file", type=Path, help="File to update gist with")
    update_parser.add_argument(
        "--filename",
        type=str,
        help="Filename in gist (default: same as source file)",
    )
    update_parser.add_argument(
        "--description",
        type=str,
        help="New gist description",
    )

    # List command
    subparsers.add_parser("list", help="List all your gists")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get a specific gist")
    get_parser.add_argument("gist_id", help="Gist ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a gist")
    delete_parser.add_argument("gist_id", help="Gist ID to delete")
    delete_parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "create":
            filename = args.filename or args.file.name
            files = {filename: args.file}
            gist = create_gist(files, args.description, args.public)
            console.print(Panel(format_gist_info(gist), title="[green]Gist Created[/green]"))

        elif args.command == "update":
            filename = args.filename or args.file.name
            files = {filename: args.file}
            gist = update_gist(args.gist_id, files, args.description)
            console.print(Panel(format_gist_info(gist), title="[green]Gist Updated[/green]"))

        elif args.command == "list":
            gists = list_gists()
            if not gists:
                console.print("[yellow]No gists found[/yellow]")
            else:
                table = Table(title="Your Gists", show_header=True, header_style="bold magenta")
                table.add_column("Description", style="cyan")
                table.add_column("ID", style="green", width=32)
                table.add_column("Visibility", style="yellow")
                table.add_column("Files", style="blue")
                table.add_column("URL", style="dim")

                for gist in gists:
                    files = ", ".join(gist["files"].keys())
                    visibility = "Public" if gist["public"] else "Private"
                    table.add_row(
                        gist["description"] or "(no description)",
                        gist["id"],
                        visibility,
                        files,
                        gist["html_url"],
                    )
                console.print(table)

        elif args.command == "get":
            gist = get_gist(args.gist_id)
            console.print(Panel(format_gist_info(gist), title="[cyan]Gist Details[/cyan]"))

            # Show file contents
            for filename, file_data in gist["files"].items():
                console.print(f"\n[bold]File: {filename}[/bold]")
                console.print(f"[dim]Size: {file_data['size']} bytes[/dim]")
                if file_data["size"] < 10000:  # Only show if < 10KB
                    content = requests.get(file_data["raw_url"]).text
                    console.print(Panel(content, title=filename, border_style="blue"))

        elif args.command == "delete":
            if not args.force:
                gist = get_gist(args.gist_id)
                console.print(Panel(format_gist_info(gist), title="[yellow]Gist to Delete[/yellow]"))
                confirm = console.input("[red]Are you sure you want to delete this gist? (yes/no): [/red]")
                if confirm.lower() != "yes":
                    console.print("[yellow]Deletion cancelled[/yellow]")
                    return

            delete_gist(args.gist_id)
            console.print(f"[green]Gist {args.gist_id} deleted successfully[/green]")

    except requests.exceptions.HTTPError as e:
        console.print(f"[red]API Error: {e}[/red]")
        if e.response.status_code == 401:
            console.print("[yellow]Check your GITHUB_TOKEN is valid[/yellow]")
        elif e.response.status_code == 404:
            console.print("[yellow]Gist not found (check the ID)[/yellow]")
        try:
            error_detail = e.response.json()
            console.print(f"[dim]{json.dumps(error_detail, indent=2)}[/dim]")
        except Exception:
            pass
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
