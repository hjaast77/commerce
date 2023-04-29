from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Listing, Category, Comment
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import User


class NewListingForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    class Meta:
        model = Listing
        fields = ['title', 'description', 'image_url', 'starting_bid']
        
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
    try:
        com = [Comment.objects.get(listing=auction_id)]
        commentFound = True
    except ObjectDoesNotExist:
        com ="No comments yet!"
        commentFound = False
    return render(request, "auctions/detail.html", {"auction": auction, "comment": com, "commentFound": commentFound})

@login_required(login_url='/login')
def create(request):
    if request.method =="POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            lTitle = form.cleaned_data["title"]
            lDescription = form.cleaned_data["description"]
            lImage_url = form.cleaned_data["image_url"]
            lStarting_bid = form.cleaned_data["starting_bid"]
            seller = request.user

            newListing = Listing(
                title = lTitle,
                description = lDescription,
                image_url = lImage_url,
                starting_bid = float(lStarting_bid),
                seller = seller)

            newListing.save()

            categories = request.POST.getlist("category")
            newListing.category.set(categories)

            return HttpResponseRedirect(reverse("index"))
        
        else:
            
            return render(request, "auctions/create.html", {"form": form})
        
    else:
        return render(request, "auctions/create.html", {"form": NewListingForm()})

