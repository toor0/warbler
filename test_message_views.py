# run these tests like:
# FLASK_ENV=production python -m unittest test_message_views.py

import os
from unittest import TestCase
from models import db, connect_db, Message, User

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

# Don't have WTForms use CSRF at all, since it's a pain to test
app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        self.client = app.test_client()
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

    def test_add_message(self):
        """Can a user add a message?"""
            resp = c.post("/messages/new", data={"text": "Hello"})
            self.assertEqual(resp.status_code, 302)
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_show_message(self):
        """Is a user able to view a page detailing a single message?"""

    def test_delete_message(self):
        """Is a user able to delete a message?"""

    def test_like_message(self):
        """Is a user able to like a message?"""

    def test_unlike_message(self):
        """Is a user able to unlike a message?"""