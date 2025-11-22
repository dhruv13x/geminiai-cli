# Gemini CLI Helper

A command-line interface (CLI) tool that acts as a wrapper around the official Gemini CLI, adding useful features for managing accounts, backups, and rate limits.

## Features

- **Account Management**: Log in and out of your Gemini account.
- **Backup and Restore**: Create local or cloud-based backups of your Gemini configuration and restore them when needed.
- **Rate Limit Tracking**: Keep track of API rate limits to avoid interruptions.
- **Automated Updates**: Check for and install updates to the underlying Gemini CLI.

## Installation

This tool is not yet published to PyPI. To install it, you would typically use pip:

```bash
pip install .
```

## Commands

### General Commands

- `geminiai --login`: Log in to your Gemini account.
- `geminiai --logout`: Log out of your Gemini account.
- `geminiai --update`: Check for and install updates to the underlying Gemini CLI.

### Rate Limit Management

- `geminiai --add "<time> [email]"`: Manually add a rate limit reset time. The email is optional.
  - Example: `geminiai --add "1:00 PM"`
  - Example: `geminiai --add "13:00 myemail@example.com"`
- `geminiai --list`: List all saved rate limit reset times.
- `geminiai --next [email|id]`: Show the next upcoming reset time for a specific account or all accounts.
- `geminiai --remove <id|email>`: Remove a saved rate limit entry.

### Backup and Restore

#### Local Backups

- `geminiai backup`: Create a local backup of your Gemini configuration (`~/.gemini`). Backups are stored as timestamped `.tar.gz` files in a local directory (default: `~/geminiai_backups`).
- `geminiai restore`: Restore your Gemini configuration from a local backup. By default, it restores from the oldest available backup archive.
  - `geminiai restore --from-archive <path/to/archive.tar.gz>`: Restore from a specific archive file.
  - `geminiai restore --from-dir <path/to/directory>`: Restore from a specific uncompressed backup directory.
- `geminiai list-backups`: List all available local backups.
- `geminiai check-integrity`: Check the integrity of your current configuration against the latest backup.

#### Cloud Backups (Backblaze B2)

This tool integrates with Backblaze B2 for cloud-based backups and restores.

**Configuration:**

You need to provide your Backblaze B2 credentials. You can do this in two ways:

1.  **Environment Variables (Recommended):**
    ```bash
    export B2_APPLICATION_KEY_ID='YOUR_KEY_ID'
    export B2_APPLICATION_KEY='YOUR_APP_KEY'
    export B2_BUCKET_NAME='your-b2-bucket-name'
    ```

2.  **Command-Line Arguments:**
    You can also provide your credentials directly in the command line:
    - `--b2-id <YOUR_KEY_ID>`
    - `--b2-key <YOUR_APP_KEY>`
    - `--bucket <YOUR_BUCKET_NAME>`

**Usage:**

- `geminiai check-b2`: Verify Backblaze B2 credentials and bucket access.
- `geminiai backup --cloud`: Create a local backup and upload it to your B2 bucket.
- `geminiai restore --cloud`: Restore your configuration from the oldest backup archive stored in your B2 bucket.
- `geminiai list-backups --cloud`: List available backups in your B2 bucket.

#### Cloud Synchronization

This feature ensures consistency between your local backup repository and your Backblaze B2 bucket by only adding missing files, without overwriting existing data.

- `geminiai cloud-sync`: Uploads any local `.tar.gz` backup archives that are missing from your configured Backblaze B2 bucket.
- `geminiai local-sync`: Downloads any `.tar.gz` backup archives from your Backblaze B2 bucket that are missing from your local backup directory.

## Usage Examples

**1. Create a local backup:**

```bash
geminiai backup
```

**2. Restore from the oldest local backup:**

```bash
geminiai restore
```

**3. Create a cloud backup to Backblaze B2:**

(Assuming environment variables are set)
```bash
geminiai backup --cloud
```

**4. Restore from a cloud backup on Backblaze B2:**

(Assuming environment variables are set)
```bash
geminiai restore --cloud
```

**5. List available local backups:**

```bash
geminiai list-backups
```

**6. Verify Backblaze B2 credentials:**

(Assuming environment variables are set)
```bash
geminiai check-b2
```

**7. List available cloud backups:**

(Assuming environment variables are set)
```bash
geminiai list-backups --cloud
```

**8. Synchronize local backups to the cloud:**

(Assuming environment variables are set)
```bash
geminiai cloud-sync
```

**9. Synchronize cloud backups to local storage:**

(Assuming environment variables are set)
```bash
geminiai local-sync
```

