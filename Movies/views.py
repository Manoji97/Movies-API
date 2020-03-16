from django.shortcuts import render, get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from .models import People, Genre, Movie, NewRating
from .serializers import PeopleSerializer, GenreSerializer, MovieSerializer, MovieMiniSerializer, NewRatingSerializer, UserSerializer
from .pagination import StandardPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticated
from django.db.models import Q


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardPagination
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {'create': [AllowAny]}

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]


class PersonList(generics.ListCreateAPIView):
    queryset = People.objects.all()
    serializer_class = PeopleSerializer


class GenresViewset(viewsets.ModelViewSet):
    '''only list_view --all,
       create_view, update_view, delete_view --only_admin
    '''
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = (TokenAuthentication,)
    pagination_class = StandardPagination
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {'list': [AllowAny]}

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        query = request.GET.get('genre', '')
        if len(query) > 0:
            queryset = queryset.filter(genre__icontains=query)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = GenreSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]


class MoviesViewset(viewsets.ModelViewSet):
    '''list_view --MovieMiniSerializer --all,
       detail_view with  --MovieSerializer --all,
       create_view, update_view, delete_view --MovieSerializer --only_admin
    '''
    queryset = Movie.objects.all()
    serializer_class = MovieMiniSerializer
    pagination_class = StandardPagination
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAdminUser,)
    permission_classes_by_action = {'list': [AllowAny],
                                    'retrieve': [AllowAny],
                                    'rate_movie': [IsAuthenticated]
                                    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        query_mainsearch = request.GET.get('ms', None)
        query_title = request.GET.get('title', None)
        query_rating = request.GET.get('rating', None)
        query_year = request.GET.get('year', None)
        query_genre = request.GET.get('genre', None)
        query_person = request.GET.get('person', None)

        if query_mainsearch:
            queryset = Movie.objects.mainsearch(query_mainsearch)
        else:
            queryset = Movie.objects.search(
                query_title, query_rating, query_year, query_genre, query_person)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MovieMiniSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        movie = get_object_or_404(self.queryset, pk=pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def rate_movie(self, request, pk=None):
        movie = get_object_or_404(self.queryset, pk=pk)
        new_rate = request.data.get('newRate', None)
        user = request.user
        if new_rate:
            try:
                new_rate = float(new_rate)
                avg_rating = movie.Rating
                tot_people = movie.Num_ratings
                new_tot_people = tot_people + 1
                new_avg_rating = round(
                    (((avg_rating*tot_people) + new_rate)/new_tot_people), 1)
                movie.Rating = new_avg_rating
                movie.Num_ratings = new_tot_people
                movie.save()
                try:
                    new_rating = NewRating.objects.get(
                        user=user.id, movie=movie.id)
                    new_rating.rating = new_rate
                    new_rating.save()
                    serializer = NewRatingSerializer(new_rating, many=False)
                    response = {'message': 'rating updated',
                                'result': serializer.data}
                    stat = status.HTTP_200_OK
                except:
                    new_rating = NewRating.objects.create(
                        user=user, movie=movie, rating=new_rate)
                    serializer = NewRatingSerializer(new_rating, many=False)
                    response = {'message': 'rating added',
                                'result': serializer.data}
                    stat = status.HTTP_200_OK
            except:
                response = {'error': 'exception when adding the rating'}
                stat = status.HTTP_400_BAD_REQUEST
        else:
            response = {'error': 'exception in getting the newRate'}
            stat = status.HTTP_400_BAD_REQUEST

        return Response(response, status=stat)

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            return [permission() for permission in self.permission_classes]
