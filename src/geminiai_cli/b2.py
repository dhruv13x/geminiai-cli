#!/usr/bin/env python3
import os
import sys
from .ui import cprint, NEON_GREEN, NEON_RED, NEON_YELLOW

try:
    from b2sdk.v2 import InMemoryAccountInfo, B2Api
except ImportError:
    B2Api = None

class B2Manager:
    def __init__(self, key_id, app_key, bucket_name):
        if not B2Api:
            cprint(NEON_RED, "[ERROR] 'b2sdk' is not installed. Please run: pip install b2sdk")
            sys.exit(1)
        
        self.info = InMemoryAccountInfo()
        self.b2_api = B2Api(self.info)
        self.bucket_name = bucket_name
        
        try:
            cprint(NEON_YELLOW, "[CLOUD] Authenticating with Backblaze B2...")
            self.b2_api.authorize_account("production", key_id, app_key)
            self.bucket = self.b2_api.get_bucket_by_name(bucket_name)
            cprint(NEON_GREEN, f"[CLOUD] Connected to bucket: {bucket_name}")
        except Exception as e:
            cprint(NEON_RED, f"[CLOUD] Authentication failed: {e}")
            sys.exit(1)

    def upload(self, local_path, remote_name=None):
        if not remote_name:
            remote_name = os.path.basename(local_path)
        
        cprint(NEON_YELLOW, f"[CLOUD] Uploading {local_path} -> {remote_name}...")
        try:
            self.bucket.upload_local_file(
                local_file=local_path,
                file_name=remote_name
            )
            cprint(NEON_GREEN, "[CLOUD] Upload successful!")
        except Exception as e:
            cprint(NEON_RED, f"[CLOUD] Upload failed: {e}")

    def list_backups(self):
        """Returns a generator of file versions."""
        return self.bucket.ls(recursive=True)

    def download(self, remote_name, local_path):
        cprint(NEON_YELLOW, f"[CLOUD] Downloading {remote_name} -> {local_path}...")
        try:
            download_dest = self.bucket.download_file_by_name(remote_name)
            download_dest.save_to(local_path)

            cprint(NEON_GREEN, "[CLOUD] Download successful!")
        except Exception as e:
            cprint(NEON_RED, f"[CLOUD] Download failed: {e}")
            sys.exit(1)
