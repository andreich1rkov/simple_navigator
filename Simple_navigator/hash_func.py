import hashlib
def hash_password(password: str) -> str:
  if not isinstance(password, str):
      raise TypeError()
  encoded_password = password.encode('utf-8')
  hashed_password = hashlib.sha256(encoded_password).hexdigest()
  return hashed_password

def verify_password(password: str, hashed_password: str) -> bool:
    if not isinstance(password, str):
      raise TypeError()
    if not isinstance(hashed_password, str):
        raise TypeError()

    rehashed_password = hash_password(password)
    return rehashed_password == hashed_password