import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


from .models import User, Post, Follow


def index(request):
    posts = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/index.html", {
        "all_posts": page_obj
    })

@csrf_exempt
@login_required
def likes(request):
    if request.method == "POST":
        data = json.loads(request.body)
        post_id = data["post_id"]
        post = Post.objects.get(id=post_id)
        post.numlikes = data["numlikes"]
        like = data["like"]
        if like == "like":
            post.likes.add(request.user)
        else:
            post.likes.remove(request.user)        
        post.save()
        return JsonResponse({}, status=204)

@login_required    
def us_posts(request, item_id):
    user = User.objects.get(id=item_id)
    follow = Follow.objects.filter(owner=user, follower=request.user)
    posts = Post.objects.filter(poster=user).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    f1 = Follow.objects.filter(owner=user).count()
    f2 = Follow.objects.filter(follower=user).count()
    return render(request, "network/us_posts.html", {
        "us_posts": page_obj,
        "follow": follow,
        "owner": user,
        "f1": f1,
        "f2": f2
    })

def us_posts_un(request, item_id):
    user = User.objects.get(id=item_id)
    posts = Post.objects.filter(poster=user).order_by('-timestamp')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    f1 = Follow.objects.filter(owner=user).count()
    f2 = Follow.objects.filter(follower=user).count()
    return render(request, "network/us_posts.html", {
        "us_posts": page_obj,
        "owner": user,
        "f1": f1,
        "f2": f2
    })


@csrf_exempt
@login_required
def new_post(request):
    if request.method == "POST":
        body = request.POST["new_post-body"]
        Post.objects.create(poster=request.user, body=body)
        return render(request, "network/index.html", {
            "all_posts": Post.objects.all().order_by('-timestamp')
        })


@csrf_exempt
@login_required
def edit(request, item_id):
    if request.method == "POST":
        body = request.POST["edit_post-body"]
        post = Post.objects.get(id=item_id)
        post.body = body.strip()
        post.save()        
        return render(request, "network/index.html", {
            "all_posts": Post.objects.all().order_by('-timestamp')
        })
        
    
@csrf_exempt
@login_required
def follow_to(request):
    if request.method == "POST":
        data = json.loads(request.body)
        poster_id = data["poster"]
        poster = User.objects.get(id=poster_id)
        fol = data["fol"]
        if fol == 'follow':
            follow = Follow.objects.create(owner=poster, follower=request.user)
            follow.save()
        else:
            foll = Follow.objects.filter(owner=poster).filter(follower=request.user)
            foll.delete()
        return JsonResponse({}, status=204)
    
    
@login_required
def follow(request):
    own = Follow.objects.filter(follower=request.user)
    posts = Post.objects.all().order_by('-timestamp')
    pt = []
    for post in posts:
        for ow in own:
            if ow.owner == post.poster:
                pt.append(post)
    paginator = Paginator(pt, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, "network/follow.html", {"fol_posts": page_obj})



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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
