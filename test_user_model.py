import os
from unittest import TestCase

from models import db, User, Message, Follows
from sqlalchemy.exc import InvalidRequestError, IntegrityError as IE
from psycopg2 import IntegrityError



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

        self.user = User(
                    email='Test-Setup-User@testsetup.com',
                    username='Test-Setup-User',
                    password='Test_SETUP_Hashed',
                    image_url='https://www.tacobell.com/images/22101_crunchy_taco_supreme_269x269.jpg',
                    bio='Test Set User Taco',
                    location='San Francisco'
        )

        self.user2 = User(
                     email='Second-user@user.com',
                     username='follower',
                     password='PASSWORD'
        )
        db.session.add(self.user2)
        db.session.add(self.user)
        db.session.commit()

    def test_user_model(self):
        """Does basic model work?"""
        u = User(
            email="user_instance@test.com",
            username="user_instance",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        self.assertIsInstance(u, User)

    def test_user_create_fails(self):
        """Does the user model fail to create a new user if any of
        the validations fail?"""
        u = User(
            username="follower",
            email="bob@gmail.com",
            password="HASHED_PASSWORD"
        )
 
        db.session.add(u)
        with self.assertRaises(IE):
            db.session.commit()
            
        db.session.rollback()

    def test_user_model_repr(self):
        """Does the repr method work as expected?"""
        u = User(
            email="repr-test@test.com",
            username="repr-test",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        self.assertEqual(f"{u}", f"<User #{u.id}: {u.username}, {u.email}>")


    def test_is_following_true(self):
        """Does is_following successfully detect when user1 is following user2"""
        u1 = User(
                email="test42224@test.com",
                username="testuser532225",
                password="HASHED_PASSWORD"
            )
        u2 = User(
                email="test52225@test.com",
                username="testuser52225",
                password="HASHED_PASSWORD"
            )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        u2.following.append(u1)
        self.assertTrue(u2.is_following(u1))


    def test_is_following_false(self):
        """Does is_following successfully detect when user1 is not following user2?"""
        u1 = User(
                email="test888@test.com",
                username="testuser888",
                password="HASHED_PASSWORD"
            )
        u2 = User(
                email="test765@test.com",
                username="testuser765",
                password="HASHED_PASSWORD"
            )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u2.is_following(u1))

    def test_is_followed_by_true(self):
        """Does is_followed_by successfully detect when user1 is followed by user2?"""
        u1 = User(
                email="test42224@test.com",
                username="testuser532225",
                password="HASHED_PASSWORD"
            )
        u2 = User(
                email="test52225@test.com",
                username="testuser52225",
                password="HASHED_PASSWORD"
            )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        u2.following.append(u1)
        self.assertTrue(u1.is_followed_by(u2))
    
    def test_is_followed_by_false(self):
        """Does is_followed_by successfully detect when user1 is not followed by user2?"""
        u1 = User(
                email="test42224@test.com",
                username="testuser532225",
                password="HASHED_PASSWORD"
            )
        u2 = User(
                email="test52225@test.com",
                username="testuser52225",
                password="HASHED_PASSWORD"
            )
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        self.assertFalse(u1.is_followed_by(u2))


    def test_user_authenticate_success(self):
        """
        Does User.authenticate successfully return a user when given a valid
        username and password?
        """
        u = User.signup("Successful-user",
                        "sucess@sucess.com",
                        "PASSWORD",
                        "http://cdn.onlinewebfonts.com/svg/img_475555.png")
        self.assertTrue(u.authenticate("Sucessful-user", "PASSWORD") is not None)
        self.assertTrue(u.authenticate("sucessful-user", "PASSWORD") is not None)

    def test_user_authenticate_invalid_username(self):
        """
        Does User.authenticate fail to return a user when the username is
        invalid?
        """
        u = User.signup("Invalid-user",
                        "invalid@test.com",
                        "PASSWORD",
                        "http://cdn.onlinewebfonts.com/svg/img_475555.png")
        self.assertFalse(u.authenticate("invalid", "PASSWORD"))
        
    def test_user_authenticate_invalid_password(self):
        """
        Does User.authenticate fail to return a user when the password is
        invalid?
        """
        u = User.signup("invalid-password-user",
                        "invalid-pw@test.com",
                        "PASSWORD",
                        "http://cdn.onlinewebfonts.com/svg/img_475555.png")
        self.assertFalse(u.authenticate("invalid-password-user", "NOTRIGHT"))
        self.assertFalse(u.authenticate("invalid-password-user", "pASSWORD"))