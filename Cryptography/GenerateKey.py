from cryptography.fernet import Fernet
# File to generate an encryption key
key = Fernet.generate_key()
file = open("encryption_key.txt","wb")
file.write(key)
file.close()













