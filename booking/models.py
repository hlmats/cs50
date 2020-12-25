from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass

class Hotels(models.Model):
    city = models.CharField(max_length=255)
    hot_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    owner = models.ForeignKey("User", on_delete=models.CASCADE, related_name="own")
    free_place = models.IntegerField()
    price = models.IntegerField()
    rating = models.DecimalField(default=0.0, max_digits=3, decimal_places=1)
    photo = models.ImageField(upload_to='booking/', blank=True, height_field=None, width_field=None, max_length=100)

    
    
class Reservations(models.Model):
    res_hotel = models.ForeignKey("Hotels", on_delete=models.CASCADE, related_name="hotres")
    res_date_in = models.DateField()
    res_date_out = models.DateField()
    numb_days = models.IntegerField()
    guest = models.ForeignKey("User", on_delete=models.CASCADE, related_name="gst")
    is_rating = models.BooleanField(default=False)
    us_rat = models.IntegerField(default=0)


class Comments(models.Model):
    com_hotel = models.ForeignKey("Hotels", on_delete=models.CASCADE, related_name="hotcom")
    com_us = models.ForeignKey("User", on_delete=models.CASCADE, related_name="uscom")
    timestamp = models.DateTimeField(auto_now_add=True)
    liv_date_in = models.DateField()
    liv_date_out = models.DateField()
    com_text = models.TextField(blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "com_us": self.com_us.username,
            "timestamp": self.timestamp,
            "liv_date_in": self.liv_date_in,
            "liv_date_out": self.liv_date_out,
            "com_text": self.com_text
        }
