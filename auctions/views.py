from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from .models import User, Listing, Comment, Category, Watchlist, Bid, Closebid


def index(request):
    try:
        wt = Watchlist.objects.filter(user=request.user).count()
    except TypeError:
        wt = 1

    ia = []
    ic = Closebid.objects.values_list('listing', flat=True)
    il = Listing.objects.values_list('id', flat=True)
    for i in il:
        if i not in ic:
            ia.append(i)
        
    return render(request, "auctions/index.html", {
#        "listing": Listing.objects.all(),
        "listing": Listing.objects.filter(id__in=ia),
        "nb": wt
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

@login_required
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


def category(request):
    try:
        wt = Watchlist.objects.filter(user=request.user).count()
    except TypeError:
        wt = 1
    return render(request, "auctions/category.html", {
        "category": Category.objects.all(),
        "nb": wt
    })

@login_required
def watchlist(request):
    current_user = request.user

    icw = []
    inw = []
    ic = Closebid.objects.values_list('listing', flat=True)
    il = Watchlist.objects.filter(user=current_user).values_list('listing', flat=True)
    for i in il:
        if i in ic:
            icw.append(i)
            
    Li = Watchlist.objects.filter(user=current_user).filter(listing__in=icw)
    if not Li:
        key = 1
    else:
        key = 0

    for i in il:
        if i not in icw:
            inw.append(i)

    
    return render(request, "auctions/watchlist.html", {
        "watchlist0": Li, "key": key,
        "watchlist": Watchlist.objects.filter(user=current_user).filter(listing__in=inw),
        "nb": Watchlist.objects.filter(user=request.user).count()
    })

def list_thing(request, item_id):
    t1 = Bid.objects.filter(listing=Listing.objects.get(id=item_id))
    t2 = t1.count
    t3 = t1.order_by('bid').last()
    try:
        wt = Watchlist.objects.filter(user=request.user).count()
        w1 = Watchlist.objects.filter(user=request.user).filter(listing=Listing.objects.get(id=item_id))
        if not w1:
            key2=1
        else:
            key2=0
    except TypeError:
        wt = 1
        key2 = 2        
    if not Comment.objects.filter(listing=Listing.objects.get(id=item_id)):
        key1 = 0
    else:
        key1 = 1
    current_user = request.user
    owner = Listing.objects.get(id=item_id).owner
    if owner == current_user.username:
        key3 = 0
    else:
        key3 = 1    
    return render(request, "auctions/list_thing.html", {
        "item": Listing.objects.get(id=item_id),
        "comment": Comment.objects.filter(listing=Listing.objects.get(id=item_id)),
        "num": t2, "maxbid": t3, "key1": key1, "key2": key2, "key3": key3,
        "nb": wt
    })

def list_categ(request, it_item):
    try:
        wt = Watchlist.objects.filter(user=request.user).count()
    except TypeError:
        wt = 1

    ia = []
    ic = Closebid.objects.values_list('listing', flat=True)
    il = Listing.objects.values_list('id', flat=True)
    for i in il:
        if i not in ic:
            ia.append(i)

    Li = Listing.objects.filter(category=it_item).filter(id__in=ia)
    if not Li:
        key = 1
    else:
        key = 0
        
    return render(request, "auctions/list_categ.html", {
        "listing": Li,
        "name": it_item.title(),
        "nb": wt, "key": key
    })

@login_required
def create(request):
    if request.method == "POST":
        title = request.POST["title"]
        if not title:
            return HttpResponseBadRequest("Bad Request: You should add title")
        description = request.POST["description"]
        image = request.POST["image"]
        category = request.POST["category"]
        if not category:
            return HttpResponseBadRequest("Bad Request: You should add category")
        starting_price = request.POST["starting_price"]
        if not starting_price:
            return HttpResponseBadRequest("Bad Request: You should add starting_price")
        current_user = request.user
        Listing.objects.create(title=title, description=description, image=image, category=category, starting_price=int(starting_price), owner=current_user.username)
        cat = Category.objects.filter(item=category)
        if not cat:
            Category.objects.create(item=category)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "nb": Watchlist.objects.filter(user=request.user).count()
            })

