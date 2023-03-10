from flaskr.models import User
import pytest

@pytest.fixture(scope="module")
def new_user():
    user = User('barshachy@gmail.com.txt')
    return user
def test_new_user(new_user):
    assert new_user.username == 'barshachy@gmail.com.txt'
    