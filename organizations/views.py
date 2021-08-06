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

# Store API Key in environment variable
ORG_HUNTER_API_KEY = os.environ.get('ORG_HUNTER_API_KEY')

def home(request):
    """ Renders the Home page including a keyword search bar """ 

    # Search Handler
    if request.method == 'POST':
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&searchTerm=" + searchTerm)
        data = response.json()
        return render(request, 'organizations/results.j2', {'organizations': data['data']})
    return render(request, 'organizations/home.j2')

def search(request):
    """ Makes an API call to OrgHunter given the provided user input data """

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

        # Include the search term in the API Request
        if searchTerm:
            url += "&searchTerm=" + searchTerm

        # Include the category in the API Request
        if category:
            url += "&category=" + category

        # Include the city in the API Request
        if city:
            url += "&city=" + city

        # Include the state in the API Request
        if state:
            url += "&state=" + state
        
        response = requests.get(url)
        data = response.json()

        return render(request, 'organizations/results.j2', {'organizations': data['data']})

    return render(request, 'organizations/search.j2', {'categories': categories['data']})


def organization(request, ein):
    """ Makes an API call to OrgHunter given a tax id and renders the given organization page """ 

    # Generate API request given user API key and the given tax id
    url = "http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&ein=" + ein

    response = requests.get(url)

    organization = response.json()

    # Search Handler
    if request.method == 'POST':
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&searchTerm=" + searchTerm)
        data = response.json()
        return render(request, 'organizations/results.j2', {'organizations': data['data']})

    return render(request, 'organizations/organization-page.j2', {'organization': organization['data']})


def about(request):
    """ Renders the About page """
    return render(request, 'organizations/about.j2', {'title': 'About'})


@login_required
def newFavorite(request, ein):
    """ Creates a new row in the database for a given user and organization tax id to
        save a user's favorite organization """

    # Save a favorite organization based on the tax id only if not a duplicate
    try: 
        # Create a unique key by combining the tax number with the username 
        ukey = ein + request.user.username

        # Check for duplicates
        dup_check = User_Favorites.objects.filter(ukey=ukey)
        if dup_check: 
            # Print message if ukey already exists
            messages.warning(request, f'Organization already added to favorites')
            return redirect('organizations-organization', ein=ein)
        
        # Save to database and print message
        newFavorite = User_Favorites(ukey=ukey, ein=ein, user=request.user.username)
        newFavorite.save()
        messages.success(request, f'Organization Added to Favorites!')
        return redirect('organizations-organization', ein=ein)
    except: 
        messages.warning(request, f'Something went wrong')
        return redirect('organizations-organization', ein=ein)


@login_required
def deleteFavorite(request, ein):
    """ Takes a tax id and deletes the row in the database given the user and tax id """
    # Delete favorite from database if ukey is found.
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
    """ Calls for the database to get all of the user's favorite organizations and 
        renders the favorites template with the data from the favorites list """

    # Get all of the tax ids of the favorite organizations for a particular user 
    favorites = User_Favorites.objects.filter(user=request.user.username)
    
    # Initialize a favorites list to be used to display the user's favorite organizations
    favorites_list = []

    # Make API calls to OrgHunter with each of the favorite organization's tax numbers
    for org in range(len(favorites)):
        ein = favorites[org].ein
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&ein=" + ein)
        data = response.json()
        # Store the json data in the favorites_list
        favorites_list.append(data['data'])

    return render(request, 'organizations/favorites.j2', {'favorites': favorites_list})
    

def results(request):
    """ Renders the results template """

    # Search Handler
    if request.method == 'POST':
        searchTerm = request.POST.get('searchTerm')
        searchTerm = urlify(searchTerm)
        response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + ORG_HUNTER_API_KEY + "&searchTerm=" + searchTerm)
        data = response.json()
        return render(request, 'organizations/results.j2', {'organizations': data['data']})

    return render(request, 'organizations/results.j2')


def urlify(url):
    """ Returns a properly-formatted URL string given an initial url string """ 
    if url is None:
        return
    urlLength = len(url)
    return url[:urlLength].replace(' ', '%20')
