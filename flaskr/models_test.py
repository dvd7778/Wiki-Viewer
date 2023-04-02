from flaskr.models import User
import pytest

#pytest fixture for testing
@pytest.fixture(scope="module")
def new_user():
    user = User('barshachy@gmail.com.txt')
    return user
#testing for user class 
def test_new_user(new_user):
    assert new_user.username == 'barshachy@gmail.com.txt'

#testing for user authenticated
def test_is_authenticated(new_user):
    user = User(new_user)
    assert user.is_authenticated() == True

#testing for user logout user
def test_logout_user(new_user):
    user = User(new_user)
    output = user.logout_user()
    assert user.logout_user() == False
#testing for set_name
def test_set_name(new_user):
    user = User(new_user)
    user.set_name("Lia")
    assert user.name == "Lia"

#testing for get_name  
def test_get_name(new_user):
    user = User(new_user)
    get_user = user.get_name()
    assert get_user.username == "barshachy@gmail.com.txt"
    