# User Model Unit Tests
# Execute these tests with: python -m unittest test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows
from app import app

# Setting up a test database before importing the app
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Importing app after environment variable is set
from app import app

# Initializing database tables
db.create_all()

class TestUserModel(TestCase):
    """Suite of tests for user model behaviors."""

    def setUp(self):
        """Set up a clean database and test client before each test."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("user1", "user1@test.com", "testpassword1", None)
        user1_id = 1001
        user1.id = user1_id

        user2 = User.signup("user2", "user2@test.com", "testpassword2", None)
        user2_id = 2002
        user2.id = user2_id

        db.session.commit()

        self.user1 = User.query.get(user1_id)
        self.user2 = User.query.get(user2_id)
        self.client = app.test_client()

    def tearDown(self):
        """Clean up any failed transactions."""
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_basic_user_model(self):
        """Test the basic functionality of the User model."""
        user = User(email="newuser@test.com", username="newuser", password="HASHED_PASSWORD")
        db.session.add(user)
        db.session.commit()

        self.assertEqual(len(user.messages), 0)
        self.assertEqual(len(user.followers), 0)

    # Tests for following functionality

    def test_user_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)

        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)

    def test_following_status(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_follower_status(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    # Tests for user signup

    def test_successful_signup(self):
        new_user = User.signup("newusername", "newuser@test.com", "newpassword", None)
        new_user_id = 3003
        new_user.id = new_user_id
        db.session.commit()

        retrieved_user = User.query.get(new_user_id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "newusername")
        self.assertNotEqual(retrieved_user.password, "newpassword")
        self.assertTrue(retrieved_user.password.startswith("$2b$"))

    def test_signup_with_invalid_data(self):
        with self.assertRaises(exc.IntegrityError):
            User.signup(None, "test@test.com", "password", None)
            db.session.commit()

    def test_signup_without_password(self):
        with self.assertRaises(ValueError):
            User.signup("testusername", "test@test.com", "", None)

    # Tests for user authentication

    def test_valid_authentication(self):
        authenticated_user = User.authenticate(self.user1.username, "testpassword1")
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.id, self.user1.id)

    def test_invalid_authentication(self):
        self.assertFalse(User.authenticate("wrongusername", "testpassword1"))
        self.assertFalse(User.authenticate(self.user1.username, "wrongpassword"))
