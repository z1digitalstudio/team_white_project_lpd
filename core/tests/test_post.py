"""
Tests for Post model, API endpoints, admin, and permissions.
All post-related tests are grouped in this file by domain.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from ..models import Blog, Post, Tag


# ============================================================================
# MODEL TESTS
# ============================================================================

class PostModelTest(TestCase):
    """Test Post model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.blog = Blog.objects.create(
            user=self.user,
            title='Test Blog'
        )
    
    def test_post_creation(self):
        """
        Test that a post can be created.
        
        PURPOSE: Verifica que el modelo Post se puede crear correctamente
        con todos sus campos básicos (blog, title, content, excerpt).
        También verifica que is_published tiene el valor por defecto False.
        """
        post = Post.objects.create(
            blog=self.blog,
            title='Test Post',
            content='<p>This is test content</p>',
            excerpt='Test excerpt'
        )
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.blog, self.blog)
        self.assertFalse(post.is_published)  # Default should be False
    
    def test_post_str_representation(self):
        """
        Test the string representation of Post.
        
        PURPOSE: Verifica que el método __str__ del modelo Post funciona
        correctamente. Para los posts, el string representation debe ser
        el título del post.
        """
        post = Post.objects.create(
            blog=self.blog,
            title='Test Post',
            content='<p>Test content</p>'
        )
        self.assertEqual(str(post), 'Test Post')
    
    def test_post_slug_generation(self):
        """
        Test that slug is automatically generated.
        
        PURPOSE: Verifica que el slug se genera automáticamente a partir
        del título del post. Los slugs son importantes para URLs amigables
        y SEO. El slug debe ser la versión "slugificada" del título.
        """
        post = Post.objects.create(
            blog=self.blog,
            title='Test Post Title',
            content='<p>Test content</p>'
        )
        # Slug should be generated from title
        self.assertTrue(post.slug.startswith('test-post-title'))
    
    def test_post_with_tags(self):
        """
        Test that a post can have tags.
        
        PURPOSE: Verifica que la relación Many-to-Many entre Post y Tag
        funciona correctamente. Un post puede tener múltiples tags y
        un tag puede estar en múltiples posts. Esto es fundamental
        para el sistema de categorización del CMS.
        """
        tag1 = Tag.objects.create(name='Django')
        tag2 = Tag.objects.create(name='Python')
        
        post = Post.objects.create(
            blog=self.blog,
            title='Test Post',
            content='<p>Test content</p>'
        )
        post.tags.add(tag1, tag2)
        
        self.assertEqual(post.tags.count(), 2)
        self.assertIn(tag1, post.tags.all())
        self.assertIn(tag2, post.tags.all())


# ============================================================================
# API TESTS
# ============================================================================

class PostAPITest(APITestCase):
    """Test Post API endpoints"""
    
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
    
    def test_post_creation(self):
        """
        Test post creation endpoint.
        
        PURPOSE: Verifica que el endpoint de creación de posts funciona
        correctamente. Un usuario autenticado debe poder crear posts
        en su blog con todos los campos necesarios.
        """
        data = {
            'title': 'Test Post',
            'content': '<p>Test content</p>',
            'excerpt': 'Test excerpt',
            'is_published': True
        }
        response = self.client.post('/api/posts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Post')
    
    def test_post_list(self):
        """
        Test post list endpoint.
        
        PURPOSE: Verifica que el endpoint de listado de posts funciona
        correctamente. Debe devolver todos los posts disponibles con
        paginación (por eso se usa response.data['results']).
        """
        Post.objects.create(
            blog=self.blog,
            title='Test Post',
            content='<p>Test content</p>'
        )
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_post_permissions(self):
        """
        Test that users can only modify their own posts.
        
        PURPOSE: Verifica que el sistema de permisos funciona correctamente
        en la API. Un usuario NO debe poder modificar posts de otros usuarios,
        debe recibir un error 403 Forbidden.
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
        other_post = Post.objects.create(
            blog=other_blog,
            title='Other Post',
            content='<p>Other content</p>'
        )
        
        data = {'title': 'Updated Title'}
        response = self.client.put(f'/api/posts/{other_post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_published_posts_filter(self):
        """
        Test published posts filter.
        
        PURPOSE: Verifica que el filtro de posts publicados funciona
        correctamente. Solo debe devolver posts con is_published=True,
        excluyendo los borradores (is_published=False).
        """
        Post.objects.create(
            blog=self.blog,
            title='Published Post',
            content='<p>Published content</p>',
            is_published=True
        )
        Post.objects.create(
            blog=self.blog,
            title='Unpublished Post',
            content='<p>Unpublished content</p>',
            is_published=False
        )
        
        response = self.client.get('/api/posts/published/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Published Post')
    
    def test_posts_by_tag_filter(self):
        """
        Test posts by tag filter.
        
        PURPOSE: Verifica que el filtro de posts por tag funciona
        correctamente. Debe devolver solo los posts que tienen
        el tag especificado en el parámetro de consulta.
        """
        tag = Tag.objects.create(name='Django')
        post = Post.objects.create(
            blog=self.blog,
            title='Django Post',
            content='<p>Django content</p>'
        )
        post.tags.add(tag)
        
        response = self.client.get('/api/posts/by_tag/?tag=Django')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django Post')


# ============================================================================
# ADMIN TESTS
# ============================================================================

class PostAdminTest(TestCase):
    """Test Post admin functionality"""
    
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
        self.post = Post.objects.create(
            blog=self.blog,
            title='Test Post',
            content='<p>Test content</p>'
        )
        
        self.client = Client()
    
    def test_admin_post_list(self):
        """
        Test admin post list.
        
        PURPOSE: Verifica que la página de listado de posts en el admin
        funciona correctamente. Debe mostrar todos los posts y contener
        el título del post de prueba.
        """
        self.client.login(username='superuser', password='superpass123')
        response = self.client.get('/admin/core/post/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Post')


# ============================================================================
# PERMISSION TESTS
# ============================================================================

class PostPermissionTest(APITestCase):
    """Test Post permissions"""
    
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
            pass
    
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
    
    def test_user_can_modify_own_post(self):
        """
        Test that users can modify their own posts.
        
        PURPOSE: Verifica que un usuario puede modificar/actualizar sus propios posts.
        Este es el comportamiento esperado: el dueño del post puede editarlo.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.user_token.key)
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
        data = {
            'title': 'Updated by Superuser',
            'content': '<p>Updated content by superuser</p>',
            'excerpt': 'Updated excerpt by superuser'
        }
        response = self.client.put(f'/api/posts/{self.post.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Updated by Superuser')
    
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

