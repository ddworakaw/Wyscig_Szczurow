from cryptography.fernet import Fernet

key = b'owdCX2JF1dWxHoB4t4FZ8fnVqo4SxplwE7SNqqp_ywU='
f = Fernet(key)
def encrypt(data):
    data = data.encode()
    return f.encrypt(data)

def decrypt(data):
    if data is None:
        return ""
    data = f.decrypt(data)
    return data.decode()
