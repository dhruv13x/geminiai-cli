# Gemini AI Automation Tool

<div align="center">
  <img src="https://raw.githubusercontent.com/dhruv13x/geminiai-cli/main/geminiai-cli_logo.png" alt="geminiai-cli logo" width="200"/>
</div>

<div align="center">

[![Build status](https://github.com/dhruv13x/geminiai-cli/actions/workflows/publish.yml/badge.svg)](https://github.com/dhruv13x/geminiai-cli/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/geminiai-cli.svg)](https://pypi.org/project/geminiai-cli/)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/badge/linting-ruff-yellow.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/maintenance-active-green.svg)](https://github.com/dhruv13x/geminiai-cli/graphs/commit-activity)

</div>

**The Swiss Army Knife for Gemini AI Automation - Backups, Cloud Sync, and Account Management.**

`geminiai-cli` is a powerful, "batteries-included" command-line interface designed to supercharge your Gemini AI experience. It handles backups (Local, S3, B2), synchronizes data across devices, manages multiple profiles, and intelligently tracks account usage to bypass rate limits.

---

## ⚡ Quick Start (The "5-Minute Rule")

### Prerequisites
- **Python**: 3.8 or higher
- **Optional**: [AWS CLI](https://aws.amazon.com/cli/) or [Backblaze B2 CLI](https://www.backblaze.com/b2/docs/quick_command_line.html) for credentials management.

### Installation

```bash
# Install from PyPI
pip install geminiai-cli

# Or install from source
pip install .
```

### Get Started Immediately

Copy and paste this snippet to configure your first profile, backup to the cloud, and verify your system health.

```bash
# 1. Run the interactive setup wizard
geminiai config --init

# 2. Run your first local backup
geminiai backup

# 3. Push your backup to the cloud (requires configured credentials)
geminiai sync push

# 4. Check the account dashboard
geminiai cooldown --cloud

# 5. Get a smart account recommendation
geminiai recommend
```

---

## ✨ Features

*   **🛡️ God Level Backups**: Securely backup your configuration and chat history to **Local**, **AWS S3**, or **Backblaze B2** storage. Supports **GPG Encryption** for sensitive data.
*   **🌍 Machine-Time Adaptive**: Automatically detects and uses your system's local timezone for all calculations and displays. No more manual IST/UTC conversions.
*   **⏱️ Smart Session Tracking**: Tracks "First Used" timestamps to accurately predict Gemini's 24-hour rolling quota resets.
*   **🧠 Intelligent Rotation**: Automatically recommends the "healthiest" account based on session start times and Least Recently Used (LRU) logic.
*   **☁️ Unified Cloud Sync**: Seamlessly `push` and `pull` backups between your local machine and the cloud.
*   **🛡️ Accident Protection**: Safeguards your session data by preventing accidental account switches from resetting your 24-hour quota clock.
*   **📊 Visual Analytics**: View beautiful, terminal-based bar charts of your usage history and account health.
*   **🩺 Doctor Mode**: Built-in diagnostic tool to validate your environment, dependencies, and configuration health.

---

## 📊 The Account Dashboard

The `geminiai cooldown` command provides a real-time, comprehensive view of your account fleet.

| Column | Type | Description |
| :--- | :--- | :--- |
| **First Used** | Static | The exact local time your daily quota session began. |
| **Last Used** | Relative | How long ago your most recent activity occurred. |
| **Availability** | Running | A dynamic countdown to your next full quota refresh (`First Used + 24h`). |
| **Next Reset** | Running | Displays explicit "Access resets at..." times captured from Gemini. |
| **Status** | Status | Color-coded state: `READY` 🟢, `COOLDOWN` 🔴, or `SCHEDULED` 🟡. |

---

## 🛠️ Configuration

You can configure `geminiai-cli` using **Environment Variables**, **CLI Arguments**, or the **Interactive Config** (`geminiai config --init`).

**Priority Order**: CLI Arguments > Environment Variables > `.env` / Doppler > Saved Config (`~/.geminiai-cli/settings.json`)

### Environment Variables

| Variable | Description | Default | Required |
| :--- | :--- | :--- | :--- |
| `GEMINI_AWS_ACCESS_KEY_ID` | AWS Access Key ID for S3. | None | No (for S3) |
| `GEMINI_AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key for S3. | None | No (for S3) |
| `GEMINI_S3_BUCKET` | AWS S3 Bucket Name. | None | No (for S3) |
| `GEMINI_S3_REGION` | AWS Region. | `us-east-1` | No |
| `GEMINI_B2_KEY_ID` | Backblaze B2 Application Key ID. | None | No (for B2) |
| `GEMINI_B2_APP_KEY` | Backblaze B2 Application Key. | None | No (for B2) |
| `GEMINI_B2_BUCKET` | Backblaze B2 Bucket Name. | None | No (for B2) |
| `GEMINI_BACKUP_PASSWORD` | Password for GPG encryption. | None | No (for `--encrypt`) |
| `DOPPLER_TOKEN` | Token for Doppler secrets management. | None | No |

---

## 🏗️ Architecture

The `geminiai-cli` is built with modularity and extensibility in mind.

```text
src/geminiai_cli/
├── cli.py             # 🚀 Entry Point & Argument Routing
├── config.py          # ⚙️ Global Constants & Paths
├── backup.py          # 📦 Backup Logic (Local & Cloud dispatch)
├── restore.py         # ♻️ Restore Logic (Auto-selection & Session logs)
├── cooldown.py        # ❄️ Master Dashboard & Adaptive Time Logic
├── recommend.py       # 🧠 Recommendation Engine (Session-aware)
├── sync.py            # 🔄 Unified Sync (Push/Pull)
├── cloud_factory.py   # ☁️ Cloud Provider Abstract Factory
└── stats.py           # 📊 Visualization Module
```

---

## 🤝 Contributing

We welcome contributions! Whether it's reporting a bug, suggesting a feature, or writing code.

1.  **Setup Dev Environment**:
    ```bash
    git clone https://github.com/dhruv13x/geminiai-cli.git
    cd geminiai-cli
    pip install -e .[dev]
    ```
2.  **Run Tests**:
    ```bash
    pytest tests/
    ```

---

## 🗺️ Roadmap

*   **Phase 1 (Completed)**: Core Backup/Restore, Multi-Cloud (S3/B2), Sync, Auto-Updates.
*   **Phase 2 (Completed)**: Machine-Time Adaptation, Session Tracking, Smart Rotation.
*   **Phase 3 (Upcoming)**:
    *   🔔 **Webhooks**: Slack/Discord notifications for backup status.
    *   🐍 **Python SDK**: Import `geminiai` as a library in your own scripts.
*   **Phase 4 (Vision)**: AI-driven anomaly detection and self-healing infrastructure.

See [ROADMAP.md](ROADMAP.md) for the full detailed vision.