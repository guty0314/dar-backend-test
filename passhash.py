from pwdlib import PasswordHash
import sys

def main():
    password_hash = PasswordHash.recommended()
    password = sys.argv[1] if len(sys.argv) > 1 else None
    if not password:
        password = input("Ingresa la contraseña a hashear:")

    hashed = password_hash.hash(password)
    print(hashed)

if __name__ == "__main__":
    main()