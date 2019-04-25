import os
from unittest import TestCase

from models import db, User, Message, Follows


# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""
        u = User(
            email="test44@test.com",
            username="testuser32",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        self.assertIsInstance(u, User)

    def test_user_create_fails(self):
        """Does the user model fail to create a new user if any of
        the validations fail?"""
        u = User(
            email="testuser59@test.com",
            username="testuser59",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        # self.assertIn()



    def test_user_model_repr(self):
        """Does the repr method work as expected?"""
        u = User(
            email="test3@test.com",
            username="testuser3",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")



    # def test_is_following_true(self):
    #     """Does is_following successfully detect when user1 is following user2"""



    # def test_is_following_false(self):
    #     """Does is_following successfully detect when user1 is not following user2?"""


    # def test_is_followed_by_true(self):
    #     """Does is_followed_by successfully detect when user1 is followed by user2?"""

    
    # def test_is_followed_by_false(self):
    #     """Does is_followed_by successfully detect when user1 is not followed by user2?"""

    def test_user_authenticate_success(self):
        """
        Does User.authenticate successfully return a user when given a valid
        username and password?
        """
        u = User.signup("testuser3",
                        "test3@test.com",
                        "PASSWORD",
                        "http://cdn.onlinewebfonts.com/svg/img_475555.png")
        self.assertTrue(u.authenticate("testuser3", "PASSWORD") is not None)

    def test_user_authenticate_invalid_username(self):
        """
        Does User.authenticate fail to return a user when the username is
        invalid?
        """
        u = User.signup("testuser4",
                        "test4@test.com",
                        "PASSWORD",
                        "http://cdn.onlinewebfonts.com/svg/img_475555.png")
        self.assertFalse(u.authenticate("NOTRIGHT", "PASSWORD"))
        
    def test_user_authenticate_invalid_password(self):
        """
        Does User.authenticate fail to return a user when the password is
        invalid?
        """
        u = User.signup("testuser5",
                        "test5@test.com",
                        "PASSWORD",
                        "http://cdn.onlinewebfonts.com/svg/img_475555.png")
        self.assertFalse(u.authenticate("testuser5", "NOTRIGHT"))