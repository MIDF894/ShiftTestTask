import jwt
from src.shifttestex.database.models import User, UserRole
from src.shifttestex.app.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    password_hash,
)


def test_password_hash_and_verify():
    password = "my_secret_password"
    hashed = password_hash.hash(password)

    assert hashed != password
    assert password_hash.verify(password, hashed) is True
    assert password_hash.verify("wrong_password", hashed) is False


def test_jwt_token_payload():
    fake_user = User(id=1, username="testuser", role=UserRole.EMPLOYEE)
    token = create_access_token(fake_user)

    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "1"
    assert decoded["role"] == UserRole.EMPLOYEE.value
    assert "exp" in decoded