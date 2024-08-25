import json
import os

def prompt_for_storage_type():
    """Prompt the user to choose between local or Mega storage."""
    while True:
        storage_type = input("Enter storage type (local/mega): ").strip().lower()
        if storage_type in ['local', 'mega']:
            if storage_type == 'local':
                base_path = "Backup/storage/local"

            elif storage_type == 'mega':
                base_path = "Backup/storage/mega"
            return storage_type, base_path
        print("Invalid input. Please enter 'local' or 'mega'.")

def prompt_for_archive_format():
    """Prompt the user to choose between tar or zip format."""
    while True:
        archive_format = input("Enter archive format (tar/zip): ").strip().lower()
        if archive_format in ['tar', 'zip']:
            return archive_format
        print("Invalid input. Please enter 'tar' or 'zip'.")

def prompt_for_mega_credentials():
    """Prompt the user to enter Mega login credentials."""
    email = input("Enter your Mega email: ").strip()
    password = input("Enter your Mega password: ").strip()
    return {
        'email': email,
        'password': password
    }

def save_settings(settings):
    """Save the settings to a JSON file."""
    with open('Backup/settings/settings.json', 'w') as f:
        json.dump(settings, f, indent=4)
    print("Settings saved to Backup/settings/settings.json.")

def main():
    """Main function to gather user input and save settings."""
    settings = {}

    # Prompt for storage type
    settings['storage_type'], settings['base_dir'] = prompt_for_storage_type()

    # Prompt for archive format
    settings['archive_format'] = prompt_for_archive_format()

    # Prompt for Mega credentials if Mega is selected
    if settings['storage_type'] == 'mega':
        settings['mega_credentials'] = prompt_for_mega_credentials()

    # Save the settings to the JSON file
    save_settings(settings)

if __name__ == "__main__":
    # Ensure the settings directory exists
    os.makedirs('Backup/settings', exist_ok=True)
    main()
