from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource

from schemas import movie_schema, movies_schema
from models_db import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route("/")
class MovieView(Resource):

    def get(self):
        movies_all = db.session.query(Movie.id, Movie.title, Movie.description,
                                      Movie.rating, Movie.trailer,
                                      Genre.name.label('genre'),
                                      Genre.name.label('director')).join(Genre).join(Director).all()
        # return jsonify(movies_schema.dump(movies_all))
        return movies_schema.dump(movies_all), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый фильм добавлен в БД c id={new_movie.id}", 201


@movie_ns.route("/<int:mid>")
class MovieView(Resource):

    def get(self, mid):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"Фильм с выбранным Вами id={mid} отсутствует в БД", 404
        return movie_schema.dump(movie)


# genre_ns = api.namespaces('genres')
# director_ns = api.namespaces('directors')


if __name__ == '__main__':
    app.run(debug=True)
