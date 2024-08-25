import os
import json
import logging
from datetime import datetime
from pathlib import Path
from utils.database import BackupDatabase
from utils.storage import save_archive

class BackupScheduler:
    def __init__(self, db_file=None):
        base_dir = Path('Backup/settings')
        self.schedule_file = base_dir / 'schedule.json'
        self.db_file = db_file or base_dir / 'db.json'
        self.database = BackupDatabase(db_file=self.db_file)
        self.load_schedule()

    def load_schedule(self):
        """Load the backup schedule from the configuration file."""
        try:
            with self.schedule_file.open('r') as f:
                self.backup_config = json.load(f)
                logging.info("Schedule loaded successfully.")
        except FileNotFoundError:
            logging.error(f"Schedule file '{self.schedule_file}' not found! Creating an empty schedule.")
            self.backup_config = {}  # Initialize as an empty dictionary if the file is not found
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in schedule file: {e}")
            self.backup_config = {}  # Initialize as an empty dictionary if JSON is invalid

    def save_schedule(self):
        """Save the backup schedule to the configuration file."""
        with self.schedule_file.open('w') as f:
            json.dump(self.backup_config, f, indent=4)

    def add_schedule(self, frequency, backup_id):
        """Add a new schedule for a backup."""
        if not hasattr(self, 'backup_config'):
            self.backup_config = {}  # Ensure backup_config is initialized

        self.backup_config[backup_id] = {
            "frequency": frequency,
            "backup_id": backup_id
        }
        self.save_schedule()
        logging.info(f"Added schedule for backup ID {backup_id} with frequency '{frequency}'.")

    def run_scheduled_backups(self):
        """Run backups based on the schedule."""
        for name, config in self.backup_config.items():
            now = datetime.now()
            last_run = self.get_last_run(name)
            logging.info(f"Checking if backup '{name}' should run. Last run: {last_run}, Now: {now}")

            if self.is_time_to_run(config['frequency'], last_run, now):
                backup_id = config.get('backup_id')
                backup_details = self.database.get_backup_details(backup_id)

                if backup_details:
                    try:
                        logging.info(f"Performing backup for ID {backup_id}.")
                        self.perform_backup(backup_details)
                    except Exception as e:
                        logging.error(f"Failed to perform backup for ID {backup_id}: {e}")
                else:
                    logging.warning(f"No details found for backup ID {backup_id}")

                self.set_last_run(name, now)

    def get_last_run(self, backup_id):
        """Get the last run time of a scheduled backup."""
        last_run_file = Path('Backup/settings/schedule/last_run') / f"{backup_id}_last_run.json"
        if last_run_file.exists():
            with last_run_file.open('r') as f:
                return datetime.fromisoformat(json.load(f)['last_run'])
        return datetime.min  # Return earliest possible date if no last run found

    def set_last_run(self, backup_id, run_time):
        """Set the last run time of a scheduled backup."""
        last_run_file = Path('Backup/settings/schedule/last_run') / f"{backup_id}_last_run.json"
        last_run_file.parent.mkdir(parents=True, exist_ok=True)
        with last_run_file.open('w') as f:
            json.dump({"last_run": run_time.isoformat()}, f)

    def is_time_to_run(self, frequency, last_run, now):
        """Check if it's time to run the backup based on the frequency."""
        if frequency == 'daily':
            return now.date() > last_run.date()
        elif frequency == 'weekly':
            return (now - last_run).days >= 7
        elif frequency == 'monthly':
            return now.month > last_run.month or now.year > last_run.year
        return False

    def perform_backup(self, backup_details):
        """Perform the backup based on the details provided."""
        try:
            backup_type = backup_details['backup_type']
            storage_type = backup_details['storage_type']
            archive_format = backup_details['archive_format']
            base_dir = backup_details['base_dir']
            backup_dir_name = backup_details['backup_dir_name']
            src = backup_details['src']
            log_file = backup_details['log_file']
            backup_path = Path(base_dir) / backup_dir_name

            # Ensure the backup directory exists
            backup_path.mkdir(parents=True, exist_ok=True)

            # Ensure a full backup exists before proceeding with incremental or differential
            if backup_type in ['incremental', 'differential']:
                full_backup_exists = any(
                    self.database.get_backup_details(bid)['backup_type'] == 'full'
                    for bid in self.database.list_backup_ids()
                )
                if not full_backup_exists:
                    logging.warning(f"No full backup found. Performing a full backup instead of {backup_type}.")
                    backup_type = 'full'

            # Delay import to avoid circular dependency
            from utils.backup import FullBackup, IncrementalBackup, DifferentialBackup

            # Mapping of backup types to their respective classes
            backup_classes = {
                'full': FullBackup,
                'incremental': IncrementalBackup,
                'differential': DifferentialBackup
            }

            backup_class = backup_classes.get(backup_type.lower())
            if backup_class is None:
                raise ValueError(f"Unsupported backup type: {backup_type}")

            backup_instance = backup_class(src, log_file, archive_format, backup_dir_name, self.db_file)
            backup_instance.run_backup()

            # Save the archive to the storage
            save_archive(src, backup_dir_name, archive_format, base_dir, storage_type)

            logging.info(f"Performed {backup_type} backup with ID {backup_details['backup_id']}.")
        except Exception as e:
            logging.error(f"Error performing backup: {e}")
            raise
