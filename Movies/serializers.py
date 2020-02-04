from rest_framework import serializers
from .models import People, Genre, Movie, NewRating
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id', 'username', 'password']
		extra_kwargs = {'password': {'write_only': True}, 'required': True}

	def create(self, validated_data):
		username = validated_data.pop('username')
		user = User.objects.create_user(username = username.lower(),**validated_data)
		Token.objects.create(user = user)
		return user


class PeopleSerializer(serializers.ModelSerializer):
	class Meta:
		model = People
		fields = '__all__'

class GenreSerializer(serializers.ModelSerializer):
	class Meta:
		model = Genre
		fields = '__all__'

class MovieSerializer(serializers.ModelSerializer):
	Directors = PeopleSerializer(read_only=True, many=True)
	Writers = PeopleSerializer(read_only=True, many=True)
	Geners = GenreSerializer(read_only=True, many=True)
	class Meta:
		model = Movie
		fields = ['id', 'ImdbId', 'Title', 'Imdb_rating', 'Image_link', 'RunTime',
				 'Year', 'Rating', 'Num_ratings', 'Geners', 'Directors', 'Writers']

class MovieMiniSerializer(serializers.ModelSerializer):
	class Meta:
		model = Movie
		fields = ['id', 'Title', 'Rating', 'Image_link' ]

class NewRatingSerializer(serializers.ModelSerializer):
	class Meta:
		model = NewRating
		fields = '__all__'
