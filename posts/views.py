from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group

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
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            Post.objects.create(text=form.cleaned_data['text'], author=request.user,
                                group=Group.objects.get(title=form.cleaned_data['group']))
            return redirect('/')

        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'profile.html',
        {'page': page, 'paginator': paginator, 'author': author}
    )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    posts_count = Post.objects.filter(author=author).count()

    return render(request, 'post.html', {'author': author, 'post': post, 'posts_count': posts_count})


def post_edit(request, username, post_id):
    author = User.objects.get(username=username)

    post = Post.objects.get(pk=post_id)
    if author != request.user:
        return redirect(post)

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post.text = form.cleaned_data['text']
            if post.group:
                post.group = Group.objects.get(title=form.cleaned_data['group'])
            post.save()

            return redirect('/')

        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})
