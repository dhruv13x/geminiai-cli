<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/geminiai-cli/main/geminiai-cli_logo.png" alt="geminiai-cli logo" width="200"/>
</div>

<div align="center">

<!-- Package Info -->
[![PyPI version](https://img.shields.io/pypi/v/geminiai-cli.svg)](https://pypi.org/project/geminiai-cli/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
![Wheel](https://img.shields.io/pypi/wheel/geminiai-cli.svg)
[![Release](https://img.shields.io/badge/release-PyPI-blue)](https://pypi.org/project/geminiai-cli/)

<!-- Build & Quality -->
[![Build status](https://github.com/dhruv13x/geminiai-cli/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/geminiai-cli/actions/workflows/publish.yml)
[![Codecov](https://codecov.io/gh/dhruv13x/geminiai-cli/graph/badge.svg)](https://codecov.io/gh/dhruv13x/geminiai-cli)
[![Test Coverage](https://img.shields.io/badge/coverage-90%25%2B-brightgreen.svg)](https://github.com/dhruv13x/geminiai-cli/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
![Security](https://img.shields.io/badge/security-CodeQL-blue.svg)

<!-- Usage -->
![Downloads](https://img.shields.io/pypi/dm/geminiai-cli.svg)
[![PyPI Downloads](https://img.shields.io/pypi/dm/geminiai-cli.svg)](https://pypistats.org/packages/geminiai-cli)
![OS](https://img.shields.io/badge/os-Linux%20%7C%20macOS%20%7C%20Windows-blue.svg)
[![Python Versions](https://img.shields.io/pypi/pyversions/geminiai-cli.svg)](https://pypi.org/project/geminiai-cli/)

<!-- License -->
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

# Gemini AI Automation Tool

**The Swiss Army Knife for Gemini AI Automation - Backups, Cloud Sync, and Account Management.**

## About

`geminiai-cli` is a powerful, "batteries-included" command-line interface designed to supercharge your Gemini AI experience. Whether you need to manage multiple accounts, ensure your configuration is safely backed up to the cloud, or track your free tier usage to avoid rate limits, this tool has you covered. It wraps complex operations into simple, memorable commands.

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.8 or higher
- **Dependencies**: `b2sdk`, `rich` (installed automatically)

### One-Command Installation

```bash
pip install .
```

### Usage Example

Get up and running immediately by backing up your current configuration:

```bash
# Run a local backup
geminiai backup

# View all available commands
geminiai --help
```

## ✨ Key Features

- **🛡️ God Level Backups**: Create local or **Cloud-based (Backblaze B2)** backups of your Gemini configuration and chats.
- **☁️ Cloud Sync**: Seamlessly synchronize your backups between your local machine and the cloud.
- **⏱️ Resets Management**: Track your Gemini free tier reset schedules to maximize usage without hitting limits.
- **❄️ Cooldown Tracking**: Monitor account cooldown status to avoid rate limiting.
- **🩺 Doctor Mode**: Run a system diagnostic check to identify and fix issues.
- **🔐 Credential Management**: Securely handle Backblaze B2 credentials via CLI, Environment Variables, or Doppler.
- **🧹 Cleanup**: Easily clear temporary chat history and logs.
- **🔄 Automated Updates**: Check for and install updates to the underlying tools.

## ⚙️ Configuration & Advanced Usage

### Environment Variables

You can configure credentials using `.env` files, environment variables, or Doppler. The priority order is: CLI Args > Doppler > Env Vars > `.env` file > Saved Config.

| Variable | Description |
| :--- | :--- |
| `GEMINI_B2_KEY_ID` | Your Backblaze B2 Application Key ID. |
| `GEMINI_B2_APP_KEY` | Your Backblaze B2 Application Key. |
| `GEMINI_B2_BUCKET` | The name of your Backblaze B2 Bucket. |
| `DOPPLER_TOKEN` | Token for fetching secrets from Doppler. |

### CLI Commands

| Command | Description | Key Arguments |
| :--- | :--- | :--- |
| `backup` | Backup configuration and chats. | `--cloud`, `--bucket`, `--b2-id`, `--b2-key` |
| `restore` | Restore configuration from backup. | `--from-dir`, `--cloud`, `--force` |
| `cloud-sync` | Sync local backups to Cloud (B2). | `--bucket`, `--b2-id`, `--b2-key` |
| `local-sync` | Sync Cloud backups to local. | `--bucket`, `--b2-id`, `--b2-key` |
| `list-backups` | List available backups. | `--cloud`, `--search-dir` |
| `prune` | Delete old backups. | `--keep`, `--cloud`, `--cloud-only` |
| `check-integrity` | Verify configuration integrity. | `--src`, `--search-dir` |
| `check-b2` | Verify B2 credentials. | `--bucket`, `--b2-id`, `--b2-key` |
| `config` | Manage persistent settings. | `set`, `get`, `list`, `unset` |
| `resets` | Manage free tier reset schedules. | `--list`, `--next`, `--add`, `--remove` |
| `cooldown` | Show account cooldown status. | `--cloud` |
| `cleanup` | Clear temp files and logs. | `--force`, `--dry-run` |
| `doctor` | Run system diagnostics. | |

### Global Options

| Option | Description |
| :--- | :--- |
| `--login` | Login to Gemini CLI. |
| `--logout` | Logout from Gemini CLI. |
| `--session` | Show current active session. |
| `--update` | Reinstall/update Gemini CLI. |
| `--check-update` | Check for updates. |

## 🏗️ Architecture

The project is structured as a modular Python CLI application using `argparse` for command handling and `rich` for the UI.

```text
src/geminiai_cli/
├── cli.py             # Main Entry Point & Argument Parsing
├── credentials.py     # Credential Resolution (Env, Doppler, Config)
├── backup.py          # Backup Logic
├── restore.py         # Restore Logic
├── sync.py            # Cloud/Local Sync Logic
├── resets_helpers.py  # Reset Schedule Management
├── doctor.py          # Diagnostic Tools
└── ...
```

## 🗺️ Roadmap

- [x] **Account Management**: Seamless login/logout.
- [x] **Cloud Backups**: Backblaze B2 integration.
- [x] **Resets & Cooldowns**: Smart rate limit management.
- [ ] **Multi-Cloud Support**: AWS S3, Google Cloud Storage.
- [ ] **Interactive Config**: Wizard-style setup.
- [ ] **GUI**: A graphical interface for common tasks.

## 🤝 Contributing & License

Contributions are welcome! Please submit a pull request or open an issue on the GitHub repository.

This project is licensed under the MIT License.
