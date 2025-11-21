import graphene
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from blog.models import Blog, Post
from tags.models import Tag

User = get_user_model()


# GraphQL Types
class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')


class BlogType(DjangoObjectType):
    posts = graphene.List(lambda: PostType)
    
    class Meta:
        model = Blog
        fields = '__all__'
    
    def resolve_posts(self, info):
        return self.posts.all()


class TagType(DjangoObjectType):
    class Meta:
        model = Tag
        fields = '__all__'


class PostType(DjangoObjectType):
    class Meta:
        model = Post
        fields = '__all__'


# Queries
class Query(graphene.ObjectType):
    # User queries
    all_users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.Int(), username=graphene.String())
    
    # Blog queries
    all_blogs = graphene.List(BlogType)
    blog = graphene.Field(BlogType, id=graphene.Int())
    blog_by_username = graphene.Field(BlogType, username=graphene.String(required=True))
    
    # Post queries
    all_posts = graphene.List(PostType, published_only=graphene.Boolean())
    post = graphene.Field(PostType, id=graphene.Int(), slug=graphene.String())
    posts_by_blog = graphene.List(PostType, blog_id=graphene.Int())
    
    # Tag queries
    all_tags = graphene.List(TagType)
    tag = graphene.Field(TagType, id=graphene.Int(), name=graphene.String())
    
    def resolve_all_users(self, info):
        return User.objects.all()
    
    def resolve_user(self, info, id=None, username=None):
        if id:
            return User.objects.get(pk=id)
        if username:
            return User.objects.get(username=username)
        return None
    
    def resolve_all_blogs(self, info):
        return Blog.objects.all()
    
    def resolve_blog(self, info, id):
        try:
            return Blog.objects.get(pk=id)
        except Blog.DoesNotExist:
            return None
    
    def resolve_blog_by_username(self, info, username):
        try:
            user = User.objects.get(username=username)
            return Blog.objects.get(user=user)
        except (User.DoesNotExist, Blog.DoesNotExist):
            return None
    
    def resolve_all_posts(self, info, published_only=False):
        if published_only:
            return Post.objects.filter(is_published=True)
        return Post.objects.all()
    
    def resolve_post(self, info, id=None, slug=None):
        if id:
            try:
                return Post.objects.get(pk=id)
            except Post.DoesNotExist:
                return None
        if slug:
            try:
                return Post.objects.get(slug=slug)
            except Post.DoesNotExist:
                return None
        return None
    
    def resolve_posts_by_blog(self, info, blog_id):
        return Post.objects.filter(blog_id=blog_id)
    
    def resolve_all_tags(self, info):
        return Tag.objects.all()
    
    def resolve_tag(self, info, id=None, name=None):
        if id:
            try:
                return Tag.objects.get(pk=id)
            except Tag.DoesNotExist:
                return None
        if name:
            try:
                return Tag.objects.get(name=name)
            except Tag.DoesNotExist:
                return None
        return None


# Mutations
class CreatePost(graphene.Mutation):
    """Mutation para crear un nuevo post"""
    class Arguments:
        blog_id = graphene.Int(required=True)
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        excerpt = graphene.String()
        is_published = graphene.Boolean()
        tag_ids = graphene.List(graphene.Int)
    
    # Lo que devuelve la mutation
    post = graphene.Field(PostType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, blog_id, title, content, excerpt=None, is_published=False, tag_ids=None):
        try:
            blog = Blog.objects.get(pk=blog_id)
            post = Post.objects.create(
                blog=blog,
                title=title,
                content=content,
                excerpt=excerpt or "",
                is_published=is_published
            )
            
            # Agregar tags si se proporcionan
            if tag_ids:
                tags = Tag.objects.filter(id__in=tag_ids)
                post.tags.set(tags)
            
            return CreatePost(
                post=post,
                success=True,
                message="Post creado exitosamente"
            )
        except Blog.DoesNotExist:
            return CreatePost(
                post=None,
                success=False,
                message="Blog no encontrado"
            )
        except Exception as e:
            return CreatePost(
                post=None,
                success=False,
                message=f"Error: {str(e)}"
            )


class UpdatePost(graphene.Mutation):
    """Mutation para actualizar un post existente"""
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()
        excerpt = graphene.String()
        is_published = graphene.Boolean()
        tag_ids = graphene.List(graphene.Int)
    
    post = graphene.Field(PostType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id, title=None, content=None, excerpt=None, is_published=None, tag_ids=None):
        try:
            post = Post.objects.get(pk=id)
            
            if title is not None:
                post.title = title
            if content is not None:
                post.content = content
            if excerpt is not None:
                post.excerpt = excerpt
            if is_published is not None:
                post.is_published = is_published
            
            post.save()
            
            # Actualizar tags si se proporcionan
            if tag_ids is not None:
                tags = Tag.objects.filter(id__in=tag_ids)
                post.tags.set(tags)
            
            return UpdatePost(
                post=post,
                success=True,
                message="Post actualizado exitosamente"
            )
        except Post.DoesNotExist:
            return UpdatePost(
                post=None,
                success=False,
                message="Post no encontrado"
            )
        except Exception as e:
            return UpdatePost(
                post=None,
                success=False,
                message=f"Error: {str(e)}"
            )


class DeletePost(graphene.Mutation):
    """Mutation para eliminar un post"""
    class Arguments:
        id = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, id):
        try:
            post = Post.objects.get(pk=id)
            post.delete()
            return DeletePost(
                success=True,
                message="Post eliminado exitosamente"
            )
        except Post.DoesNotExist:
            return DeletePost(
                success=False,
                message="Post no encontrado"
            )


class CreateTag(graphene.Mutation):
    """Mutation para crear un nuevo tag"""
    class Arguments:
        name = graphene.String(required=True)
    
    tag = graphene.Field(TagType)
    success = graphene.Boolean()
    message = graphene.String()
    
    def mutate(self, info, name):
        try:
            tag = Tag.objects.create(name=name)
            return CreateTag(
                tag=tag,
                success=True,
                message="Tag creado exitosamente"
            )
        except Exception as e:
            return CreateTag(
                tag=None,
                success=False,
                message=f"Error: {str(e)}"
            )


class Mutation(graphene.ObjectType):
    """Todas las mutations disponibles"""
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()
    create_tag = CreateTag.Field()


# Create the schema
schema = graphene.Schema(query=Query, mutation=Mutation)

