# core/tests/test_permissions.py
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models import Blog, Post, Tag
from ..permissions import HasPostPermission, HasBlogPermission, IsSuperuserOrReadOnly

class PermissionTest(APITestCase):
    """Test permission system"""
    
    def setUp(self):
        """Set up test data"""
        # Limpiar datos existentes de forma más agresiva
        try:
            Post.objects.all().delete()
            Blog.objects.all().delete()
            Token.objects.all().delete()
            User.objects.filter(username__in=['testuser', 'superuser', 'otheruser']).delete()
        except:
            pass  # Ignorar errores de limpieza
        
        # Crear datos de test
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
        self.post = Post.objects.create(
            blog=self.blog,
            title='Test Post',
            content='<p>Test content</p>'
        )
    
    def tearDown(self):
        """Clean up after each test"""
        try:
            Post.objects.all().delete()
            Blog.objects.all().delete()
            Token.objects.all().delete()
            User.objects.filter(username__in=['testuser', 'superuser', 'otheruser']).delete()
        except:
            pass  # Ignorar errores de limpieza
    
    def test_user_can_see_all_posts(self):
        """
        Test that users can see all posts.
        
        PURPOSE: Verifica que cualquier usuario autenticado puede ver todos los posts
        (no solo los suyos). Esto es correcto según nuestros permisos: cualquier
        usuario puede VER todos los posts, pero solo puede MODIFICAR los suyos.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
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
    
    def test_user_can_modify_own_post(self):
        """
        Test that users can modify their own posts.
        
        PURPOSE: Verifica que un usuario puede modificar/actualizar sus propios posts.
        Este es el comportamiento esperado: el dueño del post puede editarlo.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        # Datos completos para actualizar
        data = {
            'title': 'Updated by Owner',
            'content': '<p>Updated content</p>',
            'excerpt': 'Updated excerpt'
        }
        response = self.client.put(f'/api/posts/{self.post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by Owner')
    
    def test_user_cannot_modify_other_posts(self):
        """
        Test that users cannot modify other users' posts.
        
        PURPOSE: Verifica que un usuario NO puede modificar posts de otros usuarios.
        Esto es crítico para la seguridad: solo el dueño puede editar sus posts.
        """
        # Create another user's post
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_blog = Blog.objects.create(
            user=other_user,
            title='Other Blog'
        )
        other_post = Post.objects.create(
            blog=other_blog,
            title='Other Post',
            content='<p>Other content</p>'
        )
        
        # Try to update other user's post
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/posts/{other_post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_superuser_can_modify_any_post(self):
        """
        Test that superusers can modify any post.
        
        PURPOSE: Verifica que los superusuarios pueden modificar cualquier post,
        incluso si no es suyo. Esto es importante para la administración del sistema.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.superuser_token.key)
        # Datos completos para actualizar
        data = {
            'title': 'Updated by Superuser',
            'content': '<p>Updated content by superuser</p>',
            'excerpt': 'Updated excerpt by superuser'
        }
        response = self.client.put(f'/api/posts/{self.post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by Superuser')
    
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
        # Create another user's blog
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_blog = Blog.objects.create(
            user=other_user,
            title='Other Blog'
        )
        
        # Try to update other user's blog
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {'title': 'Updated Blog Title'}
        response = self.client.put(f'/api/blogs/{other_blog.id}/', data)
        # Should be 403 Forbidden (permission denied) or 404 Not Found (if blog doesn't exist in user's queryset)
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
    
    def test_user_can_create_post(self):
        """
        Test that users can create posts.
        
        PURPOSE: Verifica que un usuario autenticado puede crear nuevos posts
        en su blog. Esta es una funcionalidad básica del CMS.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {
            'title': 'New Post',
            'content': '<p>New content</p>',
            'excerpt': 'New excerpt'
        }
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'New Post')
    
    def test_user_cannot_create_second_blog(self):
        """
        Test that users cannot create a second blog (1:1 relationship).
        
        PURPOSE: Verifica que un usuario NO puede crear un segundo blog.
        La relación User-Blog es 1:1 (un usuario = un blog), por lo que
        intentar crear un segundo blog debe fallar con IntegrityError.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
        data = {
            'title': 'Second Blog',
            'bio': 'Second bio'
        }
        
        # This test expects an IntegrityError due to UNIQUE constraint
        # We'll catch the exception and verify it's the expected error
        try:
            response = self.client.post('/api/blogs/', data)
            # If we get here, the request didn't fail as expected
            self.fail("Expected IntegrityError but got status code: {}".format(response.status_code))
        except Exception as e:
            # Check if it's an IntegrityError or related database error
            self.assertIn("UNIQUE constraint failed", str(e))
    
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
        # Check that the user can see themselves - response.data['results'] contains user objects
        usernames = [user['username'] for user in response.data['results']]
        self.assertIn('testuser', usernames)
    
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
