import json
import logging
from pathlib import Path
from utils.storage import save_archive, retrieve_archive, delete_archive

class BackupDatabase:
    def __init__(self, db_file='Backup/settings/db.json'):
        self.db_file = Path(db_file)  # Convert to Path object
        self._ensure_db_exists()
        logging.info(f"Initialized BackupDatabase with file: {self.db_file}")

    def _ensure_db_exists(self):
        """Ensure the database file exists and is not empty."""
        if not self.db_file.exists() or self.db_file.stat().st_size == 0:
            with open(self.db_file, 'w') as f:
                json.dump({}, f)
            logging.info(f"Created new database file: {self.db_file}")

    def save_backup(self, backup_id, archive_format, backup_type, archive_path, storage_type, timestamp, src, log_file, base_dir, dest_dir):
        """Save backup details to the database."""
        backup_data = {
            backup_id: {
                "archive_format": archive_format,
                "backup_type": backup_type,
                "archive_path": archive_path,
                "storage_type": storage_type,
                "timestamp": timestamp,
                "src": src,
                "log_file": log_file,
                "base_dir": base_dir,
                "dest_dir": dest_dir
            }
        }

        with open(self.db_file, 'r+') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}  # Initialize as an empty dictionary if JSON is malformed or empty
            data.update(backup_data)
            f.seek(0)
            json.dump(data, f, indent=4)

        logging.info(f"Saved backup {backup_id} to database.")
        return backup_id

    def list_backup_ids(self):
        """List all backup IDs in the database."""
        with open(self.db_file, 'r') as f:
            try:
                backup_data = json.load(f)
            except json.JSONDecodeError:
                backup_data = {}
        return list(backup_data.keys())

    def get_backup_details(self, backup_id):
        """Retrieve details for a specific backup ID."""
        with open(self.db_file, 'r') as f:
            try:
                backup_data = json.load(f)
            except json.JSONDecodeError:
                backup_data = {}
        return backup_data.get(backup_id, None)

    def delete_backup(self, backup_id):
        """Delete backup details from the database."""
        with open(self.db_file, 'r+') as f:
            try:
                backup_data = json.load(f)
            except json.JSONDecodeError:
                backup_data = {}
            if backup_id in backup_data:
                del backup_data[backup_id]
                f.seek(0)
                f.truncate()
                json.dump(backup_data, f, indent=4)
                logging.info(f"Deleted backup {backup_id} from the database.")
            else:
                logging.warning(f"Backup ID {backup_id} not found in the database.")

    def sync_with_storage(self, dest_dir):
        """Synchronize the database with the storage operations."""
        for backup_id in self.list_backup_ids():
            backup_details = self.get_backup_details(backup_id)
            if backup_details:
                archive_path = backup_details['archive_path']
                storage_type = backup_details['storage_type']
                archive_format = backup_details['archive_format']
                backup_dir_name = backup_details.get('backup_dir_name', '')  # Default to empty string if not present
                base_dir = backup_details['base_dir']

                try:
                    if storage_type == 'local':
                        if not archive_path.exists():
                            logging.info(f"Backup {backup_id} archive file not found in local storage. Deleting record from database.")
                            self.delete_backup(backup_id)
                        else:
                            logging.info(f"Backup {backup_id} archive file found in local storage. Deleting the file.")
                            delete_archive(backup_dir_name, archive_format, base_dir, storage_type)

                    elif storage_type == 'mega':
                        if not retrieve_archive(backup_dir_name, archive_format, base_dir, dest_dir, storage_type):
                            logging.info(f"Backup {backup_id} archive file not found in Mega storage. Deleting record from database.")
                            self.delete_backup(backup_id)
                        else:
                            logging.info(f"Backup {backup_id} archive file found and retrieved from Mega storage.")

                except Exception as e:
                    logging.error(f"Error synchronizing backup {backup_id}: {e}")
