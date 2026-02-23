from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

def sign_document(pdf_data, private_key):
    """
    pdf_data → the PDF file content in bytes
    private_key → user private key for signing
    """
    
    signature = private_key.sign(
        pdf_data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    return signature