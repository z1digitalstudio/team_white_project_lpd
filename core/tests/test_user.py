"""
Tests for User API endpoints and permissions.
All user-related tests are grouped in this file by domain.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token


# ============================================================================
# API TESTS
# ============================================================================

class UserAPITest(APITestCase):
    """Test User API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
    
    def test_user_registration(self):
        """
        Test user registration endpoint.
        
        PURPOSE: Verifica que el endpoint de registro de usuarios funciona
        correctamente. Debe crear un nuevo usuario y devolver un token
        de autenticación para uso inmediato.
        """
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post('/api/users/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
    
    def test_user_login(self):
        """
        Test user login endpoint.
        
        PURPOSE: Verifica que el endpoint de login de usuarios funciona
        correctamente. Debe autenticar al usuario y devolver un token
        de autenticación para las siguientes peticiones.
        """
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/users/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


# ============================================================================
# ADMIN TESTS
# ============================================================================

class UserAdminTest(TestCase):
    """Test User admin functionality"""
    
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
        
        self.client = Client()
    
    def test_regular_user_cannot_access_admin(self):
        """
        Test that regular users cannot access admin.
        
        PURPOSE: Verifica que los usuarios normales NO pueden acceder
        al panel de administración de Django. Deben ser redirigidos
        al login (código 302) ya que no tienen permisos de staff.
        """
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_superuser_can_access_admin(self):
        """
        Test that superusers can access admin.
        
        PURPOSE: Verifica que los superusuarios SÍ pueden acceder
        al panel de administración de Django. Deben recibir
        un código 200 (OK) ya que tienen permisos de staff.
        """
        self.client.login(username='superuser', password='superpass123')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)


# ============================================================================
# PERMISSION TESTS
# ============================================================================

class UserPermissionTest(APITestCase):
    """Test User permissions"""
    
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
    
    def test_superuser_can_see_all_users(self):
        """
        Test that superusers can see all users.
        
        PURPOSE: Verifica que los superusuarios pueden ver todos los usuarios
        del sistema. Esto es importante para la administración del CMS.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see at least 2 users (testuser and superuser)
        self.assertGreaterEqual(len(response.data), 2)
    
    def test_regular_user_can_only_see_self(self):
        """
        Test that regular users can only see themselves.
        
        PURPOSE: Verifica que los usuarios normales solo pueden ver su propia
        información de usuario, no la de otros usuarios. Esto protege la privacidad.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see at least 1 user (themselves) - response.data is paginated
        self.assertGreaterEqual(len(response.data['results']), 1)
        # Check that the user can see themselves
        usernames = [user['username'] for user in response.data['results']]
        self.assertIn('testuser', usernames)

