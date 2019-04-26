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
from app import app, CURR_USER_KEY

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
        self.testmessage = Message(text="hello")
        self.testuser.messages.append(self.testmessage)
        db.session.commit()

    def test_follower_following_logged_in(self):
        """When you’re logged in, can you see the follower / following pages
        for any user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        second_user = User.signup(username="testuser2",
                                  email="test2@test.com",
                                  password="testuser2",
                                  image_url=None)
        
        db.session.add(second_user)
        db.session.commit()

        resp = c.get("/users/2/following")
        self.assertEqual(resp.status_code, 200)
    
    def test_follower_following_logged_out(self):
        """When you’re logged out, are you disallowed from visiting a user’s
        follower / following pages?"""

        second_user = User.signup(username="testuser2",
                                  email="test2@test.com",
                                  password="testuser2",
                                  image_url=None)

        db.session.add(second_user)
        db.session.commit()
        with self.client as c:
            resp = c.get("/users/2/following")
            self.assertEqual(resp.status_code, 302)
    
    def test_add_message_logged_out(self):
        """When you’re logged out, are you prohibited from adding messages?"""
    
        with self.client as c:
            resp = c.post("/messages/new", data={"text": "hello"})
            self.assertEqual(resp.status_code, 302)
    
    def test_delete_message_logged_out(self):
        """When you’re logged out, are you prohibited from deleting
        messages?"""
 
        with self.client as c:
            resp = c.post("/messages/1/delete")
            self.assertEqual(resp.status_code, 302)
    
    def test_cant_delete_other_message(self):
        """When you’re logged in, are you prohibiting from deleting a message
        as another user?"""


        
        with self.client as cp:
            second_user = User.signup(username="testuser3",
                                      email="test3@test.com",
                                      password="testuser2",
                                      image_url=None)

            db.session.add(second_user)
            db.session.commit()
            message2 = Message(text="hello2", user_id=second_user.id)
            db.session.add(message2)
            db.session.commit()

            resp = cp.post(f"/messages/{message2.id}/delete")

            self.assertEqual(resp.status_code, 302)
