
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("us_posts/<int:item_id>", views.us_posts, name="us_posts"),
    path("us_posts_un/<int:item_id>", views.us_posts_un, name="us_posts_un"),
    path("edit/<int:item_id>", views.edit, name="edit"),
    path("new_post", views.new_post, name="new_post"),
    path("follow", views.follow, name="follow"),
    path("follow_to", views.follow_to, name="follow_to"),
    path("likes", views.likes, name="likes")    
]
