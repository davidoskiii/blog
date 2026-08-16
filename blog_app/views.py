from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test, login_required
from functools import wraps
from django.http import HttpResponseForbidden, JsonResponse

from .models import Post, Category, Comment
from .forms import PostForm, CategoryForm, CommentForm

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


def index(request):
    "Home Page"
    return render(request, 'blog_app/index.html')


def posts(request):
    """List posts grouped by category (first 5 per category)."""
    categories = Category.objects.all()
    unsorted_posts = Post.objects.filter(category=None)
    
    context = {
        'categories': categories,
        'unsorted_posts': unsorted_posts,
    }
    return render(request, 'blog_app/posts.html', context)

def category(request, category_id):
    """Show all posts belonging to a specific category."""
    category = get_object_or_404(Category, id=category_id)
    posts = category.posts.all()  # Retrieves all posts for this category
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog_app/category.html', context)

def unsorted(request):
    """Show all unsorted posts (posts without a category)."""
    posts = Post.objects.filter(category=None)
    
    context = {
        'posts': posts,
    }
    return render(request, 'blog_app/unsorted.html', context)

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
    "Create Post"

    if request.method != 'POST':
        # No data submitted; create blank form
        form = PostForm()
    else:
        # Data submitted; process data
        form = PostForm(data=request.POST) 

        if form.is_valid():
            form.save()
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
def edit_category(request, category_id):
    """Edit an existing category."""
    category = get_object_or_404(Category, id=category_id)

    if request.method != 'POST':
        # Initial request; pre-fill form with current category data
        form = CategoryForm(instance=category)
    else:
        # POST data submitted; process data
        form = CategoryForm(instance=category, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_app:category', category_id=category.id)

    context = {'category': category, 'form': form}
    return render(request, 'blog_app/edit_category.html', context)

@superuser_required
def delete_category(request, category_id):
    """Delete a category."""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        
    return redirect('blog_app:posts')

@superuser_required
def new_category(request):
    "Create Category"

    if request.method != 'POST':
        # No data submitted; create blank form
        form = CategoryForm()
    else:
        # Data submitted; process data
        form = CategoryForm(data=request.POST)

        if form.is_valid():
            form.save()
            return redirect('blog_app:posts')

    context = {'form': form}
    return render(request, 'blog_app/new_category.html', context)
