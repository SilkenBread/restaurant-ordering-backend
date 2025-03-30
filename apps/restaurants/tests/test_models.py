from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from apps.restaurants.models import Restaurant
from django.db import transaction

class RestaurantModelTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'name': 'Test Restaurant',
            'address': '123 Test St',
            'rating': 4.5,
            'status': 'open',
            'category': 'italian',
            'latitude': 10.0,
            'longitude': -10.0
        }

    def test_create_restaurant_success(self):
        """Test creación exitosa de restaurante"""
        restaurant = Restaurant.objects.create(**self.valid_data)
        self.assertEqual(restaurant.name, 'Test Restaurant')
        self.assertEqual(str(restaurant), 'Test Restaurant')  # Prueba __str__
        self.assertEqual(restaurant.status, 'open')
        self.assertTrue(restaurant.is_active)
        print("✅ Test creación de restaurante exitoso")

    def test_rating_constraint(self):
        """Test que valida la constraint de rating (0-5)"""
        # Versión corregida: usamos IntegrityError y transacción
        from django.db import transaction
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Restaurant.objects.create(
                    **{**self.valid_data, 'rating': 6.0}
                )
        print("✅ Test constraint de rating válido")

    def test_unique_together_constraint(self):
        """Test que valida la combinación única name+address"""
        Restaurant.objects.create(**self.valid_data)
        
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Restaurant.objects.create(**self.valid_data)
        print("✅ Test constraint unique_together válido")
