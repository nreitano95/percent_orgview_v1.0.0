from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from .models import Favorites2
import requests
from django.contrib import messages
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator 

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
        
        response = requests.get(url)

        data = response.json()


        # images = []
        # for org in range(0,len(data['data'])):
        #     charityName = data['data'][org].get('charityName')
        #     imageURL = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

        #     querystring = {"q":charityName,"pageNumber":"1","pageSize":"1","autoCorrect":"true"}

        #     headers = {
        #         'x-rapidapi-key': "fc64577d49msh1e5935a829664a3p122e80jsn6f36a130b92e",
        #         'x-rapidapi-host': "contextualwebsearch-websearch-v1.p.rapidapi.com"
        #         }

        #     imageResponse = requests.request("GET", imageURL, headers=headers, params=querystring)

        #     print(imageResponse.text)



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
        print(ukey)
        newFavorite = Favorites2(ukey=ukey, ein=ein, user=request.user.username)
        newFavorite.save()
        messages.success(request, f'Organization Added to Favorites!')
        return redirect('organizations-organization', ein=ein)
    except: 
        messages.warning(request, f'Organization already added to favorites')
        return redirect('organizations-organization', ein=ein)


@login_required
def deleteFavorite(request, ein):
    try: 
        ukey = ein + request.user.username
        Favorites2.objects.get(ukey=ukey).delete()


        messages.success(request, f'Organization Deleted from Favorites')
        return redirect('organizations-favorites')
    except: 
        messages.warning(request, f'Something went wrong...')
        return redirect('organizations-favorites')




@login_required
def favorites(request):

    favorites = Favorites2.objects.filter(user=request.user.username)
    # favorites_list = []

    # for org in range(0,len(favorites)):
    #     ein = favorites[org].ein
    #     response = requests.get("http://data.orghunter.com/v1/charitysearch?user_key=" + apikey + "&ein=" + ein)

    #     data = response.json()
    #     favorites_list.append(data['data'])
    #     print(favorites_list)
    #     return render(request, 'organizations/favorites.j2', {'favorites': favorites_list})
    
    return render(request, 'organizations/favorites.j2', {'favorites': favorites})

def results(request):

    return render(request, 'organizations/results.j2')

def urlify(url):
    urlLength = len(url)
    return url[:urlLength].replace(' ', '%20')
