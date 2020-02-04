from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class People(models.Model):
	NameId = models.CharField(max_length = 25, unique = True)
	Name = models.CharField(max_length = 100)

	def __str__(self):
		return self.Name


class Genre(models.Model):
	genre = models.CharField(max_length = 100, unique = True)

	def __str__(self):
		return self.genre

class Movie(models.Model):
	ImdbId = models.IntegerField(unique = True, blank = True)
	Title = models.CharField(max_length = 200)
	Imdb_rating = models.FloatField(null = True, blank = True)
	Image_link = models.CharField(max_length = 1000, null = True, blank = True)
	RunTime = models.IntegerField(null = True, blank = True)
	Year = models.CharField(max_length = 4, null = True, blank = True)
	Rating = models.FloatField(null = True, blank = True, default = 0)
	Num_ratings = models.IntegerField(null = True, blank = True, default = 0)
	Genres = models.ManyToManyField(Genre)
	Directors = models.ManyToManyField(People, related_name='Directors')
	Writers = models.ManyToManyField(People, related_name='Writers')

	def __str__(self):
		return self.Title

class NewRating(models.Model):
	movie = models.ForeignKey(Movie, on_delete = models.CASCADE)
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	rating = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])

	class Meta:
		unique_together = (('user', 'movie'),)
		index_together = (('user', 'movie'),)

	def __str__(self):
		return self.movie.Title + ' - ' + self.user.username
