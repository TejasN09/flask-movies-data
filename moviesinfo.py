from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
db = SQLAlchemy(app)

# Movies model
class Movie(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),unique = True, nullable = False)
    year_of_release = db.Column(db.Integer)
    user_ratings = db.Column(db.Float)
    director_name = db.Column(db.String(100))
    actors = db.relationship('Actor',secondary = 'movie_actors',back_populates = 'movies')
    technicians = db.relationship('Technician', secondary='movie_technicians', back_populates='movies')
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'year_of_release': self.year_of_release,
            'user_ratings': self.user_ratings,
            'director_name': self.director_name,
            'actors': [actor.name for actor in self.actors],
            'technicians': [technician.name for technician in self.technicians]
        }
    
#actor model
class Actor(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(100),nullable = False)
    movies = db.relationship('Movie',secondary='movie_actors',back_populates='actors')

#technician model
class Technician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', secondary='movie_technicians', back_populates='technicians')
    
        
# many to many relationship for movies_actors and technicians
movie_actors = db.Table('movie_actors',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.id'), primary_key=True)
)

movie_technicians = db.Table('movie_technicians',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('technician_id', db.Integer, db.ForeignKey('technician.id'), primary_key=True)
)

# serializing data for json formate
def serialize_technician(technician):
    return {
        'id': technician.id,
        'name': technician.name,
        'movies': [movie.name for movie in technician.movies]
    }
        
def serialize_actor(actor):
    return {
        'id': actor.id,
        'name': actor.name,
        'movies': [movie.name for movie in actor.movies]
    }

# create or read the movies with all data
@app.route('/movies',methods=['GET','POST'])
def movies():
    if request.method == 'GET':
        actor_name = request.args.get('actor')
        director_name = request.args.get('director')
        technician_name = request.args.get('technician')
        
        movies_query = Movie.query
        if actor_name:
            movies_query = movies_query.filter(Movie.actors.any(name=actor_name))
        if director_name:
            movies_query = movies_query.filter(Movie.technicians.any(name=director_name))
        if technician_name:
            movies_query = movies_query.filter(Movie.technicians.any(name=technician_name))

        movies = movies_query.all()
        return jsonify([movie.serialize() for movie in movies])
        

    elif request.method == 'POST':
        data = request.json
        actors_data = data.pop('actors', [])  
        technicians_data = data.pop('technicians', []) 

        new_movie = Movie(**data)
        
        for actor_data in actors_data:
            actor = Actor(**actor_data)
            new_movie.actors.append(actor)

        for technician_data in technicians_data:
            technician = Technician(**technician_data)
            new_movie.technicians.append(technician)
        db.session.add(new_movie)
        db.session.commit()
        return jsonify({'message': 'Movie added successfully'})     
    
# To fetch actor information
@app.route('/actors', methods=['GET'])
def get_actors():
    actors = Actor.query.all()
    return jsonify([serialize_actor(actor) for actor in actors])

# To fetch technicians information
@app.route('/technicians', methods=['GET'])
def get_technicians():
    technicians = Technician.query.all()
    return jsonify([serialize_technician(technician) for technician in technicians])

# to update movie data
@app.route('/movies/update/<int:movie_id>',methods=['POST'])
def update(movie_id):
    movie = Movie.query.get_or_404(movie_id)
    
    if request.method == 'POST':
        data = request.json
        #fetching the data
        movie.name = data.get('name',movie.name)
        movie.year_of_release = data.get('year_of_release',movie.year_of_release)
        movie.user_ratings = data.get('user_ratings',movie.user_ratings)
        movie.director_name = data.get('director_name',movie.director_name)
        
        actors_data = data.get('actors',[])
        technicians_data = data.get('technicians',[])
        
        #Clear existing associations
        movie.actors = []
        movie.technicians = []
        
        #Adding new data
        for actor_data in actors_data:
            print(actor_data)
            if isinstance(actor_data, dict):  
                actor = Actor(name=actor_data.get('name'))
                movie.actors.append(actor)
            
        for technician_data in technicians_data:
            print(technician_data)
            if isinstance(technician_data, dict):  
                technician = Technician(name=technician_data.get('name'))
                movie.technicians.append(technician)
        
        db.session.commit()
        return jsonify({'message' : 'Movie updated successfully'})
    
# to delete the actor 
@app.route('/actors/<int:actor_id>', methods=['DELETE'])
def delete_actor(actor_id):
    # Delete an actor by name if not associated with any movies
    actor = Actor.query.get_or_404(actor_id)

    if actor:
        if not actor.movies:
            db.session.delete(actor)
            db.session.commit()
            return jsonify({'message': 'Actor deleted successfully'})
        else:
            return jsonify({'error': 'Cannot delete actor, as they are associated with one or more movies'}), 400
    else:
        return jsonify({'error': 'Actor not found'}), 404


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)