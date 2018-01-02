from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

# Create your models here.
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	helper = models.CharField(max_length=4, default='')

from django.dispatch import receiver
from django.db.models.signals import post_save
 
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile_for_new_user(sender, created, instance, **kwargs):
    if created:
        profile = Profile(user=instance)
        profile.save()

class Book(models.Model):
	prim_key = models.CharField(max_length=577, primary_key=True)
	book_name = models.CharField(max_length=512)
	sectioned = models.BooleanField()
	section_name = models.CharField(max_length=20)
	category = models.CharField(max_length=100)
	language = models.CharField(max_length=64)
	collection = models.CharField(max_length=512, default='')
	author = models.CharField(max_length=128, default='')
	order = models.IntegerField(default=0)

class Sentence(models.Model):
	prim_key = models.CharField(max_length=1024, primary_key=True)
	index = models.IntegerField()
	html_id = models.CharField(max_length=20, default='')
	text = models.CharField(max_length=2048)
	paragraph = models.IntegerField()
	section = models.IntegerField(default=0)
	book = models.ForeignKey(Book, default='')

class Book_Instance(models.Model):
	prim_key = models.CharField(max_length=2024, primary_key=True)
	iteration = models.IntegerField(default=0)
	native = models.CharField(max_length=64)
	profile = models.ForeignKey(Profile)
	sentence = models.ForeignKey(Sentence)
	sentence_chapters = ArrayField(models.IntegerField(), default=list)
	completed = models.BooleanField()
	missing_words = ArrayField(models.CharField(max_length=64))
