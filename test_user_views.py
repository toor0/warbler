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


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        self.client = app.test_client()
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()


    def test_follower_following_logged_in(self):
        """When you’re logged in, can you see the follower / following pages
        for any user?"""

    
    def test_follower_following_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s
        follower / following pages?"""
    

    def test_add_message_logged_out(self):
        """When you’re logged out, are you prohibited from adding messages?"""
    
    
    def test_delete_message_logged_out(self):
        """When you’re logged out, are you prohibited from deleting
        messages?"""
    
    
    def test_cant_add_other_message(self):
        """When you’re logged in, are you prohibiting from adding a message
        as another user?"""
    
    
    def test_cant_delete_other_message(self):
        """When you’re logged in, are you prohibiting from deleting a message
        as another user?"""
