import sqlite3
from sqlite3 import Error
import pandas as pd
import re

def create_connection():
    """Create a database connection to SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('movie_review.db')
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def create_tables(conn):
    """Create the necessary tables in the database"""
    try:
        c = conn.cursor()
        
        # Create movies table
        c.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
                series_title TEXT NOT NULL,
                released_year INTEGER,
                certificate TEXT,
                runtime TEXT,
                genre TEXT,
                imdb_rating REAL,
                overview TEXT,
                director TEXT,
                stars TEXT,
                no_of_votes INTEGER,
                gross TEXT
            )
        ''')
        
        # Create users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                hashed_password TEXT NOT NULL,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create ratings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ratings (
                rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                score INTEGER NOT NULL CHECK(score >= 1 AND score <= 10),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (movie_id) REFERENCES movies (movie_id),
                UNIQUE(user_id, movie_id)
            )
        ''')
        
        # Create reviews table
        c.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                review_text TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (movie_id) REFERENCES movies (movie_id)
            )
        ''')
        
        conn.commit()
    except Error as e:
        print(f"Error creating tables: {e}")

def parse_year(title):
    """Extract year from title string"""
    match = re.search(r'\((\d{4})\)', title)
    return int(match.group(1)) if match else None

def parse_title(title):
    """Extract clean title from title string"""
    # Remove ranking number and dot
    title = re.sub(r'^\d+\.\s*', '', title)
    # Remove year
    title = re.sub(r'\(\d{4}\)', '', title)
    return title.strip()

def extract_director_and_stars(cast_text):
    """Extract director and stars from cast text"""
    director = ""
    stars = ""
    
    if cast_text and isinstance(cast_text, str):
        parts = cast_text.split(" | Stars: ")
        if len(parts) > 0:
            director = parts[0].replace("Director: ", "").strip()
            if len(parts) > 1:
                stars = parts[1].strip()
    
    return director, stars

def parse_votes_and_gross(info):
    """Extract votes and gross from info string"""
    votes = 0
    gross = ""
    
    if "Votes:" in info:
        votes_match = re.search(r'Votes: ([\d,]+)', info)
        if votes_match:
            votes = int(votes_match.group(1).replace(',', ''))
    
    if "Gross:" in info:
        gross_match = re.search(r'Gross: \$([\d.]+)M', info)
        if gross_match:
            gross = gross_match.group(1) + "M"
            
    return votes, gross

def load_movies_from_csv(conn, csv_file):
    """Load movie data from CSV file into the database"""
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Clear existing data
        c = conn.cursor()
        c.execute('DELETE FROM movies')
        
        for _, row in df.iterrows():
            # Parse title and year
            title = parse_title(row['Title'].split('.', 1)[1].strip())
            year = parse_year(row['Title'])
            
            # Parse director and stars
            director, stars = extract_director_and_stars(row['Cast'])
            
            # Parse votes and gross
            votes, gross = parse_votes_and_gross(row['Info'])
            
            # Insert into database
            c.execute('''
                INSERT INTO movies (
                    series_title, released_year, certificate, runtime,
                    genre, imdb_rating, overview, director, stars,
                    no_of_votes, gross
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                title, year, row['Certificate'], row['Duration'],
                row['Genre'], row['Rate'], row['Description'],
                director, stars, votes, gross
            ))
        
        conn.commit()
        print(f"Successfully loaded {len(df)} movies into database")
    except Error as e:
        print(f"Error loading movies data: {e}")
    except Exception as e:
        print(f"Error processing data: {e}")

def get_all_movies():
    """Fetch all movies from database"""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('SELECT movie_id, series_title, released_year, imdb_rating FROM movies')
            return c.fetchall()
        except Error as e:
            print(f"Error fetching movies: {e}")
        finally:
            conn.close()
    return []

def get_movie_details(movie_id):
    """Fetch detailed information for a specific movie"""
    conn = create_connection()
    if conn is not None:
        try:
            c = conn.cursor()
            c.execute('''
                SELECT * FROM movies WHERE movie_id = ?
            ''', (movie_id,))
            return c.fetchone()
        except Error as e:
            print(f"Error fetching movie details: {e}")
        finally:
            conn.close()
    return None

def add_rating(user_id, movie_id, score):
    """Add or update a movie rating"""
    conn = create_connection()
    if conn is None:
        return False, "Database connection failed"
    
    try:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO ratings (user_id, movie_id, score)
            VALUES (?, ?, ?)
        ''', (user_id, movie_id, score))
        conn.commit()
        return True, "Rating added successfully"
    except Error as e:
        return False, f"Error adding rating: {str(e)}"
    finally:
        conn.close()

def get_user_review(user_id, movie_id):
    """Get a user's review for a specific movie"""
    conn = create_connection()
    if conn is None:
        return None
    
    try:
        c = conn.cursor()
        c.execute('''
            SELECT review_text FROM reviews
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        result = c.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error getting user review: {e}")
        return None
    finally:
        conn.close()

def add_review(user_id, movie_id, review_text):
    """Add a movie review"""
    conn = create_connection()
    if conn is None:
        return False, "Database connection failed"
    
    try:
        c = conn.cursor()
        # First check if user already has a review
        existing_review = get_user_review(user_id, movie_id)
        if existing_review:
            return False, f"You have already reviewed this movie. Your review: \n\n{existing_review}"
            
        c.execute('''
            INSERT INTO reviews (user_id, movie_id, review_text)
            VALUES (?, ?, ?)
        ''', (user_id, movie_id, review_text))
        conn.commit()
        return True, "Review added successfully"
    except Error as e:
        return False, f"Error adding review: {str(e)}"
    finally:
        conn.close()

def get_user_rating(user_id, movie_id):
    """Get a user's rating for a specific movie"""
    conn = create_connection()
    if conn is None:
        return None
    
    try:
        c = conn.cursor()
        c.execute('''
            SELECT score FROM ratings
            WHERE user_id = ? AND movie_id = ?
        ''', (user_id, movie_id))
        result = c.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Error getting user rating: {e}")
        return None
    finally:
        conn.close()

def get_movie_ratings(movie_id):
    """Get all ratings and calculate average for a movie"""
    conn = create_connection()
    if conn is None:
        return None, 0
    
    try:
        c = conn.cursor()
        c.execute('''
            SELECT AVG(score) as avg_score, COUNT(*) as count
            FROM ratings WHERE movie_id = ?
        ''', (movie_id,))
        result = c.fetchone()
        return result[0], result[1] if result else (None, 0)
    except Error as e:
        print(f"Error getting movie ratings: {e}")
        return None, 0
    finally:
        conn.close()

def get_movie_reviews(movie_id):
    """Get all reviews for a movie"""
    conn = create_connection()
    if conn is None:
        return []
    
    try:
        c = conn.cursor()
        c.execute('''
            SELECT r.review_id, r.user_id, u.username, r.review_text, r.timestamp
            FROM reviews r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.movie_id = ?
            ORDER BY r.timestamp DESC
        ''', (movie_id,))
        return c.fetchall()
    except Error as e:
        print(f"Error getting movie reviews: {e}")
        return []
    finally:
        conn.close()

if __name__ == '__main__':
    # Initialize database and tables
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        # Check if movies table is empty before loading data
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM movies')
        if c.fetchone()[0] == 0:
            load_movies_from_csv(conn, 'IMDB top 1000.csv')
        conn.close()
    else:
        print("Error! Cannot create the database connection.")