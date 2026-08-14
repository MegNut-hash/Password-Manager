# Secure Password Manager (GUI Version)

A secure, cross-platform password manager with a graphical user interface that uses strong encryption to protect your credentials. Includes Google Passwords import/export compatibility and autofill functionality.

## Features

- **Modern Graphical Interface**: Built with Python Tkinter and ttkbootstrap for a clean, professional look
- **Strong Encryption**: AES-256 encryption via the cryptography library (Fernet)
- **Secure Key Derivation**: PBKDF2 with SHA-256 and 100,000+ iterations
- **Google Passwords Compatible**: Import/export CSV format compatible with Google Password Manager
- **Autofill Support**: Global hotkey (Ctrl+Alt+A) to automatically fill login forms on websites
- **Password Generator**: Create strong, random passwords of any length
- **Local Storage Only**: All data stored encrypted on your device - nothing is sent to servers
- **Master Password Protection**: Your data is encrypted with a key derived from your master password

## Files

- `gui_password_manager.py` - Main GUI application
- `vault.py` - Core encryption and vault logic
- `requirements.txt` - Python dependencies (`cryptography>=49.0.0`, `ttkbootstrap`, `pyautogui`, `keyboard`)
- `README.md` - This documentation

## Installation

1. Ensure you have Python 3.6+ installed
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   (This will install `cryptography`, `ttkbootstrap`, `pyautogui`, and `keyboard`)

## Usage

### Starting the Application

```bash
python gui_password_manager.py
```

### First Time Setup

1. On first launch, you'll be prompted to create a master password
2. Choose a strong master password (minimum 8 characters)
3. This password encrypts all your stored credentials - **do not forget it**
4. If you forget your master password, your data is permanently unrecoverable (by design)

### Using the GUI

#### Main Window
- **Left Panel**: Shows all your saved websites/services and usernames
- **Bottom Buttons**:
  - **Add Account**: Create a new login entry
  - **Edit Account**: Modify an existing entry
  - **Delete Account**: Remove an entry
  - **Show Password**: Reveal the password for the selected entry
  - **Generate Password**: Create a strong random password

#### Menu Options
- **File → Import from CSV**: Import passwords from a CSV file (see format below)
- **File → Export to CSV**: Export your passwords to a CSV file
- **Options → Enable Auto‑type**: Toggle the global autofill hotkey (Ctrl+Alt+A)
- **File → Exit**: Close the application

### Google Passwords Integration

#### Exporting from Google Passwords
1. Go to [passwords.google.com](https://passwords.google.com)
2. Click the Settings gear icon
3. Select "Export passwords"
4. You'll be prompted for your Google account password
5. Save the exported CSV file

#### Importing to This Application
1. In the application, go to File → Import from CSV
2. Select the CSV file exported from Google Passwords
3. The application will import all your passwords into your encrypted vault

#### Exporting for Google Passwords
1. In our app: File → Export to CSV
2. Go to [passwords.google.com](https://passwords.google.com)
3. Settings → Import passwords
4. Select the exported CSV file

### CSV Format
The application expects CSV files with the following columns:
- `name` or `website`: The website or service name
- `username`: The username or email address
- `password`: The password

Example:
```
name,username,password
example.com,user@example.com,securepassword123
github.com,myusername,mygithubpass
```

### Autofill (Auto‑Type) Feature
Enable via Options → Enable Auto‑type (or set `AUTO_TYPE_ENABLED = True` in the code).

**Usage:**
1. Navigate to a login page in your browser (or any application)
2. Click into the username field
3. Press the hotkey **Ctrl+Alt+A**
4. The extension will:
   - Detect the website from the window title
   - Look up your stored credentials for that site
   - Type the username, press Tab, type the password, and press Enter

**Notes:**
- Works best when the username field is focused first
- If a site has multiple usernames, the first one is used
- You can disable the feature anytime via the Options menu
- Requires the `pyautogui` and `keyboard` packages (installed via requirements.txt)

## Security Features

- **Master Password**: Never stored anywhere, only used to derive the encryption key
- **Encryption**: AES-256 in CBC mode with HMAC verification (via Fernet)
- **Key Derivation**: PBKDF2-HMAC-SHA256 with 100,000+ iterations and a random seed
- **Local Only**: All data remains on your computer - no network transmission
- **Open Source Cryptography**: Uses the battle-tested `cryptography` Python library
- **No Backdoors**: Without your master password, data is mathematically unrecoverable

## Important Security Warning

If you forget your master password, **your data is permanently unrecoverable**. There is no "forgot password" option by design - this is a security feature to protect your data. Always remember your master password and consider keeping a secure backup of it elsewhere.

## Customization

- **Themes**: Change the theme by modifying the `themename` parameter in `gui_password_manager.py` (try "darkly", "cyborg", "solar", "superhero", etc.)
- **Hotkey**: Change `AUTO_TYPE_HOTKEY` in the class (e.g., `"<win>+<a>"` for Windows key+A)
- **Autofill Toggle**: Set `AUTO_TYPE_ENABLED = False` by default to start with the feature disabled

## Requirements

- Python 3.6+
- Packages listed in `requirements.txt`:
  - `cryptography>=49.0.0`
  - `ttkbootstrap>=1.0.0`
  - `pyautogui>=0.9.0`
  - `keyboard>=0.13.0`

## License

This project is open source and available for personal use.

## Disclaimer

This password manager is provided as-is without any warranties. Use at your own risk. Always keep backups of your important data.
