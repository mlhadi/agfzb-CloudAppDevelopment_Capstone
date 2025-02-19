from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer, CarModel
from .restapis import get_dealers_from_cf, get_dealer_by_state_from_cf
from .restapis import get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html')


# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return redirect('djangoapp:index')
    else:
        return redirect('djangoapp:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')


# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html')
    elif request.method == 'POST':
        username = request.POST['inputusername']
        password = request.POST['inputpassword']
        first_name = request.POST['inputfirstname']
        last_name = request.POST['inputlastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(
                username=username, first_name=first_name, last_name=last_name,
                password=password
            )
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)


# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://f7400f7f.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealerships'] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


def get_dealerships_by_state(request, state):
    if request.method == "GET":
        url = "https://f7400f7f.us-south.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealer_by_state_from_cf(url, state)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == 'GET':
        context = {}
        url = 'https://f7400f7f.us-south.apigw.appdomain.cloud/api/review'
        reviews = get_dealer_reviews_from_cf(url, dealer_id)

        url = "https://f7400f7f.us-south.apigw.appdomain.cloud/api/dealership"
        dealerships = get_dealers_from_cf(url)
        extracted_dealer = [dealer for dealer in dealerships if dealer.id == dealer_id]

        context['reviews'] = reviews
        context['dealer_id'] = dealer_id
        context['dealer'] = extracted_dealer[0] if len(extracted_dealer) > 0 else None
        dealer_reviews = '\n'. join(f'{review.review} {review.sentiment}' for review in reviews)
        return render(request, 'djangoapp/dealer_details.html', context)


# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'purchasecheck' in request.POST:
                car = CarModel.objects.get(pk=int(request.POST['car']))
                review = {
                    "name": request.user.username,
                    "dealership": dealer_id,
                    "review":  request.POST['content'],
                    "purchase": True if 'purchasecheck' in request.POST else False,
                    "purchase_date": request.POST['purchasedate'],
                    "car_make": car.make.name,
                    "car_model": car.name,
                    "car_year": car.year
                }
            else:
                review = {
                    "name": request.user.username,
                    "dealership": dealer_id,
                    "review":  request.POST['content'],
                    "purchase": False,
                    "purchase_date": None,
                    "car_make": None,
                    "car_model": None,
                    "car_year": None,
                }
            url = 'https://f7400f7f.us-south.apigw.appdomain.cloud/api/review'
            json_payload = dict(review=review)
            post_request(url, json_payload, dealerId=dealer_id)
            return HttpResponseRedirect(reverse('djangoapp:dealerreviews', args=[dealer_id]))
        if request.method == 'GET':
            url = "https://f7400f7f.us-south.apigw.appdomain.cloud/api/dealership"
            dealerships = get_dealers_from_cf(url)
            extracted_dealer = [dealer for dealer in dealerships if dealer.id == dealer_id]
            cars = CarModel.objects.all()
            context = dict(cars=cars, dealer=extracted_dealer)
            return render(request, 'djangoapp/add_review.html', context)
        return redirect('djangoapp:about')
    else:
        return redirect('djangoapp:about')



