"""
Data encryption utilities for secure data storage
"""

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64


class DataEncryptor:
    """
    Handles encryption and decryption of sensitive data
    """

    def __init__(self, key: bytes):
        self.key = key
        self.backend = default_backend()

    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        """Generate encryption key from password"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-CBC"""
        # Generate random IV
        iv = os.urandom(16)

        # Pad data
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()

        # Create cipher
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        encryptor = cipher.encryptor()

        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Return IV + encrypted data
        return iv + encrypted_data

    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using AES-256-CBC"""
        # Extract IV
        iv = encrypted_data[:16]
        actual_encrypted_data = encrypted_data[16:]

        # Create cipher
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(iv), backend=self.backend)
        decryptor = cipher.decryptor()

        # Decrypt
        padded_data = decryptor.update(actual_encrypted_data) + decryptor.finalize()

        # Unpad
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()

        return data

    def encrypt_string(self, text: str) -> str:
        """Encrypt string and return base64 encoded"""
        encrypted = self.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded string"""
        encrypted = base64.b64decode(encrypted_text)
        decrypted = self.decrypt(encrypted)
        return decrypted.decode()