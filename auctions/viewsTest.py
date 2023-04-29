from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Listing, Category

from .models import User

def index(request):

    return render(request, "auctions/index.html", {"listings": Listing.objects.exclude(active=False)})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def auctions(request, auction_id):
    auction = Listing.objects.get(id=auction_id)
    return render(request, "auctions/detail.html", {"auction": auction})

def create(request):
    if request.method =="POST":
        title = request.POST["title"]
        description = request.POST["description"]
        image_url = request.POST["image_url"]
        starting_bid = request.POST["starting_bid"]
        seller = request.user

        newListing = Listing(
            title = title,
            description = description,
            image_url = image_url,
            starting_bid = float(starting_bid),
            seller = seller)

        newListing.save()

        categories = request.POST.getlist("category[]")
        for category_name in categories:
            category = Category.objects.get(name=category_name)
            newListing.category.add(category)

        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {"category": Category.objects.all()})
    
