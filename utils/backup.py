import os
import shutil
import uuid
import json
import logging
from datetime import datetime
from utils.database import BackupDatabase
from utils.storage import save_archive

def get_file_state(directory):
    """Get the modification times of all files, directories, and the provided directory itself."""
    state = {}
    state[directory] = os.path.getmtime(directory)

    for root, dirs, files in os.walk(directory):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            state[dir_path] = os.path.getmtime(dir_path)

        for file_name in files:
            file_path = os.path.join(root, file_name)
            state[file_path] = os.path.getmtime(file_path)

    return state

def handle_error(func):
    """Decorator to handle errors in file operations."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (OSError, shutil.Error) as e:
            logging.error(f"Error occurred: {e}")
            raise  # Re-raise the exception after logging it
    return wrapper

@handle_error
def copy_file(src, dst):
    """Copy a file from src to dst if src is a valid path."""
    if os.path.exists(src):
        shutil.copy2(src, dst)
        logging.info(f"Copied file {src} to {dst}")
        return True
    return False

@handle_error
def copy_dir(src, dst):
    """Copy a directory from src to dst."""
    def wrapper(func):
        def inner(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                logging.error(f"Error copying directory from {src} to {dst}: {e}")
                raise
        return inner

    @wrapper
    def copy_tree(src, dst):
        """Perform the actual copy operation."""
        if os.path.exists(dst):
            logging.info(f"Destination directory {dst} already exists. Proceeding with copying.")
        else:
            os.makedirs(dst, exist_ok=True)
        shutil.copytree(src, dst, dirs_exist_ok=True)

class Backup:
    def __init__(self, src, log_file, storage_type, base_dir, backup_name, db_file, schedule=None):
        self.src = src
        self.log_file = log_file
        self.storage_type = storage_type
        self.base_dir = base_dir
        self.backup_name = backup_name
        self.db_file = db_file
        self.last_backup_state = self.load_backup_state()
        self.database = BackupDatabase(db_file)
        self.schedule = schedule

    def create_backup_id(self):
        """Create a unique backup ID."""
        return str(uuid.uuid4())  # Simplified to just use UUID

    def load_backup_state(self):
        """Load the last backup state from the log file."""
        if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.warning(f"Log file {self.log_file} is invalid or empty. Starting with a fresh state.")
        return {}

    def save_backup_state(self, state):
        """Save the current backup state to the log file."""
        with open(self.log_file, 'w') as f:
            json.dump(state, f)

    def sync_files(self):
        """Perform the backup operation. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method.")

    def get_archive_format(self):
        """Get the archive format from the settings file."""
        settings_file = 'Backup/settings/settings.json'
        try:
            with open(settings_file, 'r') as f:
                data = json.load(f)
                return data['archive_format']
        except (FileNotFoundError, KeyError) as e:
            logging.error(f"Failed to get archive format: {e}")
            raise

    def run_backup(self):
        try:
            backup_id = self.create_backup_id()
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_dir_name = f"backup_{timestamp}"
            backup_dir_path = os.path.join(self.base_dir, backup_dir_name)
            self.dst = backup_dir_path

            os.makedirs(backup_dir_path, exist_ok=True)

            self.sync_files()
            logging.info("Backup completed successfully.")

            archive_format = self.get_archive_format()

            archive_path = save_archive(self.src, backup_dir_name, archive_format, self.base_dir, self.storage_type)

            self.database.save_backup(
                backup_id,
                archive_format,
                self.__class__.__name__,
                archive_path,
                self.storage_type,
                timestamp,
                self.src,
                self.log_file,
                self.base_dir,
                backup_dir_name
            )

        except Exception as e:
            logging.error(f"Backup failed: {e}")
            raise  # Re-raise the exception after logging it

class FullBackup(Backup):
    def __init__(self, src, log_file, storage_type, base_dir, backup_name, db_file, schedule=None):
        super().__init__(src, log_file, storage_type, base_dir, backup_name, db_file, schedule=None)
        self.backup_dir_name = backup_name
        self.db_file = db_file

    def sync_files(self):
        """Perform the full backup operation."""
        current_state = get_file_state(self.src)
        logging.info("Performing full backup...")

        for file_path, mtime in current_state.items():
            relative_path = os.path.relpath(file_path, self.src)
            target_file = os.path.join(self.dst, relative_path)

            target_file_dir = os.path.dirname(target_file)
            if not os.path.exists(target_file_dir):
                os.makedirs(target_file_dir)

            if os.path.isdir(file_path):
                copy_dir(file_path, target_file)
            else:
                copy_file(file_path, target_file)
            logging.info(f"Backed up {relative_path}")

        self.save_backup_state(current_state)

class IncrementalBackup(Backup):
    def sync_files(self):
        """Perform the incremental backup operation."""
        current_state = get_file_state(self.src)

        for file_path, mtime in current_state.items():
            relative_path = os.path.relpath(file_path, self.src)
            target_file = os.path.join(self.dst, relative_path)

            target_file_dir = os.path.dirname(target_file)
            if not os.path.exists(target_file_dir):
                os.makedirs(target_file_dir)

            if file_path not in self.last_backup_state or self.last_backup_state[file_path] != mtime:
                if os.path.isdir(file_path):
                    copy_dir(file_path, target_file)
                else:
                    copy_file(file_path, target_file)
                logging.info(f"Added/Updated {relative_path}")

        self.save_backup_state(current_state)

class DifferentialBackup(Backup):
    def sync_files(self):
        """Perform the differential backup operation."""
        current_state = get_file_state(self.src)

        logging.info("Performing differential backup...")
        for file_path, mtime in current_state.items():
            if file_path not in self.last_backup_state or self.last_backup_state[file_path] != mtime:
                relative_path = os.path.relpath(file_path, self.src)
                target_file = os.path.join(self.dst, relative_path)

                target_file_dir = os.path.dirname(target_file)
                if not os.path.exists(target_file_dir):
                    os.makedirs(target_file_dir)

                if os.path.isdir(file_path):
                    copy_dir(file_path, target_file)
                else:
                    copy_file(file_path, target_file)

                logging.info(f"Added/Updated {relative_path}")

        self.save_backup_state(current_state)
