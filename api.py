from fastapi import FastAPI,HTTPException
import sqlite3

app=FastAPI()

class Database:
    def __init__(self, db_name: str = "cine.db"):
        self.db_name = db_name
        self.init_database()
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                duration INTEGER NOT NULL,
                cast_line TEXT,
                genre TEXT,
                theatre_id INTEGER,
                show_times TEXT,
                ticket_price REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (theatre_id) REFERENCES theatres (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                loyalty_points INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Theatres table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS theatres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                total_seats INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Managers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS managers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                theatre_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (theatre_id) REFERENCES theatres (id)
            )
        ''')
        # Snacks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS snacks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                theatre_id INTEGER,
                available BOOLEAN DEFAULT 1,
                FOREIGN KEY (theatre_id) REFERENCES theatres (id)
            )
        ''')
        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id INTEGER,
                theatre_id INTEGER,
                seats_booked INTEGER,
                show_time TEXT,
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL,
                points_earned INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                FOREIGN KEY (theatre_id) REFERENCES theatres (id)
            )
        ''')
        conn.commit()
        conn.close()
db=Database()

@app.get("/")
def root():
    return {"message": "Welcome to CinePredicta API 🎬"}
@app.post("/movies")
def add_movie(title:str,duration:int,cast_line:str):
        conn=sqlite3.connect('cine.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title,duration,cast_line) VALUES(?,?,?)",(title,duration,cast_line))
        conn.commit()
        conn.close()
        return{"message":"Movie addede successfully!"}
@app.get("/movies")
def get_movies():
        conn = sqlite3.connect('cine.db')
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movies")
        movies=cursor.fetchall()
        conn.close()
        return {"movies":[dict(row) for row in movies]}
@app.put("/movies/{movie_id}")
def update_movies(movie_id:int, title:str=None, duration:int=None, cast_line:str=None):
    conn=sqlite3.connect('cine.db')
    cursor=conn.cursor()
    cursor.execute("SELECT * FROM movies WHERE id=?",(movie_id,))
    movie=cursor.fetchone()
    if not movie:
        conn.close()
        raise HTTPException(status_code=404, detail="Movie not found")
    updates=[]
    values=[]
    if title:
        updates.append("title=?")
        values.append(title)
    if duration:
        updates.append("duration=?")
        values.append(duration)
    if cast_line:
        updates.append("cast_line=?")
        values.append(cast_line)
    if updates:
        query=f"UPDATE movies SET {','.join(updates)}WHERE id=?"
        values.append(movie_id)
        cursor.execute(query, tuple(values))
        conn.commit()
    conn.close()
    return{"message":f"Movie with id {movie_id} updated successfully"}
@app.delete("/movies/{movie_id}")
def delete_movie(movie_id:int):
    conn=sqlite3.connect('cine.db')
    cursor=conn.cursor()
    cursor.execute ("DELETE FROM movies WHERE id=?",(movie_id,))
    conn.commit()
    rows_deleted=cursor.rowcount
    conn.close()
    if rows_deleted==0:
        raise HTTPException(status_code=404,detail="Movie not found")
    return{"message":f"Movie with id {movie_id} deleted successfully"}
            
             
@app.get("/users")
def get_users():
        conn = sqlite3.connect('cine.db')
        conn.row_factory = sqlite3.Row

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users=cursor.fetchall()
        conn.close()
        return {"movies":[dict(row) for row in users]}

