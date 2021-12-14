from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'group.html',
                  {'group': group, 'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():
        return render(request, 'new_post.html', {'form': form})
    post_new = form.save(commit=False)
    post_new.author = request.user
    post_new.save()
    return redirect('post', username=request.user.username, post_id=post_new.id)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    following = False
    if Follow.objects.filter(user=request.user, author=author).count():
        following = True

    return render(
        request,
        'profile.html',
        {'page': page, 'paginator': paginator, 'author': author, 'following': following}
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    posts_count = Post.objects.filter(author=author).count()
    comments = post.comments.all()
    form = CommentForm()
    return render(request, 'post.html',
                  {'author': author, 'post': post, 'posts_count': posts_count, 'form': form, 'comments': comments, })


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    if post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None, request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('post', username=username, post_id=post_id)
    return render(request, 'new_post.html', {'form': form,
                                             'post': post})


@login_required
def add_comment(request, username, post_id):
    post = Post.objects.get(id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username=username, post_id=post_id)


@login_required
def follow_index(request):
    following = Follow.objects.filter(user=request.user).values_list('author', flat=True)
    print(following)
    post_list = Post.objects.filter(author_id__in=following).order_by('-pub_date')
    paginator = Paginator(post_list, 10)

    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'follow.html', {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if not Follow.objects.filter(user=request.user).count():
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
