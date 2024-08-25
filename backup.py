import os
import json
import logging
from utils.backup import FullBackup, IncrementalBackup, DifferentialBackup
from utils.backup_scheduler import BackupScheduler
from utils.database import BackupDatabase
from utils.storage import retrieve_archive

def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(filename='Backup/backup_operations.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

def get_settings():
    """Load settings from the settings.json file."""
    settings_file = 'Backup/settings/settings.json'
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except FileNotFoundError:
        logging.error("Settings file not found.")
        raise
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding settings file: {e}")
        raise
    return settings

def list_backup_ids(db):
    """List backup IDs from the database."""
    return db.list_backup_ids()

def main():
    setup_logging()
    settings = get_settings()
    db = BackupDatabase()  # Initialize the database
    scheduler = BackupScheduler()  # Initialize the scheduler

    print("Select backup operation:")
    print("1. Full Backup")
    print("2. Incremental Backup")
    print("3. Differential Backup")
    print("4. Retrieve Archive")
    print("5. Exit")

    choice = input("Enter your choice (1/2/3/4): ").strip()

    if choice == '1':
        # Full Backup
        src = input("Enter the source directory for the backup: ").strip()
        backup_name = input("Enter a name for the backup: ").strip()
        schedule = input("Enter schedule type (daily/weekly/monthly) or press Enter to skip: ").strip()

        if schedule not in ['daily', 'weekly', 'monthly', '']:
            print("Invalid schedule type. Skipping scheduling.")
            schedule = ''
        log_file = f'Backup/settings/logs/{backup_id}.json'

        full_backup = FullBackup(src, log_file, settings['storage_type'], 
                                 settings['base_dir'], backup_name, 'Backup/test/test_db.json', schedule)
        full_backup.run_backup()

        if schedule:
            scheduler.add_schedule(schedule, full_backup.create_backup_id())
            print(f"Scheduled a {schedule} backup for {backup_name}.")

    elif choice == '2':
        # Incremental Backup
        backup_ids = list_backup_ids(db)
        if not backup_ids:
            print("No backups found in the database.")
            return

        print("Select the backup ID to increment from:")
        for i, bid in enumerate(backup_ids, 1):
            print(f"{i}. {bid}")

        selected_id = int(input("Enter the number of the backup ID: ").strip())
        if selected_id < 1 or selected_id > len(backup_ids):
            print("Invalid choice.")
            return

        backup_id = backup_ids[selected_id - 1]
        src = input("Enter the source directory for the incremental backup: ").strip()
        db_file = 'Backup/settings/db.json'
        log_file = f'Backup/settings/logs/{backup_id}.json'

        incremental_backup = IncrementalBackup(src, log_file, settings['storage_type'], 
                                                settings['base_dir'], backup_id, db_file)
        incremental_backup.run_backup()

    elif choice == '3':
        # Differential Backup
        backup_ids = list_backup_ids(db)
        if not backup_ids:
            print("No backups found in the database.")
            return

        print("Select the backup ID to base the differential backup on:")
        for i, bid in enumerate(backup_ids, 1):
            print(f"{i}. {bid}")

        selected_id = int(input("Enter the number of the backup ID: ").strip())
        if selected_id < 1 or selected_id > len(backup_ids):
            print("Invalid choice.")
            return

        backup_id = backup_ids[selected_id - 1]
        src = input("Enter the source directory for the differential backup: ").strip()
        db_file = 'Backup/settings/db.json'
        log_file = f'Backup/settings/logs/{backup_id}.json'

        differential_backup = DifferentialBackup(src, log_file, settings['storage_type'], 
                                                 settings['base_dir'], backup_id, db_file)
        differential_backup.run_backup()

    elif choice == '4':
        # Retrieve Archive
        backup_ids = list_backup_ids(db)
        print("Available backup IDs:")
        for i, bid in enumerate(backup_ids, 1):
            print(f"{i}. {bid}")

        selected_id = int(input("Enter the number of the backup ID: ").strip())
        if selected_id < 1 or selected_id > len(backup_ids):
            print("Invalid choice.")
            return

        backup_id = backup_ids[selected_id - 1]
        if backup_id not in backup_ids:
            print("Invalid backup ID. Exiting.")
            return

        backup_details = db.get_backup_details(backup_id)
        if not backup_details:
            print("No details found for the specified backup ID. Exiting.")
            return

        dest_dir = input("Enter the destination directory to retrieve the backup: ").strip()
        base_dir = backup_details.get('base_dir', 'Backup/storage/local')
        archive_format = backup_details.get('archive_format', 'zip')
        backup_dir_name = backup_details.get('dest_dir', 'default_backup_dir')  # Provide a default value
        storage_type = backup_details.get('storage_type', 'local')

        retrieve_archive(backup_dir_name, archive_format, base_dir, dest_dir, storage_type)
    
    elif choice == '5':
        print("Exiting the program......")
        exit()
    else:
        print("Invalid choice. Exiting.")

    

if __name__ == "__main__":
    main()
