# from flask_sqlalchemy import SQLAlchemy
# sqlalchemy = SQLAlchemy()

import os
from unittest import TestCase
from sqlalchemy.exc import InvalidRequestError, IntegrityError as IE
from psycopg2 import IntegrityError
from models import db, User, Message, Follows, Like
# from sqlalchemy import InvalidRequestError


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


class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()
        self.client = app.test_client()

    def test_message_model(self):
        """Does basic model work?"""
        u = User(
            email="test4334344@test.com",
            username="testuser334342",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        m = Message(
            text="test",
            user_id=u.id
        )
        db.session.add(m)
        db.session.commit()
        self.assertIsInstance(m, Message)

    def test_message_create_fails(self):
        """Does the message model fail to create a new message if any of
        the validations fail?"""
        m = Message(
            text="test",
            user_id=5022
        )
        db.session.add(m)
        with self.assertRaises(IE):
            db.session.commit()
            
        db.session.rollback()

    def test_message_belongs_to_user_true(self):
        u = User(
            email="test4455@test.com",
            username="testuser355552",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
        m = Message(
            text="test",
            user_id=u.id
        )

        u.messages.append(m)
        self.assertEqual(m.user_id, u.id)
            
    def test_message_belongs_to_user_false(self):
        """Can you prove user does not own message?"""
        u = User(
            email="test4455@test.com",
            username="testuser355552",
            password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
        m = Message(
            text="test",
            user_id=2
        )

        self.assertNotEqual(m.user_id, u.id)

    def test_user_likes_message_true(self):
        """Can you prove user likes a message?"""
        u = User(
        email="testlikes5@test.com",
        username="testuserlikes552",
        password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()
        
        m = Message(
            text="test",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        like = Like(message_id=m.id, user_id=u.id)
        db.session.add(like)
        db.session.commit()

        self.assertEqual(like.message_id, m.id)
        self.assertEqual(like.user_id, u.id)

    def test_user_likes_message_false(self):
        """Can you prove user does not like a message?"""
        u = User(
        email="testlikes5@test.com",
        username="testuserlikes552",
        password="HASHED_PASSWORD"
        )
        db.session.add(u)
        db.session.commit()

        u2 = User(
        email="test2user5@test.com",
        username="test2user2likes552",
        password="HASHED_PASSWORD"
        )
        
        db.session.add(u2)
        db.session.commit()

        m = Message(
            text="test",
            user_id=u.id
        )

        db.session.add(m)
        db.session.commit()

        like = Like(message_id=m.id, user_id=u.id)
        db.session.add(like)
        db.session.commit()

        self.assertEqual(like.message_id, m.id)
        self.assertNotEqual(like.user_id, u2.id)