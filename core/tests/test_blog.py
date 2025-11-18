"""
Tests for Blog model, API endpoints, admin, and permissions.
All blog-related tests are grouped in this file by domain.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models import Blog, Post


# ============================================================================
# MODEL TESTS
# ============================================================================

class BlogModelTest(TestCase):
    """Test Blog model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_blog_creation(self):
        """
        Test that a blog can be created.
        
        PURPOSE: Verifica que el modelo Blog se puede crear correctamente
        con todos sus campos básicos (user, title, bio). Este es el test
        fundamental para asegurar que el modelo funciona.
        """
        blog = Blog.objects.create(
            user=self.user,
            title='Test Blog',
            bio='This is a test blog'
        )
        self.assertEqual(blog.title, 'Test Blog')
        self.assertEqual(blog.user, self.user)
        self.assertEqual(blog.bio, 'This is a test blog')
    
    def test_blog_str_representation(self):
        """
        Test the string representation of Blog.
        
        PURPOSE: Verifica que el método __str__ del modelo Blog funciona
        correctamente. Esto es importante para la visualización en el admin
        y para debugging. El formato debe ser "Título (username)".
        """
        blog = Blog.objects.create(
            user=self.user,
            title='Test Blog'
        )
        expected = f"Test Blog ({self.user.username})"
        self.assertEqual(str(blog), expected)


# ============================================================================
# API TESTS
# ============================================================================

class BlogAPITest(APITestCase):
    """Test Blog API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.blog = Blog.objects.create(
            user=self.user,
            title='Test Blog'
        )


# ============================================================================
# ADMIN TESTS
# ============================================================================

class BlogAdminTest(TestCase):
    """Test Blog admin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@example.com',
            password='superpass123'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.blog = Blog.objects.create(
            user=self.user,
            title='Test Blog'
        )
        
        self.client = Client()
    
    def test_admin_blog_list(self):
        """
        Test admin blog list.
        
        PURPOSE: Verifica que la página de listado de blogs en el admin
        funciona correctamente. Debe mostrar todos los blogs y contener
        el título del blog de prueba.
        """
        self.client.login(username='superuser', password='superpass123')
        response = self.client.get('/admin/core/blog/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Blog')


# ============================================================================
# PERMISSION TESTS
# ============================================================================

class BlogPermissionTest(APITestCase):
    """Test Blog permissions"""
    
    def setUp(self):
        """Set up test data"""
        try:
            Post.objects.all().delete()
            Blog.objects.all().delete()
            Token.objects.all().delete()
            User.objects.filter(username__in=['testuser', 'superuser', 'otheruser']).delete()
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
        
        self.blog = Blog.objects.create(
            user=self.user,
            title='Test Blog'
        )
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            Post.objects.all().delete()
            Blog.objects.all().delete()
            Token.objects.all().delete()
            User.objects.filter(username__in=['testuser', 'superuser', 'otheruser']).delete()
        except:
            pass
    
    def test_user_can_see_all_blogs(self):
        """
        Test that users can see all blogs.
        
        PURPOSE: Verifica que cualquier usuario autenticado puede ver todos los blogs
        (no solo el suyo). Esto es correcto según nuestros permisos: cualquier
        usuario puede VER todos los blogs, pero solo puede MODIFICAR el suyo.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response = self.client.get('/api/blogs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_user_can_modify_own_blog(self):
        """
        Test that users can modify their own blog.
        
        PURPOSE: Verifica que un usuario puede modificar su propio blog.
        Cada usuario tiene un blog (relación 1:1) y debe poder editarlo.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {'title': 'Updated Blog by Owner'}
        response = self.client.put(f'/api/blogs/{self.blog.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Blog by Owner')
    
    def test_user_cannot_modify_other_blogs(self):
        """
        Test that users cannot modify other users' blogs.
        
        PURPOSE: Verifica que un usuario NO puede modificar blogs de otros usuarios.
        Esto es crítico para la seguridad: solo el dueño puede editar su blog.
        """
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_blog = Blog.objects.create(
            user=other_user,
            title='Other Blog'
        )
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {'title': 'Updated Blog Title'}
        response = self.client.put(f'/api/blogs/{other_blog.id}/', data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
    
    def test_superuser_can_modify_any_blog(self):
        """
        Test that superusers can modify any blog.
        
        PURPOSE: Verifica que los superusuarios pueden modificar cualquier blog,
        incluso si no es suyo. Esto es importante para la administración del sistema.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        data = {'title': 'Updated Blog by Superuser'}
        response = self.client.put(f'/api/blogs/{self.blog.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated Blog by Superuser')
    
    def test_user_cannot_create_second_blog(self):
        """
        Test that users cannot create a second blog (1:1 relationship).
        
        PURPOSE: Verifica que un usuario NO puede crear un segundo blog.
        La relación User-Blog es 1:1 (un usuario = un blog), por lo que
        intentar crear un segundo blog debe fallar con error 400.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {
            'title': 'Second Blog',
            'bio': 'Second bio'
        }
        
        response = self.client.post('/api/blogs/', data)
        # Should return 400 Bad Request (handled by BlogViewSet.create)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

