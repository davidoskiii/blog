from django.urls import path
from . import views

app_name = 'blog_app'
urlpatterns = [
    # Home Page
    path('', views.index, name='index'),

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

    # Categories
    path('new_category/', views.new_category, name='new_category'),
    path('categories/unsorted/', views.unsorted, name='unsorted'),
    path('categories/<int:category_id>/', views.category, name='category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete_category/<int:category_id>/', views.delete_category, name='delete_category'),
]
