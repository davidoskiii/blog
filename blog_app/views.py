from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse

from .models import Post, Tag, Comment, UserProfile
from .forms import PostForm, TagForm, CommentForm

def superuser_required(view_func):
    @wraps(view_func)
    @login_required  # Redirects unauthenticated users to login
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            context = {
                'error_title': 'Accesso Negato',
                'error_message': 'Non disponi dei permessi da Superuser necessari per creare, modificare o eliminare contenuti.'
            }
            return render(request, 'blog_app/403.html', context, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def posts(request):
    """List all posts in a flat chronological log."""
    # Fetches all posts, newest first, and grabs their tags in one query
    posts = Post.objects.all().order_by('-date').prefetch_related('tags')
    
    context = {
        'posts': posts,
    }
    return render(request, 'blog_app/posts.html', context)

def search_posts(request):
    query = request.GET.get('q', '').strip()
    posts = []

    if query:
        # Search posts where title or text contains the query, and prefetch tags
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        ).order_by('-date').prefetch_related('tags').distinct()

    context = {
        'query': query,
        'posts': posts,
    }
    return render(request, 'blog_app/search_results.html', context)

def tag(request, tag_id):
    """Show all posts containing a specific tag."""
    tag = get_object_or_404(Tag, id=tag_id)
    posts = tag.posts.all()
    
    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'blog_app/tag.html', context)

def post(request, post_id):
    """Individual Post view open to everyone."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    
    # Check if the current user has already liked this post
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
    }
    return render(request, 'blog_app/post.html', context)


@login_required
def add_comment(request, post_id):
    """Add a new comment to a post (requires login)."""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

    return redirect('blog_app:post', post_id=post.id)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Verifica che l'utente sia l'autore
    if comment.author != request.user:
        return JsonResponse({'status': 'error', 'message': 'Non autorizzato'}, status=403)
        
    if request.method == 'POST':
        new_text = request.POST.get('text', '').strip()
        if new_text:
            comment.text = new_text
            comment.save()
            return JsonResponse({'status': 'ok', 'text': comment.text})
        return JsonResponse({'status': 'error', 'message': 'Il testo non può essere vuoto'}, status=400)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Verifica che l'utente sia l'autore
    if comment.author != request.user:
        return JsonResponse({'status': 'error', 'message': 'Non autorizzato'}, status=403)
        
    if request.method == 'POST':
        comment.delete()
        return JsonResponse({'status': 'ok'})


@login_required
def like_post(request, post_id):
    """Toggle like/unlike on a post (requires login)."""
    post = get_object_or_404(Post, id=post_id)

    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)  # Unlike
    else:
        post.likes.add(request.user)     # Like

    return redirect('blog_app:post', post_id=post.id)

@superuser_required
def new_post(request):
    """Create Post"""

    if request.method != 'POST':
        # No data submitted; create blank form
        form = PostForm()
    else:
        # Data submitted; process data
        form = PostForm(data=request.POST) 

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # Saves ManyToMany fields like tags
            return redirect('blog_app:posts')

    context = {'form': form}
    return render(request, 'blog_app/new_post.html', context)

@superuser_required
def edit_post(request, post_id):
    """Edit an existing post."""
    post = get_object_or_404(Post, id=post_id)

    if request.method != 'POST':
        # Initial request; pre-fill form with the current post data
        form = PostForm(instance=post)
    else:
        # POST data submitted; process data
        form = PostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_app:post', post_id=post.id)

    context = {'post': post, 'form': form}
    return render(request, 'blog_app/edit_post.html', context)

@superuser_required
def delete_post(request, post_id):
    """Delete a post."""
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        post.delete()
        
    return redirect('blog_app:posts')

@superuser_required
def edit_tag(request, tag_id):
    """Edit an existing tag."""
    tag = get_object_or_404(Tag, id=tag_id)

    if request.method != 'POST':
        form = TagForm(instance=tag)
    else:
        form = TagForm(instance=tag, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_app:tag', tag_id=tag.id)

    context = {'tag': tag, 'form': form}
    return render(request, 'blog_app/edit_tag.html', context)

@superuser_required
def delete_tag(request, tag_id):
    """Delete a tag."""
    tag = get_object_or_404(Tag, id=tag_id)
    
    if request.method == 'POST':
        tag.delete()
        
    return redirect('blog_app:posts')

@superuser_required
def new_tag(request):
    """Create Tag"""
    if request.method != 'POST':
        form = TagForm()
    else:
        form = TagForm(data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_app:posts')

    context = {'form': form}
    return render(request, 'blog_app/new_tag.html', context)

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # Safety fallback for existing users created before the signal was added
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    
    # Fetch user's comments
    comments = Comment.objects.filter(author=profile_user).order_by('-date')
    
    # Fetch posts authored by this user if they are a superuser
    posts = Post.objects.filter(author=profile_user).order_by('-date') if profile_user.is_superuser else []
    
    # Fetch saved posts
    saved_posts = profile.saved_posts.all().order_by('-date')
    
    # Check if currently logged-in user has saved this profile's post list (if visiting own profile)
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'comments': comments,
        'posts': posts,
        'saved_posts': saved_posts,
    }
    return render(request, 'blog_app/profile.html', context)


@login_required
def toggle_save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if profile.saved_posts.filter(id=post.id).exists():
        profile.saved_posts.remove(post)
    else:
        profile.saved_posts.add(post)
        
    return redirect(request.META.get('HTTP_REFERER', 'blog_app:posts'))


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        # Save user details
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        
        # Save profile details
        profile.bio = bio
        profile.save()
        
        return redirect('blog_app:profile', username=request.user.username)
        
    return render(request, 'blog_app/edit_profile.html', {'profile': profile})
