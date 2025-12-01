
import argparse
import sys
from rich.table import Table
from rich.panel import Panel
from .ui import console, cprint
from .config import DEFAULT_BACKUP_DIR
from .project_config import load_project_config, normalize_config_keys

def print_rich_help():
    """Prints a beautiful Rich-formatted help screen for the MAIN command."""
    # Note: We avoid importing print_logo here to avoid circular imports if print_logo depends on something else,
    # but cli.py handles the logo. We just focus on help.

    console.print("[bold white]Usage:[/] [bold cyan]geminiai[/] [dim][OPTIONS][/] [bold magenta]COMMAND[/] [dim][ARGS]...[/]\n")

    # Commands Table
    cmd_table = Table(show_header=False, box=None, padding=(0, 2))
    cmd_table.add_column("Command", style="bold cyan", width=20)
    cmd_table.add_column("Description", style="white")

    commands = [
        ("backup", "Backup Gemini configuration and chats"),
        ("restore", "Restore Gemini configuration from a backup"),
        ("check-integrity", "Check integrity of current configuration"),
        ("list-backups", "List available backups"),
        ("prune", "Prune old backups (local or cloud)"),
        ("cleanup", "Clear temporary chat history and logs"),
        ("check-b2", "Verify Backblaze B2 credentials"),
        ("cloud-sync", "Sync local backups to Cloud"),
        ("local-sync", "Sync Cloud backups to local"),
        ("config", "Manage persistent configuration"),
        ("doctor", "Run system diagnostic check"),
        ("resets", "Manage Gemini free tier reset schedules"),
        ("cooldown", "Show account cooldown status"),
        ("recommend", "Get the next best account recommendation"),
        ("stats", "Show usage statistics (last 7 days)"),
    ]

    for cmd, desc in commands:
        cmd_table.add_row(cmd, desc)

    console.print(Panel(cmd_table, title="[bold magenta]Available Commands[/]", border_style="cyan"))

    # Options Table
    opt_table = Table(show_header=False, box=None, padding=(0, 2))
    opt_table.add_column("Option", style="bold yellow", width=20)
    opt_table.add_column("Description", style="white")

    options = [
        ("--login", "Login to Gemini CLI"),
        ("--logout", "Logout from Gemini CLI"),
        ("--session", "Show current active session"),
        ("--update", "Reinstall / update Gemini CLI"),
        ("--check-update", "Check for updates"),
        ("--help, -h", "Show this message and exit"),
    ]

    for opt, desc in options:
        opt_table.add_row(opt, desc)

    console.print(Panel(opt_table, title="[bold yellow]Options[/]", border_style="green"))
    sys.exit(0)

class RichHelpParser(argparse.ArgumentParser):
    """
    Custom parser that overrides print_help to display a Rich-based help screen
    for subcommands (and the main command if accessed via standard flow).
    """
    def error(self, message):
        console.print(f"[bold red]Error:[/ {message}")
        console.print("[dim]Use --help for usage information.[/]")
        sys.exit(2)

    def print_help(self, file=None):
        """
        Dynamically generates Rich help for ANY parser (main or subcommand).
        """
        if self.description and "Gemini AI Automation Tool" in self.description:
             # This is likely the main parser
             print_rich_help()
             return

        # For Subcommands (e.g., 'geminiai backup')
        console.print(f"[bold cyan]Command:[/ ] [bold magenta]{self.prog}[/]\n")
        if self.description:
            console.print(f"[italic]{self.description}[/]\n")

        # Usage
        console.print(f"[bold white]Usage:[/ ] [dim]{self.format_usage().strip().replace('usage: ', '')}[/]\n")

        # Arguments
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Option", style="bold yellow", width=30)
        table.add_column("Description", style="white")

        for action in self._actions:
            opts = ", ".join(action.option_strings)
            if not opts:
                opts = action.dest # Positional arg

            help_text = action.help or ""
            table.add_row(opts, help_text)

        console.print(Panel(table, title="[bold green]Arguments & Options[/]", border_style="cyan"))

