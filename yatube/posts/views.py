from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .models import Post, Group, User
from django.contrib.auth.decorators import login_required
from .utils import page_content


def index(request):
    posts = Post.objects.all()
    context = page_content(posts, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    context = {
        'group': group,
        'posts': posts,
    }
    context.update(page_content(posts, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    context = {
        'author': author,
    }
    context.update(page_content(posts, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form_object = form.save(commit=False)
            form_object.author = request.user
            form_object.save()
            return redirect('posts:profile', request.user.username)
        return render(request, 'posts/create.html', {'form': form})
    return render(request, 'posts/create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    form = PostForm(request.POST or None, instance=post)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if form.is_valid():
        form_object = form.save(commit=False)
        form_object.author = request.user
        form_object.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create.html', {
        'form': form,
        'is_edit': is_edit,
    })
