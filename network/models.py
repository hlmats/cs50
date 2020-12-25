from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="post")
    body = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name="like")
    numlikes = models.IntegerField(default=0)
   


class Follow(models.Model):
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="owner")
    follower = models.ForeignKey("User", on_delete=models.CASCADE, related_name="follower")



