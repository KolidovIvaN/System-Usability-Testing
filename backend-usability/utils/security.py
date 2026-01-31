from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=1,
    hash_len=32,
    salt_len=16
)

def get_password_hash(password: str) -> str:
    print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!pass: {password}, {type(password)}")
    if len(password.encode("utf-8")) > 1024:
        raise ValueError("Password too long")
    
    return ph.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, plain_password)
        return True
    except VerifyMismatchError:
        return False