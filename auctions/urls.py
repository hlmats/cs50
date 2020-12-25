from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category", views.category, name="category"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("list_categ/<str:it_item>", views.list_categ, name="list_categ"),
    path("list_thing/<int:item_id>", views.list_thing, name="list_thing"),
    path("addcomm/<int:item_id>", views.addcomm, name="addcomm"),
    path("addwatch/<int:item_id>", views.addwatch, name="addwatch"),
    path("removewatch/<int:item_id>", views.removewatch, name="removewatch"),
    path("addbid/<int:item_id>", views.addbid, name="addbid"),
    path("close/<int:item_id>", views.close, name="close"),
    path("closed_thing/<int:item_id>", views.closed_thing, name="closed_thing"),
]
