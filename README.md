# Flask Movie Database App

This is a simple Flask application for managing a movie database. It provides a RESTful API to perform CRUD operations on movies, actors, and technicians. The app uses SQLAlchemy as the ORM for database interactions.

## Features

- Add, update, and delete movies
- Fetch details of a specific movie
- Get a list of all movies with optional filters (actors, directors, technicians)
- Add, update, and delete actors
- Add, update, and delete technicians

## Tech Stack

- Python
- Flask
- SQLAlchemy

## Usage

1. Install dependencies
2. Run the app: `python app.py`
3. Access the API at `http://127.0.0.1:5000/`

## API Endpoints

- `GET /movies`: Fetch all movies with optional filters
- `POST /movies`: Add or update a movie
- `GET /movies/<movie_id>`: Fetch details of a specific movie
- `DELETE /actors/<actor_id>`: Delete an actor if not associated with any movies
- `GET /actors`: Fetch all actors
- `POST /actors`: Add or update an actor
- `GET /technicians`: Fetch all technicians
- `POST /technicians`: Add or update a technician
- `GET /technicians/<technician_id>`: Fetch details of a specific technician