def build_main_parser():
    # Use RichHelpParser for the main parser
    parser = RichHelpParser(description="Gemini AI Automation Tool", add_help=False)

    # Load project config (pyproject.toml / geminiai.toml)
    project_defaults = load_project_config()
    if project_defaults:
        # Normalize keys (kebab-case -> snake_case)
        project_defaults = normalize_config_keys(project_defaults)
        parser.set_defaults(**project_defaults)

    subparsers = parser.add_subparsers(dest="command", help="Available commands", parser_class=RichHelpParser)

    # Keep existing top-level arguments
    parser.add_argument("--login", action="store_true", help="Login to Gemini CLI")
    parser.add_argument("--logout", action="store_true", help="Logout from Gemini CLI")
    parser.add_argument("--session", action="store_true", help="Show current active session")
    parser.add_argument("--update", action="store_true", help="Reinstall / update Gemini CLI")
    parser.add_argument("--check-update", action="store_true", help="Check for updates")

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup Gemini configuration and chats (local or Backblaze B2 cloud).")
    backup_parser.add_argument("--src", default="~/.gemini", help="Source gemini dir (default ~/.gemini)")
    backup_parser.add_argument("--archive-dir", default=DEFAULT_BACKUP_DIR, help="Directory to store tar.gz archives (default ~/geminiai_backups)")
    backup_parser.add_argument("--dest-dir-parent", default=DEFAULT_BACKUP_DIR, help="Parent directory where timestamped backups are stored (default ~/geminiai_backups)")
    backup_parser.add_argument("--dry-run", action="store_true", help="Do not perform destructive actions")
    backup_parser.add_argument("--cloud", action="store_true", help="Upload backup to Cloud (B2)")
    backup_parser.add_argument("--bucket", help="B2 Bucket Name")
    backup_parser.add_argument("--b2-id", help="B2 Key ID (or set env GEMINI_B2_KEY_ID)")
    backup_parser.add_argument("--b2-key", help="B2 App Key (or set env GEMINI_B2_APP_KEY)")

    # Restore command
    restore_parser = subparsers.add_parser("restore", help="Restore Gemini configuration from a backup (local or Backblaze B2 cloud).")
    restore_parser.add_argument("--from-dir", help="Directory backup to restore from (preferred)")
    restore_parser.add_argument("--from-archive", help="Tar.gz archive to restore from")
    restore_parser.add_argument("--search-dir", default=DEFAULT_BACKUP_DIR, help="Directory to search for timestamped backups when no --from-dir (default ~/geminiai_backups)")
    restore_parser.add_argument("--dest", default="~/.gemini", help="Destination (default ~/.gemini)")
    restore_parser.add_argument("--force", action="store_true", help="Allow destructive replace without keeping .bak")
    restore_parser.add_argument("--dry-run", action="store_true", help="Do a dry run without destructive actions")
    restore_parser.add_argument("--cloud", action="store_true", help="Restore from Cloud (B2)")
    restore_parser.add_argument("--bucket", help="B2 Bucket Name")
    restore_parser.add_argument("--b2-id", help="B2 Key ID")
    restore_parser.add_argument("--b2-key", help="B2 App Key")
    restore_parser.add_argument("--auto", action="store_true", help="Automatically restore the best available account")

    # Integrity check command
    integrity_parser = subparsers.add_parser("check-integrity", help="Check integrity of current configuration against the latest backup.")
    integrity_parser.add_argument("--src", default="~/.gemini", help="Source directory for integrity check (default: ~/.gemini)")
    integrity_parser.add_argument("--search-dir", default=DEFAULT_BACKUP_DIR, help="Backup directory for integrity check (default: ~/geminiai_backups)")

    # List backups command
    list_backups_parser = subparsers.add_parser("list-backups", help="List available backups (local or Backblaze B2 cloud).")
    list_backups_parser.add_argument("--search-dir", default=DEFAULT_BACKUP_DIR, help="Directory to search for backups (default ~/geminiai_backups)")
    list_backups_parser.add_argument("--cloud", action="store_true", help="List backups from Cloud (B2)")
    list_backups_parser.add_argument("--bucket", help="B2 Bucket Name")
    list_backups_parser.add_argument("--b2-id", help="B2 Key ID")
    list_backups_parser.add_argument("--b2-key", help="B2 App Key")

    # Check B2 command
    check_b2_parser = subparsers.add_parser("check-b2", help="Verify Backblaze B2 credentials.")
    check_b2_parser.add_argument("--b2-id", help="B2 Key ID (or set env GEMINI_B2_KEY_ID)")
    check_b2_parser.add_argument("--b2-key", help="B2 App Key (or set env GEMINI_B2_APP_KEY)")
    check_b2_parser.add_argument("--bucket", help="B2 Bucket Name (or set env GEMINI_B2_BUCKET)")

    # Cloud Sync command
    cloud_sync_parser = subparsers.add_parser("cloud-sync", help="Sync missing local backups to Cloud (B2).")
    cloud_sync_parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="Local backup directory (default ~/geminiai_backups)")
    cloud_sync_parser.add_argument("--bucket", help="B2 Bucket Name")
    cloud_sync_parser.add_argument("--b2-id", help="B2 Key ID")
    cloud_sync_parser.add_argument("--b2-key", help="B2 App Key")

    # Local Sync command
    local_sync_parser = subparsers.add_parser("local-sync", help="Sync missing Cloud (B2) backups to local storage.")
    local_sync_parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="Local backup directory (default ~/geminiai_backups)")
    local_sync_parser.add_argument("--bucket", help="B2 Bucket Name")
    local_sync_parser.add_argument("--b2-id", help="B2 Key ID")
    local_sync_parser.add_argument("--b2-key", help="B2 App Key")

    # Config command
    config_parser = subparsers.add_parser("config", help="Manage persistent configuration.")
    config_parser.add_argument("config_action", choices=["set", "get", "list", "unset"], help="Action to perform")
    config_parser.add_argument("key", nargs="?", help="Setting key")
    config_parser.add_argument("value", nargs="?", help="Setting value")
    config_parser.add_argument("--force", action="store_true", help="Force save sensitive keys without confirmation (automation mode)")

    # Resets command (New subcommand for reset management)
    resets_parser = subparsers.add_parser("resets", help="Manage Gemini free tier reset schedules.")
    resets_parser.add_argument("--list", action="store_true", help="List saved schedules")
    resets_parser.add_argument("--next", nargs="?", const="*ALL*", help="Show next usage time. Optionally pass email or id.")
    resets_parser.add_argument("--add", nargs="?", const="", help="Add time manually. Example: --add '01:00 PM user@example.com'")
    resets_parser.add_argument("--remove", nargs=1, help="Remove saved entry by id or email.")

    # Doctor command
    subparsers.add_parser("doctor", help="Run system diagnostic check.")

    # Prune command
    prune_parser = subparsers.add_parser("prune", help="Prune old backups.")
    prune_parser.add_argument("--keep", type=int, default=5, help="Number of recent backups to keep (default: 5)")
    prune_parser.add_argument("--backup-dir", default=DEFAULT_BACKUP_DIR, help="Local backup directory")
    prune_parser.add_argument("--cloud", action="store_true", help="Also prune cloud backups")
    prune_parser.add_argument("--cloud-only", action="store_true", help="Only prune cloud backups")
    prune_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without doing it")
    prune_parser.add_argument("--bucket", help="B2 Bucket Name")
    prune_parser.add_argument("--b2-id", help="B2 Key ID")
    prune_parser.add_argument("--b2-key", help="B2 App Key")

    # Cleanup command
    cleanup_parser = subparsers.add_parser("cleanup", help="Clear temporary chat history and logs.")
    cleanup_parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted without doing it")
    cleanup_parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")

    # Cooldown command
    cooldown_parser = subparsers.add_parser("cooldown", help="Show account cooldown status, with optional cloud sync.")
    cooldown_parser.add_argument("--cloud", action="store_true", help="Sync cooldown status from the cloud.")
    cooldown_parser.add_argument("--bucket", help="B2 Bucket Name")
    cooldown_parser.add_argument("--b2-id", help="B2 Key ID")
    cooldown_parser.add_argument("--b2-key", help="B2 App Key")
    cooldown_parser.add_argument("--remove", nargs=1, help="Remove an account from the dashboard (both cooldown and resets).")

    # Recommend command
    recommend_parser = subparsers.add_parser("recommend", aliases=["next"], help="Suggest the next best account (Green & Least Recently Used).")
    # No arguments needed for now, but could add specific filters later.

    # Stats command
    stats_parser = subparsers.add_parser("stats", aliases=["usage"], help="Show usage statistics (last 7 days).")

    return parser, resets_parser
