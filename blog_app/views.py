from functools import wraps
from urllib.parse import urlparse, parse_qs

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .models import Post, Tag, Folder, Comment, UserProfile
from .forms import PostForm, TagForm, FolderForm, CommentForm


def _redirect_to_post(request, post_id):
    """Redirect al post preservando l'eventuale parametro ?folder=<id>."""
    url = reverse('blog_app:post', kwargs={'post_id': post_id})
    
    # 1. Controlla prima POST o GET espliciti
    folder_id = request.POST.get('folder') or request.GET.get('folder')
    
    # 2. Altrimenti estrai ?folder=... dall'URL di provenienza (HTTP_REFERER)
    if not folder_id:
        referer = request.META.get('HTTP_REFERER', '')
        if referer:
            query_params = parse_qs(urlparse(referer).query)
            folder_list = query_params.get('folder')
            if folder_list:
                folder_id = folder_list[0]

    if folder_id and str(folder_id).isdigit():
        return redirect(f"{url}?folder={folder_id}")
    return redirect(url)


def superuser_required(view_func):
    @wraps(view_func)
    @login_required
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
    """Pagina iniziale: introduzione al progetto, primo post consigliato e ultimi 3 post."""
    first_post = Post.objects.all().order_by('date', 'id').prefetch_related('tags', 'folders').first()
    recent_posts = Post.objects.all().order_by('-date', '-id').prefetch_related('tags')[:3]

    context = {
        'first_post': first_post,
        'recent_posts': recent_posts,
    }
    return render(request, 'blog_app/index.html', context)

def posts(request):
    """List all posts in a flat chronological log."""
    posts = Post.objects.all().order_by('-date').prefetch_related('tags')
    
    context = {
        'posts': posts,
    }
    return render(request, 'blog_app/posts.html', context)


def search_posts(request):
    query = request.GET.get('q', '').strip()
    posts = []

    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)
        ).order_by('-date').prefetch_related('tags').distinct()

    context = {
        'query': query,
        'posts': posts,
    }
    return render(request, 'blog_app/search_results.html', context)

def tags(request):
    """Mostra tutti i tag con il conteggio dei post associati."""
    all_tags = Tag.objects.annotate(post_count=Count('posts')).order_by('name')
    return render(request, 'blog_app/tags.html', {'tags': all_tags})

def tag(request, tag_id):
    """Show all posts containing a specific tag."""
    tag = get_object_or_404(Tag, id=tag_id)
    posts = tag.posts.all().order_by('-date')
    
    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'blog_app/tag.html', context)


# --- FOLDERS CRUD & VIEWS ---

def folders(request):
    """Mostra tutte le folders."""
    all_folders = Folder.objects.all().prefetch_related('posts')
    return render(request, 'blog_app/folders.html', {'folders': all_folders})


def folder(request, folder_id):
    """Mostra tutti i post di una folder in ordine cronologico."""
    folder = get_object_or_404(Folder, id=folder_id)
    posts = folder.posts.all().order_by('date', 'id').prefetch_related('tags')
    return render(request, 'blog_app/folder.html', {'folder': folder, 'posts': posts})


@superuser_required
def new_folder(request):
    if request.method != 'POST':
        form = FolderForm()
    else:
        form = FolderForm(data=request.POST)
        if form.is_valid():
            new_f = form.save()
            return redirect('blog_app:folder', folder_id=new_f.id)

    return render(request, 'blog_app/new_folder.html', {'form': form})


@superuser_required
def edit_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method != 'POST':
        form = FolderForm(instance=folder)
    else:
        form = FolderForm(instance=folder, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('blog_app:folder', folder_id=folder.id)

    return render(request, 'blog_app/edit_folder.html', {'folder': folder, 'form': form})


@superuser_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    if request.method == 'POST':
        folder.delete()
    return redirect('blog_app:folders')


# --- POST DETAIL & INTERACTIONS ---

def post(request, post_id):
    """Individual Post view with optional Folder navigation context."""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    comment_form = CommentForm()
    
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(id=request.user.id).exists()

    # Gestione contesto Folder (?folder=<id>)
    active_folder = None
    prev_post = None
    next_post = None
    post_folders = post.folders.all()

    folder_id = request.GET.get('folder')
    if folder_id and folder_id.isdigit():
        active_folder = post_folders.filter(id=int(folder_id)).first()

    if active_folder:
        folder_posts = list(active_folder.posts.all().order_by('date', 'id'))
        try:
            idx = folder_posts.index(post)
            if idx > 0:
                prev_post = folder_posts[idx - 1]
            if idx < len(folder_posts) - 1:
                next_post = folder_posts[idx + 1]
        except ValueError:
            pass

    other_folders = post_folders.exclude(id=active_folder.id) if active_folder else post_folders

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
        'active_folder': active_folder,
        'prev_post': prev_post,
        'next_post': next_post,
        'other_folders': other_folders,
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

    return _redirect_to_post(request, post.id)


@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
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
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)

    return _redirect_to_post(request, post.id)


# --- POSTS & TAGS CRUD ---

@superuser_required
def new_post(request):
    """Create Post"""
    if request.method != 'POST':
        form = PostForm()
    else:
        form = PostForm(data=request.POST) 

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            return redirect('blog_app:posts')

    context = {'form': form}
    return render(request, 'blog_app/new_post.html', context)


@superuser_required
def edit_post(request, post_id):
    """Edit an existing post."""
    post = get_object_or_404(Post, id=post_id)

    if request.method != 'POST':
        form = PostForm(instance=post)
    else:
        form = PostForm(instance=post, data=request.POST)
        if form.is_valid():
            form.save()
            return _redirect_to_post(request, post.id)

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


# --- USER PROFILE ---

def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    
    comments = Comment.objects.filter(author=profile_user).order_by('-date')
    posts = Post.objects.filter(author=profile_user).order_by('-date') if profile_user.is_superuser else []
    saved_posts = profile.saved_posts.all().order_by('-date')
    
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
        
    return _redirect_to_post(request, post.id)


@login_required
def edit_profile(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        
        profile.bio = bio
        profile.save()
        
        return redirect('blog_app:profile', username=request.user.username)
        
    return render(request, 'blog_app/edit_profile.html', {'profile': profile})
