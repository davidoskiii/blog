from django.urls import path
from . import views

app_name = 'blog_app'
urlpatterns = [
    # Home Page
    path('', views.posts, name='index'),

    # Posts
    path('posts/', views.posts, name='posts'),
    path('posts/<int:post_id>/', views.post, name='post'),
    path('new_post/', views.new_post, name='new_post'),
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    path('search/', views.search_posts, name='search'),

    # Likes & Comments
    path('posts/<int:post_id>/like/', views.like_post, name='like_post'),
    path('posts/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),

    # Tags (Formerly Categories)
    path('new_tag/', views.new_tag, name='new_tag'),
    path('tag/<int:tag_id>/', views.tag, name='tag'),
    path('edit_tag/<int:tag_id>/', views.edit_tag, name='edit_tag'),
    path('delete_tag/<int:tag_id>/', views.delete_tag, name='delete_tag'),

    # Profile
    path('profile/<str:username>/', views.user_profile, name='profile'),
    path('profile/edit/settings/', views.edit_profile, name='edit_profile'),
    path('post/<int:post_id>/save/', views.toggle_save_post, name='toggle_save_post'),
]
