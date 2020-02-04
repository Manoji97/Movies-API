from django.contrib import admin
from .models import People, Genre, Movie, NewRating



admin.site.register(People)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(NewRating)
