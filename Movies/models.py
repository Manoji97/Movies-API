from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q


class People(models.Model):
    NameId = models.CharField(max_length=25, unique=True)
    Name = models.CharField(max_length=100)

    class Meta:
        ordering = ["NameId"]

    def __str__(self):
        return self.Name


class Genre(models.Model):
    genre = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.genre


class MovieManager(models.Manager):
    def mainsearch(self, mainsearch):
        queryset = self.get_queryset()
        q_lookup = Q()
        if mainsearch:
            q_lookup = (Q(Title__icontains=mainsearch) | Q(Year__iexact=mainsearch) | Q(Genres__genre__iexact=mainsearch)
                        | Q(Directors__Name__icontains=mainsearch)
                        | Q(Writers__Name__icontains=mainsearch))

        queryset = queryset.filter(q_lookup).distinct()
        return queryset

    def search(self, title=None, rating=None, year=None, genre=None, person=None):
        queryset = self.get_queryset()
        q_lookup = Q()
        if title:
            q_lookup &= Q(Title__icontains=title)
        if rating:
            q_lookup &= Q(Rating__gte=rating)
        if year:
            q_lookup &= Q(Year__iexact=year)
        if genre:
            q_lookup &= Q(Genres__genre__iexact=genre)
        if person:
            q_lookup &= (Q(Directors__Name__icontains=person) &
                         Q(Writers__Name__icontains=person))
        queryset = queryset.filter(q_lookup).distinct()
        return queryset


class Movie(models.Model):
    ImdbId = models.IntegerField(unique=True, blank=True)
    Title = models.CharField(max_length=200)
    Imdb_rating = models.FloatField(null=True, blank=True)
    Image_link = models.CharField(max_length=1000, null=True, blank=True)
    RunTime = models.IntegerField(null=True, blank=True)
    Year = models.CharField(max_length=4, null=True, blank=True)
    Rating = models.FloatField(null=True, blank=True, default=0)
    Num_ratings = models.IntegerField(null=True, blank=True, default=0)
    Genres = models.ManyToManyField(Genre, related_name='Genres')
    Directors = models.ManyToManyField(People, related_name='Directors')
    Writers = models.ManyToManyField(People, related_name='Writers')

    objects = MovieManager()

    class Meta:
        ordering = ["-Year"]

    def __str__(self):
        return self.Title


class NewRating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)])

    class Meta:
        unique_together = (('user', 'movie'),)
        index_together = (('user', 'movie'),)
        ordering = ["id"]

    def __str__(self):
        return self.movie.Title + ' - ' + self.user.username
