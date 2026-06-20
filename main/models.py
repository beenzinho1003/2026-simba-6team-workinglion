from django.db import models
from django.contrib.auth.models import User

class Pot(models.Model):
    host = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    pot_name = models.CharField(max_length=100)
    days = models.IntegerField()
    fee = models.IntegerField()
    total_prize = models.IntegerField()
    pot_people = models.IntegerField()
    participants = models.ManyToManyField(User, related_name='join_pots', blank=True)
    pot_code = models.CharField(max_length=6, null=True, blank=True)


class Proof(models.Model):
    pot = models.ForeignKey(Pot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='proof_images/')
    auth_date = models.DateField(auto_now_add=True)


class PotAvatar(models.Model):
    pot = models.ForeignKey(Pot, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    color = models.CharField(max_length=20)
