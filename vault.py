import json
import os
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import getpass


class PasswordVault:
    def __init__(self, vault_file='vault.db'):
        self.vault_file = vault_file
        self.salt_file = 'salt.salt'
        self.key = None
        self._initialize_vault()
    
    def _initialize_vault(self):
        '''Initialize the vault - create salt and key if needed'''
        # Generate or load salt
        if not os.path.exists(self.salt_file):
            salt = secrets.token_bytes(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
        else:
            with open(self.salt_file, 'rb') as f:
                salt = f.read()
        
        # Create empty vault if it doesn't exist
        if not os.path.exists(self.vault_file):
            with open(self.vault_file, 'wb') as f:
                f.write(b'')
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        '''Derive encryption key from master password using PBKDF2'''
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def set_master_password(self, password: str):
        '''Set/master password and initialize encryption key'''
        with open(self.salt_file, 'rb') as f:
            salt = f.read()
        self.key = self._derive_key(password, salt)
    
    def _encrypt_data(self, data: str) -> bytes:
        '''Encrypt data using Fernet symmetric encryption'''
        if self.key is None:
            raise ValueError('Master password not set')
        f = Fernet(self.key)
        return f.encrypt(data.encode())
    
    def _decrypt_data(self, encrypted_data: bytes) -> str:
        '''Decrypt data using Fernet symmetric encryption'''
        if self.key is None:
            raise ValueError('Master password not set')
        f = Fernet(self.key)
        return f.decrypt(encrypted_data).decode()
    
    def _load_vault(self) -> dict:
        '''Load and decrypt the vault'''
        if not os.path.exists(self.vault_file) or os.path.getsize(self.vault_file) == 0:
            return {}
        
        try:
            with open(self.vault_file, 'rb') as f:
                encrypted_data = f.read()
            
            if not encrypted_data:
                return {}
            
            decrypted_data = self._decrypt_data(encrypted_data)
            return json.loads(decrypted_data)
        except (json.JSONDecodeError, ValueError):
            # If decryption fails, it might be wrong password
            raise ValueError('Invalid master password or corrupted vault')
    
    def _save_vault(self, vault_data: dict):
        '''Encrypt and save the vault'''
        json_data = json.dumps(vault_data)
        encrypted_data = self._encrypt_data(json_data)
        with open(self.vault_file, 'wb') as f:
            f.write(encrypted_data)
    
    def add_password(self, service: str, username: str, password: str):
        '''Add a new password entry'''
        vault = self._load_vault()
        if service not in vault:
            vault[service] = []
        
        # Avoid duplicate usernames for same service
        vault[service] = [entry for entry in vault[service] 
                         if entry.get('username') != username]
        
        vault[service].append({
            'username': username,
            'password': password
        })
        
        self._save_vault(vault)
    
    def get_passwords(self, service: str) -> list:
        '''Get all passwords for a service'''
        vault = self._load_vault()
        return vault.get(service, [])
    
    def delete_password(self, service: str, username: str):
        '''Delete a specific password entry'''
        vault = self._load_vault()
        if service in vault:
            vault[service] = [entry for entry in vault[service] 
                             if entry.get('username') != username]
            if not vault[service]:  # Remove service if no entries left
                del vault[service]
            self._save_vault(vault)
            return True
        return False
    
    def list_services(self) -> list:
        '''List all services in the vault'''
        vault = self._load_vault()
        return list(vault.keys())
    
    def delete_service(self, service: str):
        '''Delete all entries for a service'''
        vault = self._load_vault()
        if service in vault:
            del vault[service]
            self._save_vault(vault)
            return True
        return False


def generate_password(length=16):
    '''Generate a secure random password'''
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def main():
    vault = PasswordVault()
    
    print('=== Secure Password Manager ===')
    
    # Check if vault exists and ask for master password
    if os.path.exists('salt.salt'):
        print('Vault found. Please enter your master password:')
        while True:
            try:
                password = getpass.getpass('Master Password: ')
                vault.set_master_password(password)
                # Try to load vault to verify password
                vault._load_vault()
                break
            except ValueError as e:
                print(f'Error: {e}')
                print('Please try again.')
    else:
        print('No vault found. Please set up a master password:')
        while True:
            password1 = getpass.getpass('Master Password: ')
            password2 = getpass.getpass('Confirm Master Password: ')
            if password1 == password2:
                if len(password1) >= 8:
                    vault.set_master_password(password1)
                    print('Vault created successfully!')
                    break
                else:
                    print('Password must be at least 8 characters long.')
            else:
                print('Passwords do not match. Please try again.')
    
    # Main menu loop
    while True:
        print('\n' + '='*40)
        print('Password Manager Menu')
        print('='*40)
        print('1. Add a new password')
        print('2. View passwords for a service')
        print('3. List all services')
        print('4. Delete a password')
        print('5. Delete a service')
        print('6. Generate a secure password')
        print('7. Exit')
        print('='*40)
        
        choice = input('Enter your choice (1-7): ').strip()
        
        if choice == '1':
            service = input('Service name (e.g., Gmail, Facebook): ').strip()
            username = input('Username/email: ').strip()
            password = getpass.getpass('Password (leave blank to generate): ').strip()
            
            if not password:
                password = generate_password()
                print(f'Generated password: {password}')
            
            if service and username and password:
                vault.add_password(service, username, password)
                print('Password saved successfully!')
            else:
                print('Error: All fields are required.')
        
        elif choice == '2':
            service = input('Enter service name: ').strip()
            if service:
                passwords = vault.get_passwords(service)
                if passwords:
                    print(f'\nCredentials for {service}:')
                    print('-' * 40)
                    for i, cred in enumerate(passwords, 1):
                        print(f'{i}. Username: {cred["username"]}')
                        print(f'   Password: {cred["password"]}')
                        print()
                else:
                    print(f'No credentials found for {service}')
            else:
                print('Service name is required.')
        
        elif choice == '3':
            services = vault.list_services()
            if services:
                print('Saved services:')
                for i, service in enumerate(services, 1):
                    print(f'{i}. {service}')
            else:
                print('No services found in vault.')
        
        elif choice == '4':
            service = input('Enter service name: ').strip()
            username = input('Enter username to delete: ').strip()
            if service and username:
                if vault.delete_password(service, username):
                    print('Password deleted successfully!')
                else:
                    print('No matching entry found.')
            else:
                print('Both service and username are required.')
        
        elif choice == '5':
            service = input('Enter service name to delete entirely: ').strip()
            if service:
                confirm = input(f'Are you sure you want to delete all entries for "{service}"? (y/N): ').strip().lower()
                if confirm == 'y':
                    if vault.delete_service(service):
                        print(f'Service "{service}" deleted successfully!')
                    else:
                        print('Service not found.')
                else:
                    print('Deletion cancelled.')
            else:
                print('Service name is required.')
        
        elif choice == '6':
            length = input('Password length (default 16): ').strip()
            try:
                length = int(length) if length else 16
                if length < 6:
                    print('Password should be at least 6 characters long.')
                    length = 16
            except ValueError:
                print('Invalid length, using default 16.')
                length = 16
            
            password = generate_password(length)
            print(f'Generated password: {password}')
        
        elif choice == '7':
            print('Goodbye!')
            break
        
        else:
            print('Invalid choice. Please enter a number between 1-7.')


if __name__ == '__main__':
    main()
