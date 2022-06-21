from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_restx import Api, Resource

from schemas import movie_schema, movies_schema
from models_db import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {"ensure_ascii": False, "indent": 3}

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route("/")
class MovieView(Resource):

    def get(self):
        movie_query = db.session.query(Movie.id, Movie.title, Movie.description,
                                       Movie.rating, Movie.trailer, Movie.genre_id, Movie.director_id,
                                       Genre.name.label('genre'),
                                       Director.name.label('director')).join(Genre).join(Director)

        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')

        if director_id:
            movie_query = movie_query.filter(Movie.director_id == director_id)
        if genre_id:
            movie_query = movie_query.filter(Movie.genre_id == genre_id)

        movies_all = movie_query.all()

        return movies_schema.dump(movies_all), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый фильм добавлен в БД c id={new_movie.id}", 201


@movie_ns.route("/<int:mid>")
class MovieView(Resource):

    def get(self, mid: int):
        movie = db.session.query(Movie)

        if not movie:
            return f"Фильм с выбранным Вами id={mid} отсутствует в БД", 404
        return movie_schema.dump(movie), 200

    def patch(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"Фильм с выбранным Вами id={mid} отсутствует в БД", 404
        req_json = request.json

        if "title" in req_json:
            movie.title = req_json["title"]
        elif "description" in req_json:
            movie.description = req_json["description"]
        elif "rating" in req_json:
            movie.rating = req_json["rating"]
        elif "year" in req_json:
            movie.year = req_json["year"]
        elif "trailer" in req_json:
            movie.trailer = req_json["trailer"]
        db.session.add(movie)
        db.session.commit()
        return f"Изменения в БД о фильме {movie.title} добавлены", 204

    def put(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"Фильм с выбранным Вами id={mid} отсутствует в БД", 404
        req_json = request.json()

        movie.title = req_json["title"]
        movie.description = req_json["description"]
        movie.trailer = req_json["trailer"]
        movie.year = req_json["year"]
        movie.rating = req_json["rating"]
        movie.genre_id = req_json["genre_id"]
        movie.director_id = req_json["director_id"]
        db.session.add(movie)
        db.session.commit()
        return f"Сведения о фильме с выбранным Вами id={mid} обновлены в БД", 204

    def delete(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return f"Фильм с выбранным Вами id={mid} отсутствует в БД", 404
        db.session.delete(movie)
        db.session.commit()
        return f"Сведения о фильме с выбранным Вами id={mid} удалены из БД", 204


if __name__ == '__main__':
    app.run(debug=True)
