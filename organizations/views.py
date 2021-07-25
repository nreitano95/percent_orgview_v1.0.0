from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from .models import Post
import requests

apikey = "a0b3f0195e1ded52ac937673dd45e95a"

def home(request):
    # Search Handler
    if request.method == 'POST':
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + apikey + "&searchTerm=" + searchTerm)

        data = response.json()
        return render(request, 'organizations/results.j2', {'organizations': data['data']})
    return render(request, 'organizations/home.j2')

def search(request):

    categoriesList = requests.get("http://data.orghunter.com/v1/categories?user_key=" + apikey)
    categories = categoriesList.json()

    # Search Handler
    if request.method == 'POST':
        
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        category = request.POST.get('category')
        city = request.POST.get('city')
        city = urlify(city)
        state = request.POST.get('state')

        url = "http://data.orghunter.com/v1/charitysearch?user_key=" + apikey

        if searchTerm:
            url += "&searchTerm=" + searchTerm

        if category:
            url += "&category=" + category
        
        if city:
            url += "&city=" + city

        if state:
            url += "&state=" + state
        
        print(url)
        response = requests.get(url)

        data = response.json()
        return render(request, 'organizations/results.j2', {'organizations': data['data']})

    return render(request, 'organizations/search.j2', {'categories': categories['data']})



def organization(request, ein):
    url = "http://data.orghunter.com/v1/charitysearch?user_key=a0b3f0195e1ded52ac937673dd45e95a&ein=" + ein

    response = requests.get(url)

    organization = response.json()

    return render(request, 'organizations/organization-page.j2', {'organization': organization['data']})

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

def favorites(request):
    return render(request, 'organizations/favorites.j2', {'title': 'Favorites'})

def results(request):
    return render(request, 'organizations/results.j2')

def urlify(url):
    urlLength = len(url)
    return url[:urlLength].replace(' ', '%20')
