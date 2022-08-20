"""
Tests for Models
"""

from multiprocessing.sharedctypes import Value
from venv import create
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core import models

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user"""

    return get_user_model().objects.create_user(email, password)


## User Model Tests
class ModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating User with email is successful"""

        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email = email,
            password = password
        )

        self.assertEqual(email, user.email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test if email is normalized for new users"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@EXAMPLE.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email = email, password = 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'password1')

    def test_create_superuser(self):
        '''Test Creating Superuser'''
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    #### Recipe Tests ####
    def test_create_recipe(self):
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        recipe = models.Recipe.objects.create(
            user = user,
            title = "Sample Recipe Name",
            time_minutes = 5,
            price = Decimal('5.50'),
            description = "Simple Recipe"
        )

        ## Assumed that the __str__ method will return the title
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test Creating Tag is successful"""

        user = create_user()
        tag = models.Tag.objects.create(user=user, name='tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test Creating Ingredient is successful"""

        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name="Ingredient1"
        )

        self.assertEqual(str(ingredient), 'Ingredient1')




