from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    """A Tag for filtering posts."""
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    """A Post created by a Superuser."""
    title = models.CharField(max_length=200)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    
    # Switched from ForeignKey(Category) to ManyToManyField(Tag)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        verbose_name_plural = 'posts'

    def __str__(self):
        return f"{self.title} - {self.text[:50]}..."

    def total_likes(self):
        return self.likes.count()


class Comment(models.Model):
    """A Comment on a Post by any authenticated user."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
