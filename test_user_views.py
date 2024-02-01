# Tests for User Views
# Execute these tests via: FLASK_ENV=production python -m unittest test_user_views.py

import os
from unittest import TestCase
from models import db, User, Message, Likes, Follows
from bs4 import BeautifulSoup
from app import app, CURR_USER_KEY

# Configuring test database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Importing app after setting test database
from app import app

# Initialize database tables for testing
db.create_all()

# Disable CSRF for testing convenience
app.config['WTF_CSRF_ENABLED'] = False

class TestUserViews(TestCase):
    """Tests for user-related views."""

    def setUp(self):
        """Set up test data before each test."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Create sample users
        self.sample_user = User.signup(username="sampleuser", email="sample@test.com", password="password", image_url=None)
        self.sample_user_id = 9999
        self.sample_user.id = self.sample_user_id

        self.user1 = User.signup("user1", "user1@test.com", "password1", None)
        self.user1_id = 1111
        self.user1.id = self.user1_id
        self.user2 = User.signup("user2", "user2@test.com", "password2", None)
        self.user2_id = 2222
        self.user2.id = self.user2_id

        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transactions."""
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_user_directory(self):
        """Test the user index page."""
        with self.client as c:
            response = c.get("/users")
            self.assertIn("@sampleuser", str(response.data))
            self.assertIn("@user1", str(response.data))
            self.assertIn("@user2", str(response.data))

    def test_user_search(self):
        """Test user search functionality."""
        with self.client as c:
            response = c.get("/users?q=sample")

            self.assertIn("@sampleuser", str(response.data))
            self.assertNotIn("@user1", str(response.data))
            self.assertNotIn("@user2", str(response.data))

    # Additional tests for user views would follow similar refactoring

