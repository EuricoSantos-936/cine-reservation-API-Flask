# Cine Reservation API

Cine Reservation API is a Flask-based API for managing movie reservations. It provides endpoints for user management, movie management, and reservation management.

## Features

- User registration and authentication
- Movie management (add, view, delete movies)
- Reservation management (create reservations)
- Admin-only endpoints for managing movies
- JWT-based authentication
- Swagger documentation

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/euricosantos-936/cine-reservation-API-Flask.git
    cd cine-reservation-API-Flask
    ```

2. Create a virtual environment and activate it:

    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate.ps1`
    ```

3. Install the dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file based on the `.env.example`:

    ```sh
    cp .env.example .env
    ```

    Edit the `.env` file located in the root directory and add your configuration values.

5. Start the application:

    ```sh
    cd api
    flask run
    ```

    The API will be available at `http://localhost:5000`.

## Usage

### Swagger Documentation

The API documentation is available at `http://localhost:5000/apidocs/`.

![Swagger Screenshot](/apiswagger.png)

### Endpoints

#### User Endpoints

- `POST /users`: Create a new user
- `POST /users/<int:user_id>/reset_password`: Reset a user's password
- `POST /login`: Login a user

#### Movie Endpoints

- `GET /movies`: Get all movies
- `GET /movies/<int:movie_id>`: Get a specific movie by ID
- `POST /showing_movies`: Add a new movie (Admin only)
- `DELETE /movies/<int:movie_id>`: Delete a movie (Admin only)

#### Reservation Endpoints

- `POST /reservations`: Create a reservation for a movie
- `GET /reservations/<int:user_id>`: Get reservations for the authenticated user

## Configuration

The application uses environment variables for configuration. The following variables are required:

- `SECRET_KEY`: A secret key for the Flask application
- `SQLALCHEMY_DATABASE_URI`: The database URI
- `SQLALCHEMY_TRACK_MODIFICATIONS`: Whether to track modifications (usually set to `False`)
- `JWT_SECRET_KEY`: A secret key for JWT
- `JWT_VERIFY_SUB`: Whether to verify the subject claim in JWT (usually set to `False`)

## License

This project is licensed under the MIT License. See the  [LICENSE](/LICENSE) file for details.