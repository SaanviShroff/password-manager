import csv
import json
import os
from . import crypto
from . import database

class VaultManager:
    def __init__(self):
        self.key = None
        self.salt = None 
        self.data = {} 
        self.is_unlocked = False

    def setup_new_vault(self, master_password: str) -> None:
        if os.path.exists(database.VAULT_FILE):
            raise FileExistsError("Vault already exists! Please unlock it instead.")
            
        self.salt = crypto.generate_salt()  # UPDATED
        self.key = crypto.derive_key(master_password, self.salt)
        self.data = {}
        self.is_unlocked = True
        
        self._save()

    def unlock_vault(self, master_password: str) -> bool:
        try:
            ciphertext, self.salt = database.load_vault() 
            self.key = crypto.derive_key(master_password, self.salt)
            
            decrypted_str = crypto.decrypt_data(self.key, ciphertext)
            
            self.data = json.loads(decrypted_str)
            self.is_unlocked = True
            return True
        except Exception as e:
            self.key = None
            self.salt = None
            self.data = {}
            self.is_unlocked = False
            return False

    def add_entry(self, site: str, username: str, password: str) -> None:
        if not self.is_unlocked:
            raise PermissionError("Vault is locked!")
            
        self.data[site] = {
            "username": username,
            "password": password
        }
        self._save()

    def delete_entry(self, site: str) -> None:
        if not self.is_unlocked:
            raise PermissionError("Vault is locked!")
            
        if site in self.data:
            del self.data[site]
            self._save()
        else:
            raise KeyError("Site not found")

    def export_csv(self, filepath: str) -> None:
        """Exports the entire vault to a plain-text CSV file."""
        if not self.is_unlocked:
            raise PermissionError("Vault is locked!")
            
        with open(filepath, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Site", "Username", "Password"])
            
            for site, credentials in self.data.items():
                writer.writerow([site, credentials["username"], credentials["password"]])

    def import_csv(self, filepath: str) -> int:
        """Imports passwords from a CSV and overwrites duplicates."""
        if not self.is_unlocked:
            raise PermissionError("Vault is locked!")
            
        imported_count = 0
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # We expect standard headers: Site, Username, Password
                site = row.get("Site")
                username = row.get("Username", "")
                password = row.get("Password")
                
                if site and password:
                    self.data[site] = {"username": username, "password": password}
                    imported_count += 1
                    
        if imported_count > 0:
            self._save()
            
        return imported_count

    def _save(self) -> None:
        if not self.is_unlocked or self.key is None or self.salt is None:
            raise PermissionError("Cannot save: Vault is locked!")
            
        data_str = json.dumps(self.data)
        ciphertext = crypto.encrypt_data(self.key, data_str)
        
        database.save_vault(ciphertext, self.salt)

if __name__ == "__main__":
    print("--- Testing Vault Manager ---")
    
    if os.path.exists(database.VAULT_FILE):
        os.remove(database.VAULT_FILE)

    manager = VaultManager()
    
    print("1. Setting up new vault...")
    manager.setup_new_vault("MyStrongPassword123")
    
    print("2. Adding entries...")
    manager.add_entry("github.com", "my_user", "super_secret_git_pw")
    manager.add_entry("gmail.com", "user@gmail.com", "email_pw_123")
    
    print(f"Current Memory Data: {manager.data}")
    
    print("\n3. Simulating program restart...")
    manager2 = VaultManager()
    
    print("4. Attempting unlock with WRONG password...")
    success = manager2.unlock_vault("WrongPassword")
    print(f"Unlock success? {success}")
    
    print("5. Attempting unlock with CORRECT password...")
    success = manager2.unlock_vault("MyStrongPassword123")
    print(f"Unlock success? {success}")
    print(f"Recovered Data: {manager2.data}")
    
    if os.path.exists(database.VAULT_FILE):
        os.remove(database.VAULT_FILE)