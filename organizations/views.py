from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator 
from .models import User_Favorites
import requests
import json
import os 
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

ORG_HUNTER_API_KEY = os.environ.get('ORG_HUNTER_API_KEY')

def home(request):
    # Search Handler
    if request.method == 'POST':
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&searchTerm=" + searchTerm)
        data = response.json()
        return render(request, 'organizations/results.j2', {'organizations': data['data']})
    return render(request, 'organizations/home.j2')

def search(request):

    # Get dynamically populated list of categories 
    categoriesList = requests.get("http://data.orghunter.com/v1/categories?user_key=" + ORG_HUNTER_API_KEY)
    categories = categoriesList.json()

    # Search Handler
    if request.method == 'POST':
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        category = request.POST.get('category')
        city = request.POST.get('city')
        city = urlify(city)
        state = request.POST.get('state')

        url = "http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY

        if searchTerm:
            url += "&searchTerm=" + searchTerm

        if category:
            url += "&category=" + category
        
        if city:
            url += "&city=" + city

        if state:
            url += "&state=" + state
        
        response = requests.get(url)
        data = response.json()

        return render(request, 'organizations/results.j2', {'organizations': data['data']})

    return render(request, 'organizations/search.j2', {'categories': categories['data']})


def organization(request, ein):
    url = "http://data.orghunter.com/v1/charitysearch?user_key=a0b3f0195e1ded52ac937673dd45e95a&ein=" + ein

    response = requests.get(url)

    organization = response.json()

    return render(request, 'organizations/organization-page.j2', {'organization': organization['data']})


def about(request):
    return render(request, 'organizations/about.j2', {'title': 'About'})


@login_required
def newFavorite(request, ein):
    try: 
        ukey = ein + request.user.username
        dup_check = User_Favorites.objects.filter(ukey=ukey)
        if dup_check: 
            messages.warning(request, f'Organization already added to favorites')
            return redirect('organizations-organization', ein=ein)
        
        newFavorite = User_Favorites(ukey=ukey, ein=ein, user=request.user.username)
        newFavorite.save()
        messages.success(request, f'Organization Added to Favorites!')
        return redirect('organizations-organization', ein=ein)
    except: 
        messages.warning(request, f'Something went wrong')
        return redirect('organizations-organization', ein=ein)


@login_required
def deleteFavorite(request, ein):
    try: 
        ukey = ein + request.user.username
        User_Favorites.objects.get(ukey=ukey).delete()
        messages.success(request, f'Organization Deleted from Favorites')
        return redirect('organizations-favorites')
    except: 
        messages.warning(request, f'Something went wrong...')
        return redirect('organizations-favorites')


@login_required
def favorites(request):

    favorites = User_Favorites.objects.filter(user=request.user.username)
    favorites_list = []

    for org in range(len(favorites)):
        ein = favorites[org].ein
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&ein=" + ein)
        data = response.json()
        favorites_list.append(data['data'])

    return render(request, 'organizations/favorites.j2', {'favorites': favorites_list})
    

def results(request):
    return render(request, 'organizations/results.j2')


def urlify(url):
    urlLength = len(url)
    return url[:urlLength].replace(' ', '%20')
