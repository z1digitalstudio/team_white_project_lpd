"""
Tests for Tag model, API endpoints, admin, and permissions.
All tag-related tests are grouped in this file by domain.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models import Tag


# ============================================================================
# MODEL TESTS
# ============================================================================

class TagModelTest(TestCase):
    """Test Tag model functionality"""
    
    def test_tag_creation(self):
        """
        Test that a tag can be created.
        
        PURPOSE: Verifica que el modelo Tag se puede crear correctamente
        con su campo name. Los tags son elementos simples pero importantes
        para categorizar posts.
        """
        tag = Tag.objects.create(name='Django')
        self.assertEqual(tag.name, 'Django')
    
    def test_tag_str_representation(self):
        """
        Test the string representation of Tag.
        
        PURPOSE: Verifica que el método __str__ del modelo Tag funciona
        correctamente. Para los tags, el string representation debe ser
        simplemente el nombre del tag.
        """
        tag = Tag.objects.create(name='Python')
        self.assertEqual(str(tag), 'Python')
    
    def test_tag_unique_name(self):
        """
        Test that tag names must be unique.
        
        PURPOSE: Verifica que los nombres de los tags deben ser únicos.
        Esto evita duplicados y mantiene la consistencia en el sistema.
        Si se intenta crear un tag con un nombre que ya existe, debe fallar.
        """
        Tag.objects.create(name='Django')
        with self.assertRaises(Exception):
            Tag.objects.create(name='Django')


# ============================================================================
# API TESTS
# ============================================================================

class TagAPITest(APITestCase):
    """Test Tag API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )
        
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)
    
    def test_tag_creation(self):
        """
        Test tag creation endpoint.
        
        PURPOSE: Verifica que solo los superusuarios pueden crear tags
        a través de la API. Los tags son elementos globales del sistema,
        por lo que solo los administradores pueden crearlos.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        data = {'name': 'Django'}
        response = self.client.post('/api/tags/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Django')


# ============================================================================
# ADMIN TESTS
# ============================================================================

class TagAdminTest(TestCase):
    """Test Tag admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )
        
        self.tag = Tag.objects.create(name='Django')
        
        self.client = Client()
    
    def test_admin_tag_list(self):
        """
        Test admin tag list.
        
        PURPOSE: Verifica que la página de listado de tags en el admin
        funciona correctamente. Debe mostrar todos los tags y contener
        el nombre del tag de prueba.
        """
        self.client.login(username='superuser', password='superpass123')
        response = self.client.get('/admin/core/tag/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django')


# ============================================================================
# PERMISSION TESTS
# ============================================================================

class TagPermissionTest(APITestCase):
    """Test Tag permissions"""
    
    def setUp(self):
        """Set up test data"""
        try:
            Token.objects.all().delete()
            User.objects.filter(username__in=['testuser', 'superuser']).delete()
        except:
            pass
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )
        
        self.user_token = Token.objects.create(user=self.user)
        self.superuser_token = Token.objects.create(user=self.superuser)
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            Token.objects.all().delete()
            User.objects.filter(username__in=['testuser', 'superuser']).delete()
        except:
            pass
    
    def test_superuser_can_create_tags(self):
        """
        Test that superusers can create tags.
        
        PURPOSE: Verifica que solo los superusuarios pueden crear tags.
        Los tags son elementos globales del sistema, por lo que solo los
        administradores pueden crearlos para mantener la consistencia.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        data = {'name': 'Django'}
        response = self.client.post('/api/tags/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'Django')
    
    def test_regular_user_cannot_create_tags(self):
        """
        Test that regular users cannot create tags.
        
        PURPOSE: Verifica que los usuarios normales NO pueden crear tags.
        Solo los superusuarios pueden crear tags para mantener la consistencia
        y evitar duplicados en el sistema.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {'name': 'Django'}
        response = self.client.post('/api/tags/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

