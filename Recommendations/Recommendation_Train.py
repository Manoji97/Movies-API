import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
import sqlite3
import pickle
import os


def Train(db_path):
    try:
        con = sqlite3.connect(db_path, isolation_level=None,
                              detect_types=sqlite3.PARSE_COLNAMES)
        Movies = pd.read_sql_query("SELECT * FROM Movies_movie", con)
        Movie_genres = pd.read_sql_query(
            'select * from Movies_movie_Genres', con)
        Gneres = pd.read_sql_query('select * from Movies_genre', con)

        Genres = Gneres.set_index('id').to_dict()
        Movie_genres.genre_id = Movie_genres.genre_id.apply(
            lambda x: Genres['genre'][x])
        Movie_genres = Movie_genres.groupby(
            'movie_id')['genre_id'].apply('|'.join).reset_index()

        genre_features = Movie_genres.genre_id.str.get_dummies(sep='|')
        Movie_feartures = Movies[[
            'id', 'Imdb_rating', 'RunTime', 'Rating', 'Year']]
        Movie_feartures = pd.concat(
            [Movie_feartures, genre_features], axis=1, join='inner')

        min_max_scaler = MinMaxScaler()
        movies_final_features = min_max_scaler.fit_transform(
            Movie_feartures.reset_index())

        nbrs = NearestNeighbors(n_neighbors=5, algorithm='brute').fit(
            movies_final_features)
        distances, indices = nbrs.kneighbors(movies_final_features)

        Recommendatiosn_df = pd.DataFrame(indices)
        Recommendatiosn_df = pd.concat([Movies.id, Recommendatiosn_df], axis=1)

        with open('Recommendations.pkl', 'wb') as file:
            pickle.dump(Recommendatiosn_df, file)
        return [True, Recommendatiosn_df]
    except:
        print("error in connecting to database")
        return [False, None]


def Train_or_Get(train=None, filepath="Recommendations.pkl"):
    if not train and os.path.exists(filepath):
        indices = pd.DataFrame()
        with open(filepath, 'rb') as file:
            indices = pickle.load(file)
        return [True, indices]
    else:
        return Train('db.sqlite3')


class Get_Recommendations:
    def __init__(self):
        self.Recommendation_indices = []
        self.received = False

    def get_Indices(self):
        self.received, self.Recommendation_indices = Train_or_Get()

    def userRecommendations(self, id):
        self.get_Indices()
        MovieId = []
        if self.received:
            related = np.array(
                self.Recommendation_indices[self.Recommendation_indices.id == int(id)].iloc[:, 2:])[0]
            for i in related:
                MovieId.append(self.Recommendation_indices.iloc[i].id)
        return MovieId
