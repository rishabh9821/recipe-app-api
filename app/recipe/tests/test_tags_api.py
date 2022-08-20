"""Tests for the Tags API"""

import re
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

def get_tag_detail(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password="testpass123"):
    """Create a User"""
    return get_user_model().objects.create_user(email=email, password=password)


################################################################ Public Tests ################################################################

class PublicTagsAPITests(TestCase):
    """Test UnAuthenticated API Request"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that auth is required for get"""

        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################ Private Tests ################################################################

class PrivateTagsAPITests(TestCase):
    """Tests Authorized API Rquests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test getting tags"""

        Tag.objects.create(user=self.user, name="Vegan")
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to user"""

        user2 = create_user(email="user2@example.com")
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_updating_tags(self):
        """Test Updating Tags"""

        tag = Tag.objects.create(user=self.user, name='New Tag')

        payload = {'name': 'New Updated Tag'}
        url = get_tag_detail(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test Deleting a Tag"""
        tag = Tag.objects.create(user=self.user, name='New Tag')
        url = get_tag_detail(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(name='New Tag', user=self.user).exists())


















