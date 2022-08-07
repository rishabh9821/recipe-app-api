from django.test import SimpleTestCase
from app import calc

class AddTest(SimpleTestCase):
    """Test the calc module"""

    def test_add_numbers(self):
        """Test adding numbers together"""
        res = calc.add(5,6)
        self.assertEqual(res, 11)
    
    def test_subtract_numbers(self):
        """Test Subtracting Numbers"""
        res = calc.subtract(6,5)
        self.assertEqual(res, 1)



