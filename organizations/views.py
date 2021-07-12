from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from .models import Post


def home(request):

    return render(request, 'organizations/home.j2', )


class PostListView(ListView):
    model = Post
    template_name = 'organizations/home.j2'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView):
    model = Post
    template_name = 'organizations/user_posts.j2'
    context_object_name = 'posts'
    paginate_by = 6

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    template_name = 'organizations/post_detail.j2'
    

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'organizations/post_form.j2'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    template_name = 'organizations/post_form.j2'
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author: 
            return True
        return False


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'organizations/post_confirm_delete.j2'
    success_url = '/'

    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author: 
            return True
        return False

def about(request):
    return render(request, 'organizations/about.j2', {'title': 'About'})


