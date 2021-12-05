from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group


def index(request):
    latest = Post.objects.order_by("-pub_date")[:11]
    return render(request, "index.html", {"posts": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:12]
    return render(request, 'group.html', {'group': group, 'posts': posts})


def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            print(form.cleaned_data)
            Post.objects.create(text=form.cleaned_data['text'], author=request.user,
                                group=Group.objects.get(title=form.cleaned_data['group']))
            return redirect('/')

        return render(request, 'new_post.html', {'form': form})

    form = PostForm()
    return render(request, 'new_post.html', {'form': form})
