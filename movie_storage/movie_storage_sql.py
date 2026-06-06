from sqlalchemy import create_engine, text
from colorama import Fore

# Define the database URL
DB_URL = "sqlite:///data/movies.db"

# Create the engine
engine = create_engine(DB_URL, echo=False)

# Create the movies table if it does not exist
with engine.connect() as connection:
    connection.execute(text("""CREATE TABLE IF NOT EXISTS users
                               (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT UNIQUE NOT NULL)"""))
    connection.execute(text("""CREATE TABLE IF NOT EXISTS movies
                               (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               title TEXT UNIQUE NOT NULL,
                               year INTEGER NOT NULL,
                               rating REAL NOT NULL,
                               poster TEXT UNIQUE NOT NULL,
                               user_id INTEGER NOT NULL,
                               note TEXT CHECK (length(note) <= 50),
                               FOREIGN KEY(user_id) 
                               REFERENCES users(user_id))"""))

    connection.commit()


def list_users():
    """Retrieve all users from the database"""
    with engine.connect() as connection:
        result = connection.execute(text("SELECT user_id, name FROM users"))
        users = result.fetchall()

    return {row[0]: {"name": row[1]} for row in users}


def select_user_id(user):
    """Returns the user_id of a given user"""
    with engine.connect() as connection:
        result = connection.execute(
            text("""SELECT user_id, name FROM users WHERE name = :name"""),
            {"name": user},
        )
        user_id = result.fetchall()

    return {"id": row[0] for row in user_id}


def add_new_user(name):
    """adds a new user to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("INSERT INTO users (name) VALUES (:name)"),
                {"name": name},
            )
            connection.commit()
            print(
                Fore.GREEN + "User",
                Fore.YELLOW + f"'{name}'",
                Fore.GREEN + "added successfully.",
            )
        except Exception as e:
            print(f"Error: {e}")


def list_movies(user_id):
    """Retrieve all movies from the database."""
    with engine.connect() as connection:
        result = connection.execute(
            text("""SELECT title, year, rating, poster, user_id, note FROM movies 
                    WHERE user_id = :user_id"""),
            {"user_id": user_id},
        )
        movies = result.fetchall()

    return {
        row[0]: {
            "year": row[1],
            "rating": row[2],
            "poster": row[3],
            "user_id": row[4],
            "note": row[5],
        }
        for row in movies
    }


def add_movie(title, year, rating, poster, user_id):
    """Add a new movie to the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""INSERT INTO movies (title, year, rating, poster, user_id)
                       VALUES (:title, :year, :rating, :poster, :user_id)"""),
                {
                    "title": title,
                    "year": year,
                    "rating": rating,
                    "poster": poster,
                    "user_id": user_id,
                },
            )
            connection.commit()
            print(
                Fore.GREEN + "Movie",
                Fore.YELLOW + f"'{title}'",
                Fore.GREEN + "added successfully.",
            )
        except Exception as e:
            print(f"Error: {e}")


def delete_movie(title, user_id):
    """Delete a movie from the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text(
                    """DELETE FROM movies WHERE title = :title AND user_id = :user_id"""
                ),
                {"title": title, "user_id": user_id},
            )
            connection.commit()
            print(
                Fore.GREEN + "Movie",
                Fore.YELLOW + f"'{title}'",
                Fore.GREEN + "deleted successfully.",
            )
        except Exception as e:
            print(f"Error: {e}")


def update_movie(title, note, user_id):
    """Update a movie's rating in the database."""
    with engine.connect() as connection:
        try:
            connection.execute(
                text("""UPDATE movies
                        SET note = :note
                        WHERE title = :title AND user_id = :user_id """),
                {"title": title, "note": note, "user_id": user_id},
            )
            connection.commit()
            print(
                Fore.GREEN + "Movie",
                Fore.YELLOW + f"'{title}'",
                Fore.GREEN + "updated successfully.",
            )
        except Exception as e:
            print(f"Error: {e}")
