# Passkey Password Manager

This is a secure, local-only password manager skill for the gstack framework.

## Features
- Cryptographically secure password generation
- Local encrypted storage (no cloud sync)
- Integration with browse skill for form autofilling
- Simple interface for adding/viewing/searching credentials
- Security-first design with no sensitive data logging

## Files
-  - The installed skill documentation
-  - The template used to generate the skill

## Usage
After installing this skill in your gstack environment, you can use it by invoking:


The skill will guide you through generating secure passwords, storing credentials, and autofilling login forms on websites.

## Security Notes
- All data remains on the user's device - no cloud sync or external transmission
- Passwords are generated using cryptographically secure random
- No logging or display of passwords in plaintext in logs or debug output
- User consent is always required before storing, retrieving, or using credentials

