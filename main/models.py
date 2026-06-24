from django.db import models
from django.contrib.auth.models import User
from PIL import Image, ImageOps
import datetime

class Pot(models.Model):
    host = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    pot_name = models.CharField(max_length=100)
    days = models.IntegerField()
    auth_days = models.CharField(max_length=30, default='mon,tue,wed,thu,fri,sat,sun')
    fee = models.IntegerField()
    total_prize = models.IntegerField()
    pot_people = models.IntegerField()
    participants = models.ManyToManyField(User, related_name='join_pots', blank=True)
    pot_code = models.CharField(max_length=6, null=True, blank=True)
    start_date = models.DateField(default=datetime.date.today)
    is_completed = models.BooleanField(default=False)


class Proof(models.Model):
    pot = models.ForeignKey(Pot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='proof_images/')
    auth_date = models.DateField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            image = Image.open(self.image.path)
            image = ImageOps.exif_transpose(image)
            
            max_size = (800, 800) 
            
            image.thumbnail(max_size)
            image.save(self.image.path)


class PotAvatar(models.Model):
    pot = models.ForeignKey(Pot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=20)
    item = models.CharField(max_length=20, null=True, blank=True)
    item_applied_at = models.DateTimeField(null=True, blank=True)

class Vote(models.Model):
    proof = models.ForeignKey(Proof, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField()
