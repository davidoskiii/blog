from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver

class Tag(models.Model):
    """A Tag for filtering posts."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Post(models.Model):
    """A Post created by a Superuser."""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
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


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    saved_posts = models.ManyToManyField('Post', related_name='saved_by', blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"

# Signal: Automatically create a UserProfile whenever a User is created
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.profile.save()
