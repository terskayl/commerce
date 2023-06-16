from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=500)
    current_price = models.DecimalField(decimal_places=2, max_digits=16)
    image = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    active = models.BooleanField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    watched_by = models.ManyToManyField(User, blank=True, related_name="watchlist")

    def __str__(self):
        return f"{self.title}: listing num {self.id}, at {self.current_price}, {self.category}"


class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    bid_amount = models.DecimalField(decimal_places=2, max_digits=16)

    def __str__(self):
        return f"{self.user.username} bid ${self.bid_amount} on {self.listing.title}"    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.user.username} commented ${self.text} on {self.listing.title}"  
