from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Listing, Category, Comment, Bid, Watchlist
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .models import User




class NewListingForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    starting_bid = forms.DecimalField(max_digits=10, decimal_places=2)
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
    comments = Comment.objects.filter(listing=auction)
    commentFound = comments.exists()
    error = None  # Variable for storing error message

    if request.method == 'POST':
        bid_amount = request.POST.get('bid_amount')
        try:
            bid_amount = float(bid_amount)
        except ValueError:
            # handle error if bid amount is not a valid number
            
            pass
        else:
            if bid_amount > auction.starting_bid and (not auction.bids.exists() or bid_amount > auction.bids.last().amount):
                # bid is valid. can store it
                new_bid = Bid(amount=bid_amount, bidder=request.user, listing=auction)
                new_bid.save()
                return redirect('auctions', auction_id=auction.id)
            else:
                
                if bid_amount <= auction.starting_bid:
                    error = "Bid must be higher than starting price."
                elif auction.bids.exists() and bid_amount <= auction.bids.last().amount:
                    error = "Bid must be higher than highest bid."
                else:
                    error = "Invalid Bid format!."
                
    
    return render(request, "auctions/detail.html", {"auction": auction, "comments": comments, "commentFound": commentFound, "error": error, "user": request.user,})

@login_required(login_url='/login')
def create(request):
    if request.method =="POST":
        form = NewListingForm(request.POST)
        if form.is_valid():

            new_listing = form.save(commit=False)
            new_listing.starting_bid = form.cleaned_data["starting_bid"]
            new_listing.seller = request.user

            new_listing.title = form.cleaned_data["title"]  # Guardar el título
            new_listing.description = form.cleaned_data["description"]  # Guardar la descripción
            new_listing.image_url = form.cleaned_data["image_url"]  # Guardar la URL de la imagen

            new_listing.save()
            form.save_m2m()
        
        else:
            
            #return render(request, "auctions/create.html", {"form": form})
            form = NewListingForm()
        
    
    return render(request, "auctions/create.html", {"form": form})
    
def add_comment(request, auction_id):
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            auction = Listing.objects.get(id=auction_id)
            new_comment = Comment(text=comment_text, author=request.user, listing=auction)
            new_comment.save()

    return redirect('auctions', auction_id=auction_id)

@login_required(login_url='/login')
def add_watchlist(request, auction_id):
    auction = Listing.objects.get(id=auction_id)
    user = request.user

    try:
        watchlist = Watchlist.objects.get(user=user)
    except Watchlist.DoesNotExist:
        watchlist = Watchlist.objects.create(user=user)

    watchlist.listings.add(auction)
    watchlist.save()
    return HttpResponseRedirect(reverse("auctions", args=(auction_id,)))

@login_required(login_url='/login')
def remove_watchlist(request, auction_id):
    auction = Listing.objects.get(id=auction_id)
    user = request.user

    try:
        watchlist = Watchlist.objects.get(user=user)
    except Watchlist.DoesNotExist:
        watchlist = Watchlist.objects.create(user=user)

    watchlist.listings.remove(auction)
    return HttpResponseRedirect(reverse("auctions", args=(auction_id,)))

@login_required(login_url='/login')
def watchlist(request):
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist})

@login_required(login_url='/login')
def change_active_status(request, auction_id):
    auction = Listing.objects.get(id=auction_id)
    if request.method == 'POST':
        if request.user == auction.seller:
            auction.active = False
            auction.save()
            return redirect('auctions', auction_id=auction_id)
        else:
            return HttpResponse("You are not allowed to change the active status of this auction.")
    else:
        return HttpResponse("Method not allowed.")
    
@login_required(login_url='/login')
def categories(request):
    categories = Category.objects.all()
    return render(request, "auctions/categories.html", {"categories": categories})