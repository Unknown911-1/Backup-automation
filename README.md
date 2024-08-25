# Backup Automation Script

This project provides a comprehensive backup solution that allows users to perform full, incremental, and differential backups, as well as retrieve and manage backup archives. The script supports both local and Mega cloud storage options and allows you to create backups in `tar` or `zip` formats.

## Features

- **Full Backup**: Create a complete backup of specified directories.
- **Incremental Backup**: Backup only the changes since the last backup.
- **Differential Backup**: Backup changes since the last full backup.
- **Retrieve Archives**: Download and restore archived backups from local or Mega storage.
- **Scheduling**: Optionally schedule backups to run at specified intervals (daily, weekly, monthly).

## Prerequisites

1. **Python 3.7+**: Ensure Python 3.7 or higher is installed.
2. **Required Libraries**: Install the necessary libraries using:
   ```bash
   pip install mega.py shutil uuid
   ```

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Unknown911-1/Backup-automation
   cd Backup-automation
   ```

2. **Create and Configure `settings.json`**:
   Run the `settings.py` script to configure your backup preferences:
   ```bash
   bash setup.sh
   ```
   Follow the prompts to set storage type (local or Mega), archive format (tar or zip), and Mega login credentials if applicable. The settings will be saved in `settings.json`.

## Usage

### Main Operations

Run the `main.py` script to perform backup or retrieval operations:

```bash
python backup.py
```

1. **Select Backup Operation**:
   - **1. Full Backup**: Backup an entire directory. Enter the source directory, backup name, and optionally schedule the backup.
   - **2. Incremental Backup**: Backup only changes since the last backup. Choose from existing backup IDs.
   - **3. Differential Backup**: Backup changes since the last full backup. Choose from existing backup IDs.
   - **4. Retrieve Archive**: Retrieve and restore a backup from local or Mega storage.

### Example

To perform a full backup:

1. Run:
   ```bash
   python backup.py
   ```
2. Choose option `1` for Full Backup.
3. Enter the source directory.
4. Enter a name for the backup.
5. Optionally enter a schedule type or press Enter to skip.

## How It Works

1. **Settings**: The `settings.py` script gathers user preferences and stores them in `settings.json`.
2. **Backup Operations**:
   - **Full Backup**: Archives the entire directory and saves it to the chosen storage.
   - **Incremental and Differential Backup**: Archives only new or changed files based on previous backups.
   - **Retrieve Archives**: Downloads and restores archived backups from specified storage.

3. **Scheduling**: The `backup_scheduler.py` script manages backup schedules and runs backups based on configured intervals.

## Updates

- **Future Updates**:
  - **Graphical User Interface (GUI)**: Upcoming versions will include a user-friendly GUI for easier interaction.
  - **Enhanced Storage Options**: Support for additional storage solutions and improved integration with existing ones.

## Troubleshooting

- **Error Handling**: Check the log files for detailed error messages('backup_operations.log').
- **Common Issues**:
  - **File Exists Error**: Ensure destination directories do not already exist when performing operations.
  - **Mega API Issues**: Verify Mega credentials and network connectivity.

## Contribution

Contributions are welcome! Please fork the repository and submit pull requests for bug fixes, new features, or improvements.

## License

This project is licensed under the MIT License.

## Support This Project

If you find this script useful and would like to support further development, consider donating using cryptocurrency!

### Bitcoin
Address: `32VaadWB1EkD18hoE8t5pGqRmyD5g4CV9A`

[![Bitcoin QR Code](https://github.com/user-attachments/assets/83bbedff-f793-4797-9a50-391ab8a2a838)](https://github.com/user-attachments/assets/83bbedff-f793-4797-9a50-391ab8a2a838)

### Ethereum
Address: `0x673ffaA78F49CF7f3627178EDaf512F58160e3ED`

[![Ethereum QR Code](https://github.com/user-attachments/assets/e537afb6-cc0f-4ef6-9beb-0a9002a32014)](https://github.com/user-attachments/assets/e537afb6-cc0f-4ef6-9beb-0a9002a32014)


### USDT (TRC-20)
Address: `TMcVnY3CyqEfgqCwhunzGjJdwsR4WSZZc9`

[![USDT QR Code](https://github.com/user-attachments/assets/d4666b3a-bbca-42d5-85c0-df4e21b96203)](https://github.com/user-attachments/assets/d4666b3a-bbca-42d5-85c0-df4e21b96203)

---

Thank you for using the Backup Automation Script!
```