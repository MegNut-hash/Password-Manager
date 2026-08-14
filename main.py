from vault import PasswordVault, generate_password
import getpass
import os
import sys

def main():
    print('=== Welcome to the Secure Password Manager ===')
    print()
    
    # Initialize vault
    vault = PasswordVault()
    
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
        print()
        print('='*50)
        print('Password Manager - Main Menu')
        print('='*50)
        print('1. Add a new password')
        print('2. View passwords for a service')
        print('3. List all services')
        print('4. Delete a password')
        print('5. Delete a service')
        print('6. Generate a secure password')
        print('7. Change master password')
        print('8. Exit')
        print('='*50)
        
        choice = input('Enter your choice (1-8): ').strip()
        
        if choice == '1':
            service = input('Service name (e.g., Gmail, Facebook): ').strip()
            username = input('Username/email: ').strip()
            password = getpass.getpass('Password (leave blank to generate): ').strip()
            
            if not password:
                password = generate_password()
                print(f'Generated password: {password}')
            
            if service and username and password:
                vault.add_password(service, username, password)
                print('? Password saved successfully!')
            else:
                print('? Error: All fields are required.')
        
        elif choice == '2':
            service = input('Enter service name: ').strip()
            if service:
                passwords = vault.get_passwords(service)
                if passwords:
                    print(f'\nCredentials for {service}:')
                    print('-' * 50)
                    for i, cred in enumerate(passwords, 1):
                        # Handle quoting safely
                        username = cred['username']
                        password = cred['password']
                        print(f'{i}. Username: {username}')
                        print(f'   Password: {password}')
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
                    count = len(vault.get_passwords(service))
                    plural = 's' if count != 1 else ''
                    print(f'{i}. {service} ({count} credential{plural})')
            else:
                print('No services found in vault.')
        
        elif choice == '4':
            service = input('Enter service name: ').strip()
            username = input('Enter username to delete: ').strip()
            if service and username:
                if vault.delete_password(service, username):
                    print('? Password deleted successfully!')
                else:
                    print('? No matching entry found.')
            else:
                print('Both service and username are required.')
        
        elif choice == '5':
            service = input('Enter service name to delete entirely: ').strip()
            if service:
                confirm = input(f'Are you sure you want to delete all entries for "{service}"? (y/N): ').strip().lower()
                if confirm == 'y':
                    if vault.delete_service(service):
                        print(f'? Service "{service}" deleted successfully!')
                    else:
                        print('? Service not found.')
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
            print('Change Master Password')
            print('-' * 20)
            current_password = getpass.getpass('Enter current master password: ')
            try:
                vault.set_master_password(current_password)
                # Verify by trying to load vault
                vault._load_vault()
                
                print()
                print('Enter new master password:')
                while True:
                    new_password1 = getpass.getpass('New Master Password: ')
                    new_password2 = getpass.getpass('Confirm New Master Password: ')
                    if new_password1 == new_password2:
                        if len(new_password1) >= 8:
                            vault.set_master_password(new_password1)
                            print('? Master password changed successfully!')
                            break
                        else:
                            print('Password must be at least 8 characters long.')
                    else:
                        print('Passwords do not match. Please try again.')
            except ValueError:
                print('? Current password is incorrect.')
        
        elif choice == '8':
            print('Thank you for using the Password Manager. Goodbye!')
            break
        
        else:
            print('Invalid choice. Please enter a number between 1-8.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\nOperation cancelled by user. Goodbye!')
        sys.exit(0)
