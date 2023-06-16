from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User
from .models import Listing
from .models import Bids
from .models import Comments

def index(request):
    return render(request, "auctions/index.html", {
        'listings' : Listing.objects.filter(active=True)
    })


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

class CreateListingForm(forms.Form):
    title = forms.CharField(label="Title")
    description = forms.CharField(label="Describe your item here", widget=forms.Textarea)
    starting_bid = forms.DecimalField(decimal_places=2)
    image = forms.URLField(required=False)
    CATEGORIES = [
        ('',''),
        ('EL','electronics'),
        ('HO', 'home'),
        ('TO', 'toys'),
        ('FA', 'fashion')
    ]
    category = forms.ChoiceField(required=False, choices=CATEGORIES)

def create_listing(request):
    if request.method == "POST":
        form = CreateListingForm(request.POST)
        if form.is_valid():
            l = Listing(title=form.cleaned_data["title"], description=form.cleaned_data["description"], 
                        current_price=form.cleaned_data["starting_bid"], image=form.cleaned_data["image"], 
                        category=form.cleaned_data["category"], active=True, owner=request.user)
            l.save()
            return HttpResponseRedirect(reverse('index'))
    return render(request, "auctions/createListing.html", {
        'form' : CreateListingForm()
    })

class BidForm(forms.Form):
    bid = forms.DecimalField(label='bid', decimal_places=2)

def listing(request, id):
    if request.method == 'POST':
        l = Listing.objects.get(pk=id)
        if 'watchlist' in request.POST:
            l.watched_by.add(request.user)
        elif 'close' in request.POST:
            l.active = False
            l.save()
        else:
            form = BidForm(request.POST)
            if form.is_valid():
                bid = form.cleaned_data['bid']
                if bid > l.current_price:
                    l.current_price = bid
                    l.save()
                    b = Bids(listing=l, user=request.user, bid_amount=bid)
                    b.save()
                #return render(request, "auctions/register.html")
    return render(request, "auctions/listing.html", {
        'form' : BidForm(),
        'listing' : Listing.objects.get(pk=id)
    })

def watchlist(request):
    watchlistList = [l for l in Listing.objects.all() if request.user in l.watched_by.all() and l.active]
    return render(request, "auctions/index.html", {
        'listings' : watchlistList
    })