from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    image = models.ImageField(upload_to='static/auctions/', blank=True, height_field=None, width_field=None, max_length=100)
    category = models.CharField(max_length=64)
    starting_price = models.IntegerField()
    owner = models.CharField(max_length=64)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} {self.description} {self.category} {self.starting_price} {self.owner}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} {self.listing} {self.text}"

class Category(models.Model):
    item = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.item}"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user} {self.listing}"

    
class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")
    bid = models.IntegerField()

    def __str__(self):
        return f"{self.user} {self.listing} {self.bid}"


class Closebid(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="own")
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="win")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="list")
    bid = models.IntegerField()

    def __str__(self):
        return f"{self.owner} {self.winner} {self.listing} {self.bid}"














    
