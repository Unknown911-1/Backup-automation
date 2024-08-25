import os
import shutil
import logging
import json
from pathlib import Path
from mega import Mega

# Global variable for Mega instance
_mega_instance = None

def load_mega_credentials():
    """Load Mega login credentials from a JSON file and log in."""
    global _mega_instance

    if _mega_instance is None:
        try:
            credentials_file = Path('Backup/settings/settings.json')
            with credentials_file.open('r') as f:
                settings = json.load(f)
            if 'mega_credentials' in settings:
                credentials = settings.get('mega_credentials', {})

            else:
                print('Run settings.py to set up Mega credentials.')
                    
            mega = Mega()
            _mega_instance = mega.login(credentials['email'], credentials['password'])
            logging.info("Logged into Mega successfully.")
        except Exception as e:
            logging.error(f"Failed to log in to Mega: {e}")
            raise
    else:
        logging.info("Using existing Mega login session.")

    return _mega_instance

def ensure_directory_exists(directory):
    """Ensure that the target directory exists."""
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logging.error(f"Error creating directory {directory}: {e}")
        raise

def save_archive(src, backup_dir_name, archive_format, base_dir, storage_type):
    """Create an archive and save it to the specified storage."""
    archive_name = f"{backup_dir_name}.{archive_format}"
    archive_path = Path(base_dir) / archive_name

    try:
        logging.info(f"Creating archive {archive_name} from {src}.")
        shutil.make_archive(str(Path(base_dir) / backup_dir_name), archive_format, src)

        if storage_type == "local":
            logging.info(f"Archive {archive_name} saved locally at {archive_path}.")
        elif storage_type == "mega":
            upload_to_mega(archive_path)
            archive_paths = Path(base_dir) / archive_name
            dir = f'{base_dir}/{backup_dir_name}'
            os.remove(archive_paths)
            os.remove(dir)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

        return str(archive_path)

    except (shutil.Error, ValueError) as e:
        logging.error(f"Error saving archive {archive_name}: {e}")
        raise

def upload_to_mega(archive_path):
    """Upload the archive to Mega storage."""
    try:
        mega = load_mega_credentials()
        logging.info(f"Uploading {archive_path} to Mega storage.")
        mega.upload(str(archive_path))
        logging.info(f"Successfully uploaded {archive_path} to Mega storage.")
    except Exception as e:
        logging.error(f"Error uploading {archive_path} to Mega storage: {e}")
        raise

def retrieve_archive(backup_dir_name, archive_format, base_dir, dest_dir, storage_type):
    """Retrieve an archive from the specified storage."""
    archive_name = f"{backup_dir_name}.{archive_format}"
    archive_path = Path(base_dir) / archive_name
    dest_path = Path(dest_dir) / backup_dir_name

    try:
        ensure_directory_exists(dest_dir)

        if storage_type == "local":
            logging.info(f"Retrieving {archive_name} from local storage.")
            shutil.unpack_archive(str(archive_path), str(dest_path))
            return True

        elif storage_type == "mega":
            logging.info(f"Retrieving {archive_name} from Mega storage.")
            download_from_mega(archive_name, dest_path)
            return True

        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    except (shutil.Error, ValueError) as e:
        logging.error(f"Error retrieving archive {archive_name}: {e}")
        raise

def download_from_mega(archive_name, dest_path):
    """Download an archive from Mega storage."""
    try:
        mega = load_mega_credentials()
        logging.info(f"Searching for {archive_name} on Mega storage.")
        files = mega.find(archive_name)

        # Check the type of files and handle appropriately
        if isinstance(files, list) and len(files) > 0:
            file = files[0]  # Get the first match
            logging.info(f"Downloading {archive_name} from Mega storage to {dest_path}.")
            mega.download(file['h'], dest_path)  # 'h' is the file handle, might need adjustment
            logging.info(f"Successfully downloaded {archive_name} to {dest_path}.")
        else:
            logging.warning(f"File {archive_name} not found on Mega.")

    except Exception as e:
        logging.error(f"Error downloading {archive_name} from Mega storage: {e}")
        raise

def delete_archive(backup_dir_name, archive_format, base_dir, storage_type):
    """Delete an archive from the specified storage."""
    archive_name = f"{backup_dir_name}.{archive_format}"
    archive_path = Path(base_dir) / archive_name

    try:
        if storage_type == "local":
            if archive_path.exists():
                logging.info(f"Deleting {archive_name} from local storage.")
                archive_path.unlink()
            else:
                logging.warning(f"Archive {archive_name} not found in local storage.")

        elif storage_type == "mega":
            logging.info(f"Deleting {archive_name} from Mega storage.")
            mega = load_mega_credentials()
            files = mega.find(archive_name)
            if files:
                mega.delete(files[0])
                logging.info(f"Successfully deleted {archive_name} from Mega storage.")
            else:
                logging.warning(f"File {archive_name} not found in Mega storage.")
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")

    except (OSError, ValueError) as e:
        logging.error(f"Error deleting archive {archive_name}: {e}")
        raise
