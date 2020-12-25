from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("book/<int:item_id>", views.book, name="book"),
    path("city_hotels/<int:item_id>", views.city_hotels, name="city_hotels"),
    path("create", views.create, name="create"),
    path("us_hotels", views.us_hotels, name="us_hotels"),
    path("us_booking", views.us_booking, name="us_booking"),
    path("us_old_booking", views.us_old_booking, name="us_old_booking"),
    path("comment/<int:item_id>", views.comment, name="comment"),
    path("rat/<int:item_id>", views.rat, name="rat"),
    path("comm_us", views.comm_us, name="comm_us"),
    path("all_comm", views.all_comm, name="all_comm"),
    path("del_book/<int:item_id>", views.del_book, name="del_book"),
    path("conf_del_book/<int:item_id>", views.conf_del_book, name="conf_del_book"),
    path("edit_hot/<int:item_id>", views.edit_hot, name="edit_hot")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
