from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keys():
    
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    
    public_key = private_key.public_key()

    return private_key, public_key


def save_private_key(private_key, filename):
    with open(filename, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
        )


def save_public_key(public_key, filename):
    with open(filename, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )


def load_private_key(filename):
    with open(filename, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(),
            password=None
        )


def load_public_key(filename):
    with open(filename, "rb") as f:
        return serialization.load_pem_public_key(
            f.read()
        )