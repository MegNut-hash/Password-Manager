🔐 Passkey Password Manager
A highly secure, local-only password manager built for the gstack framework. Designed with a strict security-first architecture, this tool ensures your credentials never leave your local environment.

✨ Features
Credential Management: Easily add, securely view, search, and remove your stored passwords through a simple, intuitive user interface.

Strong Password Generation: Automatically generate cryptographically secure, high-entropy passwords for new accounts.

Zero-Cloud Architecture: 100% local encrypted storage. No cloud synchronization, external data transmission, or third-party servers.

Seamless Integration: Works perfectly with the gstack browse skill for rapid, automated form autofilling on websites.

Privacy First: Strict zero-logging policy. Passwords are never displayed in plaintext within logs, console outputs, or debug traces.

📂 Project Structure
docs/ - The installed skill documentation and reference guides.

templates/ - The template used to generate the skill structure.

Password_Manager.py - The main executable script for the user interface.

🚀 Getting Started
Prerequisites
Python 3.x installed on your machine.

A configured gstack environment.

Installation & Usage
Clone the repository to your local machine:

Bash
git clone <your-repository-url>
Navigate to the project directory:

Bash
cd PasswordManager
Run the application:

Bash
python Password_Manager.py
(If you are on Linux/macOS or a Raspberry Pi, use python3 Password_Manager.py)

Upon launching, a secure UI will prompt you to establish or enter your Master Key. This key is required to decrypt and access your vault. Once authenticated, the interface will guide you through generating secure passwords, storing new credentials, and utilizing the autofill integration.

🛡️ Security Notes & Disclaimer
Device-Bound: All data remains strictly on the device where it is generated.

Cryptographic Standards: Passwords and keys are generated using cryptographically secure pseudorandom number generators (CSPRNG).

Explicit Consent: User consent and authentication are strictly required before any credential is saved, retrieved, or injected into a form.

Master Key Recovery: Because this is a zero-knowledge, local-only architecture, there is no recovery mechanism if you lose your Master Key. Please keep it safe.
