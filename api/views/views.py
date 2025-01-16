from flask import Blueprint, jsonify, request
from functools import wraps
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_login import login_user
from api.models import models
from api.orm.data_orm import db

main_view = Blueprint("main_view", __name__)

# Decorator to check if user is admin
def admin_required(f):
    """Decorator to check if user is an admin.

    This decorator checks if the user is authenticated and is an admin.
    If the user is not an admin, it returns a 403 status code with
    an appropriate error message.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user = get_jwt_identity()
        if not current_user or not current_user.get("is_admin"):
            return jsonify({"message": "Access denied, you are not an admin"}), 403
        return f(*args, **kwargs)
    return decorated_function

# Route to create a user
@main_view.route("/users", methods=["POST"])
def create_user():
    """
    Creates a new user.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      201:
        description: User created successfully
      400:
        description: User and password are required
      409:
        description: The user already exists
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username and password:
        existing_user = models.User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({"message": "The user already exists"}), 409
        else:
            user = models.User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({"message": "User created successfully"}), 201
    else:
        return jsonify({"message": "User and password are required"}), 400

# Route to reset a user's password
@main_view.route("/users/<int:user_id>/reset_password", methods=["POST"])
def reset_password(user_id):
    """
    Resets a user's password.
    ---
    tags:
      - Users
    parameters:
      - in: path
        name: user_id
        required: true
        schema:
          type: integer
      - in: body
        name: body
        schema:
          type: object
          required:
            - new_password
          properties:
            new_password:
              type: string
    responses:
      200:
        description: Password reset successfully
      400:
        description: The new password is required
      404:
        description: User not found
    """
    user = models.User.query.get(user_id)
    if user:
        data = request.get_json()
        new_password = data.get("new_password")

        if new_password is not None:
            user.set_password(new_password)
            db.session.commit()
            return jsonify({"message": "Password reset successfully"}), 200
        else:
            return jsonify({"message": "The new password is required"}), 400
    else:
        return jsonify({"message": "User not found"}), 404

# Route to login
@main_view.route("/login", methods=["POST"])
def login():
    """
    Logs in a user.
    ---
    tags:
      - Users
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            message:
              type: string
            access_token:
              type: string
            id:
              type: integer
            is_admin:
              type: boolean
      401:
        description: Credentials are incorrect. Please try again.
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = models.User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        login_user(user)
        access_token = create_access_token(identity={"id": user.id, "is_admin": user.is_admin})
        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "id": user.id,
            "is_admin": user.is_admin
        }), 200
    else:
        return jsonify({"message": "Credentials are incorrect. Please try again."}), 401

# Route to get all movies
@main_view.route("/movies", methods=["GET"])
def get_movies():
    """
    Retrieves all movies.
    ---
    tags:
      - Movies
    responses:
      200:
        description: A list of movies
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              title:
                type: string
              description:
                type: string
              seats:
                type: integer
              room:
                type: string
      404:
        description: No movies found.
    """
    movies = models.Movie.query.all()

    if not movies:
        return jsonify({"message": "No movies found."}), 200

    movie_list = [{"id": movie.id, "Title": movie.title, "Description": movie.description, "Seats": movie.seats, "Room": movie.room} for movie in movies]
    return jsonify(movie_list)

# Route to get a specific movie by id
@main_view.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    """
    Retrieves a specific movie by its id.
    ---
    tags:
      - Movies
    parameters:
      - in: path
        name: movie_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: A movie
        schema:
          type: object
          properties:
            id:
              type: integer
            title:
              type: string
            description:
              type: string
      404:
        description: Movie not found
    """
    movie = models.Movie.query.get(movie_id)
    if movie:
        return jsonify(
            {"id": movie.id, "title": movie.title, "description": movie.description}
        )
    else:
        return jsonify({"message": "Movie not found"}), 404

# Route to create a reservation
@main_view.route("/reservations", methods=["POST"])
def create_reservation():
    """
    Creates a reservation for a given movie.
    ---
    tags:
      - Reservations
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - movie_id
            - user_id
          properties:
            movie_id:
              type: integer
            user_id:
              type: integer
    responses:
      201:
        description: Reservation created successfully
      400:
        description: Don't have available seats to this movie
      404:
        description: Movie not found
    """
    data = request.get_json()
    movie_id = data.get("movie_id")
    user_id = data.get("user_id")

    movie = models.Movie.query.get(movie_id)
    if not movie:
        return jsonify({"message": "Movie not found"}), 404

    if movie.seats <= 0:
        return jsonify({"message": "Don't have available seats to this movie"}), 400

    movie.seats -= 1

    reservation = models.Reservation(
        movie_id=movie_id,
        user_id=user_id,
        room_select=movie.room
    )
    db.session.add(reservation)
    db.session.commit()

    return jsonify({"message": "Reservation created successfully"}), 201

# Route to create a movie
@main_view.route("/showing_movies", methods=["POST"])
@admin_required
def add_showing_movie():
    """
    Creates a new movie.
    ---
    tags:
      - Movies
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - title
            - description
            - room
            - seats
          properties:
            title:
              type: string
            description:
              type: string
            room:
              type: string
            seats:
              type: integer
    responses:
      201:
        description: Movie added successfully
      400:
        description: Title, room and seats are required
      400:
        description: Room already in use
    """
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    room = data.get("room")
    seats = data.get("seats")

    if not title or not room or not seats:
        return jsonify({"message": "Title, room and seats are required"}), 400

    existing_movie = models.Movie.query.filter_by(room=room).first()
    if existing_movie:
        return jsonify({"message": "Room already in use"}), 400

    new_movie = models.Movie(
        title=title, description=description, room=room, seats=seats
    )
    db.session.add(new_movie)
    db.session.commit()

    return jsonify({"message": "Movie added successfully"}), 201

# Route to delete a movie, deletes all its reservations too
@main_view.route("/movies/<int:movie_id>", methods=["DELETE"])
@admin_required
def delete_movie(movie_id):
    """
    Deletes a movie by id and all its reservations.
    ---
    tags:
      - Movies
    parameters:
      - in: path
        name: movie_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Movie deleted successfully
      404:
        description: Movie not found
    """
    movie = models.Movie.query.get(movie_id)
    if movie is None:
        return jsonify({"message": "Movie not found"}), 404

    models.Reservation.query.filter_by(movie_id=movie_id).delete()

    db.session.delete(movie)
    db.session.commit()

    return jsonify({"message": "Movie deleted successfully"}), 200