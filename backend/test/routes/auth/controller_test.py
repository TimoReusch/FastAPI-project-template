from src.routes.auth.controller import verify_password, get_password_hash


def test_verify_password():
    # Plain and hash match
    assert verify_password("asdf", get_password_hash("asdf")) == True
    # Plain and hash do not match
    assert verify_password("asdf", get_password_hash("fdsa")) == False
