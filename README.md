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

`geminiai-cli` is a powerful, "batteries-included" command-line interface designed to supercharge your Gemini AI experience. It wraps complex operations into simple, memorable commands, ensuring your data is safe, your accounts are managed efficiently, and your workflow is uninterrupted. Whether you're a power user juggling multiple accounts or a developer needing reliable backups, `geminiai-cli` is your ultimate companion.

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.8 or higher
- **Dependencies**: `b2sdk`, `boto3`, `rich` (installed automatically)

### One-Command Installation

```bash
pip install geminiai-cli
# Or from source
pip install .
```

### Usage Example

Get up and running immediately. You can use `geminiai`, `geminiai-cli`, or the shorthand `ga`.

```bash
# Run a local backup
ga backup

# Configure your Cloud Provider (B2 or AWS S3) via Wizard
ga config --init

# Sync your backups to the cloud (Push to B2/S3)
ga sync push

# Get the next best account recommendation
ga recommend

# Check your account cooldown status
ga cooldown

# View all available commands
ga --help
```

## ✨ Key Features

- **🛡️ God Level Backups**: Create local or **Cloud-based** backups of your Gemini configuration and chats.
- **☁️ Multi-Cloud Support**: Native support for **Backblaze B2** and **AWS S3**.
- **🔄 Unified Cloud Sync**: Seamlessly `push` and `pull` backups between your local machine and your chosen cloud provider.
- **🧠 Smart Recommendation**: Automatically switch to the best available account based on cooldowns, resets, and usage history.
- **👥 Profile Management**: Switch between configuration contexts (e.g., `--profile work`, `--profile personal`) and port them across machines (`ga profile export/import`).
- **💬 Chat Management**: Backup, restore, resume, and **cleanup** chat sessions and logs.
- **⏱️ Resets Management**: Track your Gemini free tier reset schedules to maximize usage without hitting limits.
- **❄️ Cooldown Tracking**: Monitor account cooldown status to avoid rate limiting.
- **📊 Visual Usage Stats**: Visualize usage patterns over the last 7 days directly in the terminal.
- **🩺 Doctor Mode**: Run a system diagnostic check to identify and fix issues.
- **🔐 Credential Management**: Securely handle credentials via CLI arguments, Environment Variables, `.env` files, or Doppler.
- **⚡ Integrity Checks**: Verify your configuration integrity against backups.
- **🧙 Interactive Wizard**: Guided setup process for easy configuration (`config --init`).

## ⚙️ Configuration & Advanced Usage

### Environment Variables

You can configure credentials using `.env` files, environment variables, or Doppler. The priority order is: CLI Args > Doppler > Env Vars > `.env` file > Saved Config.

| Variable | Description |
| :--- | :--- |
| `GEMINI_B2_KEY_ID` | Backblaze B2 Application Key ID. |
| `GEMINI_B2_APP_KEY` | Backblaze B2 Application Key. |
| `GEMINI_B2_BUCKET` | Backblaze B2 Bucket Name. |
| `GEMINI_AWS_ACCESS_KEY_ID` | AWS Access Key ID for S3. |
| `GEMINI_AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key for S3. |
| `GEMINI_S3_BUCKET` | AWS S3 Bucket Name. |
| `GEMINI_S3_REGION` | AWS S3 Region (default: `us-east-1`). |
| `DOPPLER_TOKEN` | Token for fetching secrets from Doppler. |

### CLI Commands

| Command | Description | Key Arguments |
| :--- | :--- | :--- |
| `backup` | Backup configuration and chats. | `--src`, `--archive-dir`, `--cloud`, `--bucket`, `--dry-run`, `--dest-dir-parent` |
| `restore` | Restore configuration from backup. | `--from-dir`, `--from-archive`, `--cloud`, `--force`, `--auto` |
| `sync` | Sync backups with Cloud (B2/S3). | `push`, `pull`, `--backup-dir`, `--bucket`, `--b2-id`, `--b2-key` |
| `chat` | Manage chat history. | `backup`, `restore`, `cleanup` (w/ `--force`), `resume` |
| `list-backups` | List available backups. | `--cloud`, `--search-dir`, `--bucket` |
| `prune` | Delete old backups. | `--keep`, `--cloud`, `--cloud-only`, `--dry-run` |
| `check-integrity` | Verify configuration integrity. | `--src` |
| `check-b2` | Verify B2 credentials. | `--bucket`, `--b2-id`, `--b2-key` |
| `config` | Manage persistent settings. | `set`, `get`, `list`, `unset`, `--force`, `--init` |
| `resets` | Manage free tier reset schedules. | `--list`, `--next`, `--add`, `--remove` |
| `cooldown` | Show account cooldown status. | `--cloud`, `--remove`, `--bucket` |
| `recommend` | Suggest next best account. | *(No arguments)* |
| `stats` | Show usage statistics. | *(No arguments)* |
| `profile` | Export/Import profiles. | `export`, `import`, `--force` |
| `doctor` | Run system diagnostics. | *(No arguments)* |

### Global Options

| Option | Description |
| :--- | :--- |
| `--login` | Login to Gemini CLI. |
| `--logout` | Logout from Gemini CLI. |
| `--session` | Show current active session. |
| `--update` | Reinstall/update Gemini CLI. |
| `--check-update` | Check for updates. |
| `--profile` | Specify a configuration profile (e.g., `--profile work`). |

## 🏗️ Architecture

The project is structured as a modular Python CLI application using `argparse` for command handling and `rich` for the UI.

```text
src/geminiai_cli/
├── cli.py             # Main Entry Point
├── args.py            # Argument Parsing & Dispatch
├── backup.py          # Backup Logic
├── restore.py         # Restore Logic
├── chat.py            # Chat History Management
├── sync.py            # Unified Cloud Sync (Push/Pull)
├── cloud_factory.py   # Cloud Provider Factory
├── cloud_s3.py        # AWS S3 Implementation
├── b2.py              # Backblaze B2 Implementation
├── recommend.py       # Smart Account Recommendation
├── profile.py         # Profile Management
├── stats.py           # Visual Usage Statistics
├── integrity.py       # Integrity Check Logic
├── prune.py           # Backup Pruning Logic
├── doctor.py          # System Diagnostics
└── wizard.py          # Interactive Config Wizard
```

## 🗺️ Roadmap

### ✅ Completed
- **Core**: Account Management, Local Backups, Encrypted Backups.
- **Cloud**: Backblaze B2 Integration, AWS S3 Support, Unified Sync.
- **Intelligence**: Smart Recommendations, Auto-Switching, Rate Limit Tracking.
- **Experience**: Interactive Wizard, Visual Stats, Doctor Mode, Auto-Updates.
- **Management**: Profile Portability, Configuration Profiles.

### 🚧 Upcoming
- **Enhanced TUI**: Rich dashboards and real-time progress bars.
- **Webhooks**: Integration with Slack/Discord for alerts.
- **AI-Driven Anomaly Detection**: Smart backup analysis.
- **Ecosystem**: Python SDK and REST API Server.

## 🤝 Contributing & License

Contributions are welcome! Please submit a pull request or open an issue on the GitHub repository.

This project is licensed under the MIT License.
