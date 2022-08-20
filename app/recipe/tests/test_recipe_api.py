"""Tests for Recipe API"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


def detail_url(recipe_id):
    """Create and return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_recipe(user, **params):
    defaults = {
        'title': 'Sample Recipe Title',
        'description': 'New Recipe for dada',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'link': 'https://www.example.com/recipe.pdf'
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user = user, **defaults)
    return recipe

def create_user(**params):
    """Create a new user"""
    return get_user_model().objects.create(**params)

############################################ Public Recipe Tests ############################################

RECIPES_URL = reverse('recipe:recipe-list')
class PublicRecipeAPITest(TestCase):
    """Test Unauthenticated API Requests"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test Auth is required to call API"""

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

############################################ Private Recipe Tests ############################################

class PrivateRecipeAPITest(TestCase):
    """Test UnAuthenticated API Request"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        ## Create Recipes
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        ## Use HTTP GET to retrieve the recipes
        res = self.client.get(RECIPES_URL)

        ## Get all recipes and push through serializer
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        ## Assert that the recipes equal the HTTP GET Recipes
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipe_list_limited_to_user(self):
        """Test if recipe list is limited to user"""

        userTwo = get_user_model().objects.create_user(
            'other@example.com',
            'testnewpass123'
        )

        create_recipe(user=userTwo)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        myRecipes = Recipe.objects.filter(user = self.user)
        mySerializer = RecipeSerializer(myRecipes, many = True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, mySerializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail"""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe_id = recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test Creating a Recipe"""

        payload = {
            'title': 'Sample Recipe Title',
            'description': 'New Recipe for dada',
            'time_minutes': 22,
            'price': Decimal('5.25'),
            'link': 'https://www.example.com/recipe.pdf',
        }

        res = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(id = res.data['id'])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(recipe.user, self.user)

    def test_partial_update(self):
        """Test Partial Update to recipe"""

        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user = self.user,
            title = 'Sample Recipe Title',
            link = original_link
        )

        payload = {'title': 'New Sample Recipe Title'}
        url = detail_url(recipe_id = recipe.id)
        res = self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test Full Update of Recipe"""

        recipe = create_recipe(
            user = self.user
        )
    #     default recipe linked here defaults = {'title': 'Sample Recipe Title','description': 'New Recipe for dada', 'time_minutes': 22,'price': Decimal('5.25'),'link': 'https://www.example.com/recipe.pdf'}

        payload = {
            'title': 'New Title',
            'description': 'COmpletely New Desc',
            'time_minutes': 12,
            'price': Decimal('5.11'),
            'link': 'https://example.com/new_recipe.pdf',
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

        self.assertEqual(self.user, recipe.user)

    def test_update_user_returns_error(self):
        """Test changing the recipe user results in error"""

        new_user = create_user(email = 'user2@example.com', password='newpass123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user}
        url = detail_url(recipe_id=recipe.id)

        res = self.client.patch(url, payload)
        recipe.refresh_from_db()

        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful"""
        recipe = create_recipe(user=self.user)

        url = detail_url(recipe_id=recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id = recipe.id).exists())

    def test_recipe_other_users_recipe_error(self):
        new_user = create_user(email = 'user2@example.com', password='newpass123')
        recipe = create_recipe(user=new_user)

        url = detail_url(recipe_id = recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id = recipe.id).exists())

    def test_create_recipe_with_new_tags(self):
        """Test Creating Recipe with new tags"""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(),2)
        for tag in payload['tags']:
            self.assertTrue(recipe.tags.filter(name=tag['name'], user=self.user).exists())

    def test_create_recipe_with_existing_tags(self):
        """Test Create recipe with existing tags"""

        tag = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': "Indian"}, {'name': 'Breakfast'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag, recipe.tags.all())

        for tag in payload['tags']:
            self.assertTrue(recipe.tags.filter(name=tag['name'], user=self.user).exists())

    def test_create_tag_on_update(self):
        """Test creating tag when updating the recipe"""

        recipe = create_recipe(user=self.user)

        payload = {'tags':[{'name':'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe"""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test Clearing a Recipe Tags"""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        recipe.refresh_from_db()

        payload = {'tags':[]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(),0)

    def test_creating_recipe_with_new_ingredients(self):
        """Test Creating Recipes With New Ingredients"""

        payload = {
            'title': 'Burger',
            'description': "Quick Desc",
            'time_minutes': 20,
            'price': Decimal('2.50'),
            'link': "https://example.com",
            'ingredients': [{'name': 'Beef'},{'name': 'Bun'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)

        for ingredient in payload['ingredients']:
            self.assertTrue(Ingredient.objects.filter(name=ingredient['name'], user=self.user).exists())

    def test_creating_recipe_with_existing_ingredients(self):
        """Test Creating Recipe with Existing Ingredients"""

        ingredient = Ingredient.objects.create(user=self.user, name='Watermelon Seeds')

        payload = {
            'title': 'Burger',
            'description': "Quick Desc",
            'time_minutes': 20,
            'price': Decimal('2.50'),
            'link': "https://example.com",
            'ingredients': [{'name': 'Beef'},{'name': 'Watermelon Seeds'}],
        }

        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(),1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(),2)
        self.assertIn(ingredient, recipe.ingredients.all())

        for ingredient in payload['ingredients']:
            self.assertTrue(Ingredient.objects.filter(user=self.user, name=ingredient['name']).exists())

    def test_updating_recipe_with_new_ingredients(self):
        """Test Adding New Ingredients to existing recipe"""

        recipe = create_recipe(user = self.user)

        payload = {
            'ingredients': [{'name': 'Beef'}, {'name': 'Provolone'}]
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()

        print(recipe.ingredients.all())

        self.assertEqual(recipe.ingredients.count(), 2)

        for ingredient in payload['ingredients']:
            ingredient_obj = Ingredient.objects.filter(name=ingredient['name'])
            self.assertTrue(ingredient_obj.exists())
            self.assertIn(ingredient_obj[0], recipe.ingredients.all())

    def test_updating_recipe_with_existing_ingredients(self):
        """Test Updating Recipe with existing ingredients along with new ingredients"""

        recipe = create_recipe(user=self.user)
        ingredient = Ingredient.objects.create(name='Chicken', user=self.user)

        payload = {
            'ingredients' : [{'name': 'Whiskey'}, {'name': 'Chicken'}]
        }

        url = detail_url(recipe_id = recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertTrue(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertIn(ingredient, recipe.ingredients.all())
        ingredient_whis = Ingredient.objects.filter(name = 'Whiskey')[0]

        self.assertIn(ingredient_whis, recipe.ingredients.all())


