@login_required
def addcomm(request, item_id):
    if request.method == "POST":
        current_user = request.user
        comment = request.POST["comment"]        
        if not comment:
            return HttpResponseBadRequest("Bad Request: You should add comment")             
        else:
            Comment.objects.create(user=current_user, listing=Listing.objects.get(id=item_id), text=comment)
            return HttpResponseRedirect(reverse("list_thing", args=(item_id,)))

@login_required
def addwatch(request, item_id):
    if request.method == "POST":
        current_user = request.user        
        Watchlist.objects.create(user=current_user, listing=Listing.objects.get(id=item_id))
        return HttpResponseRedirect(reverse("list_thing", args=(item_id,)))

@login_required
def addbid(request, item_id):
    if request.method == "POST":
        current_user = request.user
        bid = int(request.POST["addbid"])
        price = Listing.objects.get(id=item_id).starting_price
        b1 = Bid.objects.filter(listing=Listing.objects.get(id=item_id))
        if not b1:
            if bid >= price:
                Bid.objects.create(user=current_user, listing=Listing.objects.get(id=item_id), bid=bid)
                return HttpResponseRedirect(reverse("list_thing", args=(item_id,)))
            else:
                return HttpResponseBadRequest("Bad Request: Your bid should be greater or equal than Price and greater than Max Bid.")
        else:
            b2 = b1.order_by('bid').last()
            maxbid=b2.bid
            if bid > maxbid:
                Bid.objects.create(user=current_user, listing=Listing.objects.get(id=item_id), bid=bid)
                return HttpResponseRedirect(reverse("list_thing", args=(item_id,)))
            else:
                return HttpResponseBadRequest("Bad Request: Your bid should be greater or equal than Price and greater than Max Bid.")



@login_required
def removewatch(request, item_id):
    if request.method == "POST":
        current_user = request.user
        Watchlist.objects.get(user=current_user, listing=Listing.objects.get(id=item_id)).delete()
        return HttpResponseRedirect(reverse("list_thing", args=(item_id,)))

@login_required
def close(request, item_id):
    current_user = request.user
    b1 = Bid.objects.filter(listing=Listing.objects.get(id=item_id))
    if not b1:
        Closebid.objects.create(owner=current_user, winner=current_user, listing=Listing.objects.get(id=item_id), bid=0)
        key = 1
        return render(request, "auctions/closed_thing.html", {
            "item": Listing.objects.get(id=item_id),
            "clobj": Closebid.objects.get(listing=Listing.objects.get(id=item_id)),
            "nb": Watchlist.objects.filter(user=request.user).count(), "key": key,
            })
    else:
        b2 = b1.order_by('bid').last()
        Closebid.objects.create(owner=current_user, winner=b2.user, listing=Listing.objects.get(id=item_id), bid=b2.bid)
        key = 3
        return render(request, "auctions/closed_thing.html", {
            "item": Listing.objects.get(id=item_id),
            "clobj": Closebid.objects.get(listing=Listing.objects.get(id=item_id)), "key": key,
            "nb": Watchlist.objects.filter(user=request.user).count()
            })

@login_required
def closed_thing(request, item_id):
    b1 = Bid.objects.filter(listing=Listing.objects.get(id=item_id))
    if not b1:
        key = 1
        return render(request, "auctions/closed_thing.html", {
            "item": Listing.objects.get(id=item_id),
            "clobj": Closebid.objects.get(listing=Listing.objects.get(id=item_id)),
            "nb": Watchlist.objects.filter(user=request.user).count(), "key": key,
            })
    else:
        b2 = b1.order_by('bid').last()
        if Closebid.objects.get(listing=Listing.objects.get(id=item_id)).winner == request.user:
            key = 2
        else:
            key = 3
        return render(request, "auctions/closed_thing.html", {
            "item": Listing.objects.get(id=item_id),
            "clobj": Closebid.objects.get(listing=Listing.objects.get(id=item_id)), "key": key,
            "nb": Watchlist.objects.filter(user=request.user).count()
            })





    

    
