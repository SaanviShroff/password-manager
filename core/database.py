import json
import base64
import os

VAULT_FILE = "vault.json"

def save_vault(ciphertext: bytes, salt: bytes, filename: str = VAULT_FILE) -> None:
    
    salt_str = base64.b64encode(salt).decode('utf-8')
    vault_str = base64.b64encode(ciphertext).decode('utf-8')
    
    data = {
        "salt": salt_str,
        "vault": vault_str
    }
    
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)

def load_vault(filename: str = VAULT_FILE) -> tuple:
    
    if not os.path.exists(filename):
        raise FileNotFoundError("Vault file not found.")
        
    with open(filename, "r") as file:
        data = json.load(file)
        
    salt_str = data["salt"]
    vault_str = data["vault"]
    
    salt = base64.b64decode(salt_str)
    ciphertext = base64.b64decode(vault_str)
    
    return ciphertext, salt

if __name__ == "__main__":
    print("--- Testing Database Core ---")
    
    fake_salt = b'\x01\x02\x03\x04\x05'
    fake_ciphertext = b'this_is_encrypted_gibberish'
    
    print("Saving to JSON...")
    save_vault(fake_ciphertext, fake_salt, "test_vault.json")
    
    print("Loading from JSON...")
    loaded_ciphertext, loaded_salt = load_vault("test_vault.json")
    
    print(f"Original Salt: {fake_salt}")
    print(f"Loaded Salt:   {loaded_salt}")
    print(f"Match? {fake_salt == loaded_salt}")
    
    if os.path.exists("test_vault.json"):
        os.remove("test_vault.json")