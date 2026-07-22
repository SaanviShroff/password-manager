import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken

ITERATIONS = 600_000

def generate_salt() -> bytes:
    return os.urandom(16)

def derive_key(master_password: str, salt: bytes) -> bytes:
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )

    key = kdf.derive(master_password.encode('utf-8'))
    
    return base64.urlsafe_b64encode(key)

def encrypt_data(key: bytes, plaintext: str) -> bytes:

    f = Fernet(key)

    return f.encrypt(plaintext.encode('utf-8'))

def decrypt_data(key: bytes, ciphertext: bytes) -> str:

    f = Fernet(key)
    try:
        decrypted_bytes = f.decrypt(ciphertext)
        return decrypted_bytes.decode('utf-8')
    except InvalidToken:
        raise ValueError("Invalid Master Password or corrupted data!")

if __name__ == "__main__":
    print("--- Testing Cryptography Core ---")
    
    my_password = "SuperSecretPassword123"
    my_salt = generate_salt()
    
    my_key = derive_key(my_password, my_salt)
    print(f"Derived Key (Base64): {my_key.decode('utf-8')}")
    
    secret_message = "My bank PIN is 1234"
    encrypted_msg = encrypt_data(my_key, secret_message)
    print(f"Encrypted message: {encrypted_msg}")
    
    decrypted_msg = decrypt_data(my_key, encrypted_msg)
    print(f"Decrypted message: {decrypted_msg}")
    
    wrong_key = derive_key("WrongPassword", my_salt)
    try:
        decrypt_data(wrong_key, encrypted_msg)
    except ValueError as e:
        print(f"Intentional Failure Test Passed: {e}")