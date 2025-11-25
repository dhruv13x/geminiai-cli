<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/gemini-cli/main/gemini-cli_logo.png" alt="gemini-cli logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/gemini-cli.svg)](https://pypi.org/project/gemini-cli/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/gemini-cli.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/gemini-cli/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/gemini-cli/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/gemini-cli/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/gemini-cli/graph/badge.svg)](https://codecov.io/gh/dhruv13x/gemini-cli)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/gemini-cli/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/gemini-cli.svg)
[![PyPI Downloads](https://img.shields.io/pypi/dm/gemini-cli.svg)](https://pypistats.org/packages/gemini-cli)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/gemini-cli.svg)](https://pypi.org/project/gemini-cli/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<!-- Docs -->
[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://your-docs-link)

</div>


# Gemini CLI Helper

A command-line interface (CLI) tool that acts as a wrapper around the official Gemini CLI, adding useful features for managing accounts, backups, and rate limits.

## About

This tool was created to simplify the management of the Gemini CLI by providing a more user-friendly interface for common tasks such as logging in, managing backups, and tracking API rate limits. It aims to be a "batteries-included" solution for both new and experienced users.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- The dependencies listed in `pyproject.toml`:
  - `b2sdk>=1.18.0`
  - `rich>=10.0.0`

### One-Command Installation

```bash
pip install .
```

### Usage Example

Here's how to create a local backup of your Gemini configuration:

```bash
geminiai backup
```

## ✨ Key Features

- **Account Management**: Seamlessly log in and out of your Gemini account.
- **Backup and Restore**: **God Level** - Create local or cloud-based backups of your Gemini configuration and restore them with a single command.
- **Rate Limit Tracking**: Keep track of API rate limits to avoid interruptions.
- **Automated Updates**: Check for and install updates to the underlying Gemini CLI.
- **Cloud Sync**: Synchronize your local backups with a Backblaze B2 bucket.

## ⚙️ Configuration & Advanced Usage

### Environment Variables

For cloud-based backups with Backblaze B2, you can configure your credentials using the following environment variables:

- `B2_APPLICATION_KEY_ID`: Your Backblaze B2 application key ID.
- `B2_APPLICATION_KEY`: Your Backblaze B2 application key.
- `B2_BUCKET_NAME`: The name of your B2 bucket.

### Commands

| Command         | Description                                     | Arguments                                                                                                                                                                                                                                                                                          |
| --------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `backup`        | Backup Gemini configuration.                    | `--src`, `--archive-dir`, `--dest-dir-parent`, `--dry-run`, `--cloud`, `--bucket`, `--b2-id`, `--b2-key`                                                                                                                                                                                               |
| `restore`       | Restore Gemini configuration from a backup.     | `--from-dir`, `--from-archive`, `--search-dir`, `--dest`, `--force`, `--dry-run`, `--cloud`, `--bucket`, `--b2-id`, `--b2-key`                                                                                                                                                                            |
| `check-integrity` | Check integrity of the current configuration.   | `--src`, `--search-dir`                                                                                                                                                                                                                                                                            |
| `list-backups`  | List available backups.                         | `--search-dir`, `--cloud`, `--bucket`, `--b2-id`, `--b2-key`                                                                                                                                                                                                                                         |
| `prune`         | Prune old backups.                              | `--keep`, `--backup-dir`, `--cloud`, `--cloud-only`, `--dry-run`, `--bucket`, `--b2-id`, `--b2-key`                                                                                                                                                                                                    |
| `check-b2`      | Verify Backblaze B2 credentials.                | `--b2-id`, `--b2-key`, `--bucket`                                                                                                                                                                                                                                                                    |
| `cloud-sync`    | Sync local backups to the cloud.                | `--backup-dir`, `--bucket`, `--b2-id`, `--b2-key`                                                                                                                                                                                                                                                    |
| `local-sync`    | Sync cloud backups to local.                    | `--backup-dir`, `--bucket`, `--b2-id`, `--b2-key`                                                                                                                                                                                                                                                    |
| `config`        | Manage persistent configuration.                | `set`, `get`, `list`, `unset`                                                                                                                                                                                                                                                                      |
| `doctor`        | Run a system diagnostic check.                  |                                                                                                                                                                                                                                                                                                    |
| `resets`        | Manage Gemini free tier reset schedules.        | `--list`, `--next`, `--add`, `--remove`                                                                                                                                                                                                                                                              |

### Global Options

| Option         | Description                                     |
| --------------- | ----------------------------------------------- |
| `--login`       | Login to Gemini CLI.                            |
| `--logout`      | Logout from Gemini CLI.                         |
| `--session`     | Show the current active session.                |
| `--update`      | Reinstall/update Gemini CLI.                    |
| `--check-update`| Check for updates.                              |

## 🏗️ Architecture

### Directory Tree

```
src/
└── geminiai_cli/
    ├── __init__.py
    ├── cli.py
    ├── backup.py
    ├── restore.py
    ├── ...
```

### Core Logic Flow

The main entry point is `src/geminiai_cli/cli.py`, which uses the `argparse` module to define the CLI commands and their arguments. Each command is then handled by a corresponding function in a separate file (e.g., `backup.py`, `restore.py`). The `rich` library is used to create a more user-friendly and visually appealing command-line interface.

## 🗺️ Roadmap

### Completed

- [x] Account Management
- [x] Local and Cloud Backups
- [x] Rate Limit Tracking
- [x] Automated Updates

### Upcoming

- [ ] Support for other cloud providers (e.g., AWS S3, Google Cloud Storage)
- [ ] A more interactive configuration process
- [ ] Improved error handling and reporting

## 🤝 Contributing & License

Contributions are welcome! Please feel free to submit a pull request or open an issue on the GitHub repository.

This project is licensed under the MIT License. See the `LICENSE` file for more details.
