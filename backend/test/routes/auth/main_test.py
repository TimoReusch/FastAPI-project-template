from src.routes.auth.models import PasswordResetToken
from src.routes.users.models import User

def test_post_reset_password(db, client, regular_user):
    url = "/auth/reset-password"

    # User does not exist
    response = client.post(url=url, json={'email': 'tuco@salamanca.biz'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'There is no user with the E-Mail \"tuco@salamanca.biz\".'}

    # User does exist, check if the mail has been sent
    response = client.post(url=url, json={'email': 'kim.wexler@wexler-mcgill.law'})
    assert regular_user.id == db.query(PasswordResetToken).filter(PasswordResetToken.user_id == regular_user.id).count()
    assert response.status_code == 200

# TODO: Your unittests for /auth here
