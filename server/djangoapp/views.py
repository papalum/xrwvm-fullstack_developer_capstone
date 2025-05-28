
 #from django.shortcuts import render
 #from django.http import HttpResponseRedirect, HttpResponse
 #from django.shortcuts import get_object_or_404, render, redirect
 #from django.contrib import messages
 #from datetime import datetime
 
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data['userName']
            password = data['password']
        except (json.JSONDecodeError, KeyError):
            return JsonResponse({"error": "Invalid JSON or missing fields"}, status=400)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

# Create a `logout_request` view to handle sign out request
@csrf_exempt
def logout_user(request):
    username = request.user.username if request.user.is_authenticated else ""
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    # Load JSON data from the request body
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)



# Create a `get_cars` view to return car makes and models
@csrf_exempt
def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if count == 0:
        initiate()  # Ensure the initiate() function is uncommented and implemented in .populate
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })
    return JsonResponse({"CarModels": cars})


# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    # if dealer id has been provided
    if(dealer_id):
        endpoint = "/fetchReviews/dealer/"+str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status":200,"reviews":reviews})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if request.method != "POST":
        return JsonResponse({"status": 405, "message": "Method not allowed"}, status=405)

    if request.user.is_authenticated:
        try:
            data = json.loads(request.body)
            print("Incoming review data:", data)  # DEBUGGING
            response = post_review(data)

            # DEBUGGING: δες τι επιστρέφει η post_review()
            print("Review post response:", response)

            return JsonResponse({"status": 200, "message": "Review submitted successfully."})
        except Exception as e:
            print("Exception during review post:", e)  # DEBUGGING
            return JsonResponse({"status": 500, "message": f"Error in posting review: {str(e)}"}, status=500)
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized. Please log in."}, status=403)
