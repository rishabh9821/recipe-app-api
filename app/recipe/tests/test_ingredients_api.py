"""Tests from Ingredients API"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

################################################################ Helper Functions ################################################################
INGREDIENTS_URL = reverse('recipe:ingredient-list')

def get_ingredient_url(ingredient_url):
    return reverse('recipe:ingredient-detail', args=[ingredient_url])

def create_user(email="user@example.com", password='testpass123'):
    return get_user_model().objects.create(email = email, password = password)

################################################################ Public Tests ################################################################
class PublicIngredientsAPITests(TestCase):
    """Test UnAuthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test If Authorization is required for endpoint"""
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

################################################################ Private Tests ################################################################
class PrivateIngredientsAPITests(TestCase):
    """Test Authenticated API Requests"""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving list of ingredients"""
        Ingredient.objects.create(name='Kale', user=self.user)
        Ingredient.objects.create(name='Pickle', user=self.user)

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredients_limited_to_user(self):
        """List of Ingredients Limited to User"""

        userTwo = create_user(email='user2@example.com')
        in1 = Ingredient.objects.create(user = userTwo, name = 'Cauliflower')
        Ingredient.objects.create(user = self.user, name = 'Sunflower Seeds')
        Ingredient.objects.create(user = self.user, name = 'Watermelon')

        res = self.client.get(INGREDIENTS_URL)
        ingredient_list = Ingredient.objects.filter(user=self.user).order_by('-name')
        serializer = IngredientSerializer(ingredient_list, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        self.assertNotIn(in1, res.data)

    def test_update_ingredients(self):
        in1 = Ingredient.objects.create(user=self.user, name="Sunflower Seeds")
        payload = {
            'name': 'Watermelon Seeds'
        }

        url = get_ingredient_url(in1.id)
        res = self.client.put(url, payload)
        in1.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(in1.name, payload['name'])

    def test_delete_ingredients(self):
        in1 = Ingredient.objects.create(user=self.user, name="Sunflower Seeds")

        url = get_ingredient_url(in1.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(user=self.user, name='Sunflower Seeds').exists())












