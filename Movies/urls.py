from django.urls import path, include
from .views import PersonList, GenresViewset, MoviesViewset, UserViewset
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'signUp', UserViewset)
router.register(r'genresall', GenresViewset)
router.register(r'movies', MoviesViewset)



urlpatterns = [
    path('people/', PersonList.as_view()),
    path('', include(router.urls))
]
