import sqlite3
import hashlib
import datetime
from typing import Optional, List, Dict, Any

class Database:
    def __init__(self, db_name: str = "cine.db"):
        self.db_name = db_name
        self.init_database()
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Users table
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
        # Movies table
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
        # Food orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                booking_id INTEGER,
                snack_id INTEGER,
                quantity INTEGER,
                total_price REAL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (booking_id) REFERENCES bookings (id),
                FOREIGN KEY (snack_id) REFERENCES snacks (id)
            )
        ''')
        # Reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                movie_id INTEGER,
                theatre_id INTEGER,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                comment TEXT,
                review_type TEXT CHECK(review_type IN ('movie', 'theatre')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                FOREIGN KEY (theatre_id) REFERENCES theatres (id)
            )
        ''')
        #seats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS seats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                theatre_id INTEGER,
                movie_id INTEGER,
                show_time TEXT,
                seat_row TEXT,
                seat_number INTEGER,
                is_booked BOOLEAN DEFAULT 0,
                booking_id INTEGER,
                FOREIGN KEY (theatre_id) REFERENCES theatres (id),
                FOREIGN KEY (movie_id) REFERENCES movies (id),
                FOREIGN KEY (booking_id) REFERENCES bookings (id)
            )
        ''')
        conn.commit()
        conn.close()
class Auth:
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return hashlib.sha256(password.encode()).hexdigest() == hashed
class Admin:
    def __init__(self, db: Database):
        self.db = db
    def signup(self, username: str, password: str, email: str) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            hashed_password = Auth.hash_password(password)
            cursor.execute(
                "INSERT INTO admins (username, password, email) VALUES (?, ?, ?)",
                (username, hashed_password, email)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    def login(self, username: str, password: str) -> Optional[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        )
        admin = cursor.fetchone()
        conn.close()
        if admin and Auth.verify_password(password, admin[2]):
            return {
                'id': admin[0],
                'username': admin[1],
                'email': admin[3]
            }
        return None
    def add_theatre(self, name: str, location: str, total_seats: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO theatres (name, location, total_seats) VALUES (?, ?, ?)",
                (name, location, total_seats)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def view_users(self) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, loyalty_points FROM users")
        users = cursor.fetchall()
        conn.close()
        return [
            {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'loyalty_points': user[3]
            }
            for user in users
        ]
    def view_theatres(self) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM theatres")
        theatres = cursor.fetchall()
        conn.close()
        return [
            {
                'id': theatre[0],
                'name': theatre[1],
                'location': theatre[2],
                'total_seats': theatre[3]
            }
            for theatre in theatres
        ]
    def delete_theatre(self, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM theatres WHERE id = ?", (theatre_id,))
            if not cursor.fetchone():
                return False
            # Delete related records first (to maintain referential integrity)
            cursor.execute("DELETE FROM reviews WHERE theatre_id = ?", (theatre_id,))
            cursor.execute("DELETE FROM food_orders WHERE booking_id IN (SELECT id FROM bookings WHERE theatre_id = ?)", (theatre_id,))
            cursor.execute("DELETE FROM bookings WHERE theatre_id = ?", (theatre_id,))
            cursor.execute("DELETE FROM snacks WHERE theatre_id = ?", (theatre_id,))
            cursor.execute("DELETE FROM movies WHERE theatre_id = ?", (theatre_id,))
            cursor.execute("DELETE FROM managers WHERE theatre_id = ?", (theatre_id,))
            cursor.execute("DELETE FROM theatres WHERE id = ?", (theatre_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def view_all_reviews(self) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT r.id, r.rating, r.comment, r.review_type, r.created_at,
                    u.username, t.name as theatre_name, m.title as movie_title
            FROM reviews r 
            JOIN users u ON r.user_id = u.id 
            JOIN theatres t ON r.theatre_id = t.id
            LEFT JOIN movies m ON r.movie_id = m.id 
            ORDER BY r.created_at DESC"""
        )
        reviews = cursor.fetchall()
        conn.close()
        return [
            {
                'id': review[0],
                'rating': review[1],
                'comment': review[2],
                'review_type': review[3],
                'created_at': review[4],
                'username': review[5],
                'theatre_name': review[6],
                'movie_title': review[7] if review[7] else 'N/A'
            }
            for review in reviews
        ]
class Manager:
    def __init__(self, db: Database):
        self.db = db
    def signup(self, username: str, password: str, email: str, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            hashed_password = Auth.hash_password(password)
            cursor.execute(
                "INSERT INTO managers (username, password, email, theatre_id) VALUES (?, ?, ?, ?)",
                (username, hashed_password, email, theatre_id)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    def login(self, username: str, password: str) -> Optional[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM managers WHERE username = ?", (username,)
        )
        manager = cursor.fetchone()
        conn.close()
        if manager and Auth.verify_password(password, manager[2]):
            return {
                'id': manager[0],
                'username': manager[1],
                'email': manager[3],
                'theatre_id': manager[4]
            }
        return None
    def add_movie(self, title: str, duration: int, cast_line: str, genre: str, 
                  show_times: str, ticket_price: float, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO movies (title, duration, cast_line, genre, show_times, ticket_price, theatre_id) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (title, duration, cast_line, genre, show_times, ticket_price, theatre_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def add_snack(self, name: str, price: float, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO snacks (name, price, theatre_id) VALUES (?, ?, ?)",
                (name, price, theatre_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def view_bookings(self, theatre_id: int) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT b.*, m.title, u.username 
               FROM bookings b 
               JOIN movies m ON b.movie_id = m.id 
               JOIN users u ON b.user_id = u.id 
               WHERE b.theatre_id = ?""",
            (theatre_id,)
        )
        bookings = cursor.fetchall()
        conn.close()
        return [
            {
                'booking_id': booking[0],
                'seats_booked': booking[4],
                'show_time': booking[5],
                'total_amount': booking[7],
                'movie_title': booking[9],
                'username': booking[10]
            }
            for booking in bookings
        ]
    def view_reviews(self, theatre_id: int) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT r.*, u.username, m.title 
               FROM reviews r 
               JOIN users u ON r.user_id = u.id 
               LEFT JOIN movies m ON r.movie_id = m.id 
               WHERE r.theatre_id = ?""",
            (theatre_id,)
        )
        reviews = cursor.fetchall()
        conn.close()
        return [
            {
                'rating': review[4],
                'comment': review[5],
                'review_type': review[6],
                'username': review[8],
                'movie_title': review[9] if review[9] else 'N/A'
            }
            for review in reviews
        ]
    def view_movies(self, theatre_id: int)-> List[Dict]:
        conn=self.db.get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM movies WHERE theatre_id=?",(theatre_id,))
        movies=cursor.fetchall()
        conn.close()
        return[
            {
                'id':movie[0],
                'title': movie[1],
                'duration': movie[2],
                'cast_line': movie[3],
                'genre': movie[4],
                'show_times': movie[6],
                'ticket_price': movie[7]
            }
            for movie in movies
        ]
    def delete_movie(self, movie_id: int, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM food_orders WHERE booking_id IN (SELECT id FROM bookings WHERE movie_id = ?)", (movie_id,))
            cursor.execute("DELETE FROM reviews WHERE movie_id = ?", (movie_id,))
            cursor.execute("DELETE FROM bookings WHERE movie_id = ?", (movie_id,))
            cursor.execute("DELETE FROM movies WHERE id = ? AND theatre_id = ?", (movie_id, theatre_id))
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except:
            return False
    def update_movie(self, movie_id: int, title: str, duration: int, cast_line: str, 
                genre: str, show_times: str, ticket_price: float, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE movies SET title = ?, duration = ?, cast_line = ?, genre = ?, 
                show_times = ?, ticket_price = ? WHERE id = ? AND theatre_id = ?""",
                (title, duration, cast_line, genre, show_times, ticket_price, movie_id, theatre_id)
            )
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except:
            return False    
    def view_snacks(self, theatre_id: int) -> List[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM snacks WHERE theatre_id = ?", (theatre_id,))
        snacks = cursor.fetchall()
        conn.close()
        return [
            {
                'id': snack[0],
                'name': snack[1],
                'price': snack[2],
                'available': snack[4]
            }
            for snack in snacks
        ]    
    def delete_snack(self, snack_id: int, theatre_id: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM food_orders WHERE snack_id = ?", (snack_id,))
            cursor.execute("DELETE FROM snacks WHERE id = ? AND theatre_id = ?", (snack_id, theatre_id))
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except:
            return False
class User:
    def __init__(self, db: Database):
        self.db = db
    def signup(self, username: str, password: str, email: str, phone: str = None) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            hashed_password = Auth.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)",
                (username, hashed_password, email, phone)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    def login(self, username: str, password: str) -> Optional[Dict]:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            if Auth.verify_password(password, user[2]):
                return {
                    'id': user[0],
                    'username': user[1],
                    'email': user[3],
                    'phone': user[4],
                    'loyalty_points': user[5]
                }
            else:
                print("Debug: Password verification failed")
        else:
            print("Debug: No user found with that username")
        return None
    def book_ticket_with_points(self, user_id: int, movie_id: int, theatre_id: int, 
                   seats: int, show_time: str, points_to_redeem:int=0) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # Get ticket price
            cursor.execute("SELECT ticket_price FROM movies WHERE id = ?", (movie_id,))
            price_result = cursor.fetchone()
            if not price_result:
                return False
            ticket_price = price_result[0]
            original_amount=ticket_price*seats
            discount=(points_to_redeem//100)*10
            total_amount = original_amount-discount
            points_earned = int(total_amount / 10)  # 1 point per $10 spent
            # Check if user has enough points
            if points_to_redeem>0:
                cursor.execute("SELECT loyalty_points FROM users WHERE id=?", (user_id,))
                user_points=cursor.fetchone()[0]
                if user_points<points_to_redeem:
                    return False
            # Create booking
            cursor.execute(
                """INSERT INTO bookings (user_id, movie_id, theatre_id, seats_booked, 
                   show_time, total_amount, points_earned) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, movie_id, theatre_id, seats, show_time, total_amount, points_earned)
            )
            # Update loyalty points
            point_change=points_earned-points_to_redeem
            cursor.execute(
                "UPDATE users SET loyalty_points = loyalty_points + ? WHERE id = ?",
                (points_earned, user_id)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def order_food(self, user_id: int, booking_id: int, snack_id: int, quantity: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            # Get snack price
            cursor.execute("SELECT price FROM snacks WHERE id = ?", (snack_id,))
            price_result = cursor.fetchone()
            if not price_result:
                return False
            total_price = price_result[0] * quantity
            cursor.execute(
                """INSERT INTO food_orders (user_id, booking_id, snack_id, quantity, total_price) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, booking_id, snack_id, quantity, total_price)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def add_review(self, user_id: int, rating: int, comment: str, 
                   review_type: str, theatre_id: int, movie_id: int = None) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO reviews (user_id, movie_id, theatre_id, rating, comment, review_type) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, movie_id, theatre_id, rating, comment, review_type)
            )
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def get_loyalty_points(self, user_id: int) -> int:
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT loyalty_points FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0
    def redeem_points(self, user_id: int, points: int) -> bool:
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET loyalty_points = loyalty_points - ? WHERE id = ? AND loyalty_points >= ?",
                (points, user_id, points)
            )
            success = cursor.rowcount > 0
            conn.commit()
            conn.close()
            return success
        except:
            return False
    def get_available_theatres(self) -> List[Dict]:
        """Get theatres that have movies available"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT DISTINCT t.id, t.name, t.location, t.total_seats 
            FROM theatres t 
            JOIN movies m ON t.id = m.theatre_id"""
        )
        theatres = cursor.fetchall()
        conn.close()
        return [
            {
                'id': theatre[0],
                'name': theatre[1],
                'location': theatre[2],
                'total_seats': theatre[3]
            }
            for theatre in theatres
        ]
    def get_movies_by_theatre(self, theatre_id: int) -> List[Dict]:
        """Get all movies for a specific theatre"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM movies WHERE theatre_id = ?",
            (theatre_id,)
        )
        movies = cursor.fetchall()
        conn.close()
        return [
            {
                'id': movie[0],
                'title': movie[1],
                'duration': movie[2],
                'cast_line': movie[3],
                'genre': movie[4],
                'theatre_id': movie[5],
                'show_times': movie[6],
                'ticket_price': movie[7]
            }
            for movie in movies
        ]
    def get_user_food_orders(self,user_id:int)->List[Dict]:
        '''Get all food orders for a user'''
        conn=self.db.get_connection()
        cursor=conn.cursor()
        cursor.execute(
            ''' SELECT fo.id, fo.quantity, fo.total_price, fo.order_date,
                    s.name as snack_name, s.price as unit_price,
                    b.id as booking_id, m.title as movie_title
                FROM food_orders fo
                JOIN snacks s ON fo.snack_id=s.id
                JOIN bookings b ON b.movie_id =b.id
                JOIN movies m ON b.movie_id=m.id
                WHERE fo.user_id=?
                ORDER BY fo.order_date DESC''',
            (user_id,)    
        )
        orders=cursor.fetchall()
        conn.close()
        return[
            {
                'id':order[0],
                'quantity':order[1],
                'total_price':order[2],
                'order_date':order[3],
                'snack_name':order[4],
                'unit_price':order[5],
                'booking_id':order[6],
                'movie_title':order[7],
            }
            for order in orders
        ]
    def get_user_reviews(self, user_id:int)->List[Dict]:
        """Get all reviews written by a user"""
        conn=self.db.get_connection()
        cursor=conn.cursor()
        cursor.execute(
            """SELECT r.id, r.rating, r.comment, r.review_type, r.created_at,
                    t.name as theatre_name, m.title as movie_title
                FROM reviews r
                JOIN theatres t ON r.theatre_id = t.id
                LEFT JOIN movies m ON r.movie_id = m.id
                WHERE r.user_id = ? 
                ORDER BY r.created_at DESC""",                
            (user_id,)    
        )
        reviews = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': review[0],
                'rating': review[1],
                'comment': review[2],
                'review_type': review[3],
                'created_at': review[4],
                'theatre_name': review[5],
                'movie_title': review[6] if review[6] else 'N/A'
            }
            for review in reviews
        ]
    def get_all_reviews(self) -> List[Dict]:
        """Get all reviews from all users"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT r.id, r.rating, r.comment, r.review_type, r.created_at,
                    u.username, t.name as theatre_name, m.title as movie_title
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN theatres t ON r.theatre_id = t.id
            LEFT JOIN movies m ON r.movie_id = m.id
            ORDER BY r.created_at DESC"""
        )
        reviews = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': review[0],
                'rating': review[1],
                'comment': review[2],
                'review_type': review[3],
                'created_at': review[4],
                'username': review[5],
                'theatre_name': review[6],
                'movie_title': review[7] if review[7] else 'N/A'
            }
            for review in reviews
        ]
    def get_user_bookings(self, user_id: int) -> List[Dict]:
        """Get all bookings for a user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT b.id, b.seats_booked, b.show_time, b.total_amount, 
                    b.booking_date, m.title, t.name 
            FROM bookings b 
            JOIN movies m ON b.movie_id = m.id 
            JOIN theatres t ON b.theatre_id = t.id 
            WHERE b.user_id = ? 
            ORDER BY b.booking_date DESC""",
            (user_id,)
        )
        bookings = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': booking[0],
                'seats_booked': booking[1],
                'show_time': booking[2],
                'total_amount': booking[3],
                'booking_date': booking[4],
                'movie_title': booking[5],
                'theatre_name': booking[6]
            }
            for booking in bookings
        ]
    def get_available_snacks(self, theatre_id: int) -> List[Dict]:
        """Get all snacks for a specific theatre"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM snacks WHERE theatre_id = ? AND available = 1",
            (theatre_id,)
        )
        snacks = cursor.fetchall()
        conn.close()
        
        return [
            {
                'id': snack[0],
                'name': snack[1],
                'price': snack[2],
                'theatre_id': snack[3]
            }
            for snack in snacks
        ]
    def get_seat_arrangement(self, theatre_id: int, movie_id: int, show_time: str) -> Dict:
        """Get seat arrangement for a specific show"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Get theatre info
        cursor.execute("SELECT total_seats FROM theatres WHERE id = ?", (theatre_id,))
        theatre_info = cursor.fetchone()
        if not theatre_info:
            return None
        
        total_seats = theatre_info[0]
        
        # Calculate rows and seats per row (assuming rectangular arrangement)
        seats_per_row = 10  # You can adjust this
        rows = (total_seats + seats_per_row - 1) // seats_per_row
        
        # Get booked seats for this show
        cursor.execute(
            """SELECT seat_row, seat_number FROM seats 
            WHERE theatre_id = ? AND movie_id = ? AND show_time = ? AND is_booked = 1""",
            (theatre_id, movie_id, show_time)
        )
        booked_seats = cursor.fetchall()
        conn.close()
        
        # Create seat map
        seat_map = {}
        for row in range(1, rows + 1):
            seat_map[chr(64 + row)] = {}  # A, B, C, etc.
            for seat in range(1, seats_per_row + 1):
                if (row - 1) * seats_per_row + seat <= total_seats:
                    seat_map[chr(64 + row)][seat] = 'Available'
        
        # Mark booked seats
        for booked_seat in booked_seats:
            row, seat_num = booked_seat
            if row in seat_map and seat_num in seat_map[row]:
                seat_map[row][seat_num] = 'Booked'
        
        return {
            'seat_map': seat_map,
            'rows': rows,
            'seats_per_row': seats_per_row,
            'total_seats': total_seats
        }
    def book_specific_seats(self, user_id: int, movie_id: int, theatre_id: int, 
                        show_time: str, selected_seats: List[tuple]) -> bool:
        """Book specific seats"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get ticket price
            cursor.execute("SELECT ticket_price FROM movies WHERE id = ?", (movie_id,))
            price_result = cursor.fetchone()
            if not price_result:
                return False
            
            ticket_price = price_result[0]
            total_amount = ticket_price * len(selected_seats)
            points_earned = int(total_amount / 10)
            
            # Create booking
            cursor.execute(
                """INSERT INTO bookings (user_id, movie_id, theatre_id, seats_booked, 
                show_time, total_amount, points_earned) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (user_id, movie_id, theatre_id, len(selected_seats), show_time, total_amount, points_earned)
            )
            booking_id = cursor.lastrowid
        
            # Book individual seats
            for seat_row, seat_number in selected_seats:
                cursor.execute(
                    """INSERT INTO seats (theatre_id, movie_id, show_time, seat_row, 
                    seat_number, is_booked, booking_id) VALUES (?, ?, ?, ?, ?, 1, ?)""",
                    (theatre_id, movie_id, show_time, seat_row, seat_number, booking_id)
                )
            
            # Update loyalty points
            cursor.execute(
                "UPDATE users SET loyalty_points = loyalty_points + ? WHERE id = ?",
                (points_earned, user_id)
            )
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    def book_specific_seats_with_points(self,user_id:int, movie_id:int, theatre_id:int,
                        show_time:str, selected_seats:List[tuple], points_to_redeem:int=0) -> bool:
        """Book specific seats with optional loyalty points redemption""" 
        try:
            conn=self.db.get_connection()
            cursor=conn.cursor()
            #Get ticket price
            cursor.execute("SELECT ticket_price FROM movies WHERE id=?",(movie_id,))
            price_result=cursor.fetchone()
            if not price_result:
                conn.close()
                return False
            ticket_price=price_result[0] 
            original_cost=ticket_price*len(selected_seats)
            discount=(points_to_redeem//100)*10
            final_cost=original_cost-discount
            points_earned=int(final_cost/10)        
            # Check if user has enough points to redeem
            if points_to_redeem>0:
                cursor.execute("SELECT loyalty_points FROM users WHERE id=?",(user_id,))
                user_result=cursor.fetchone()
                if not user_result or user_result[0]< points_to_redeem:
                    conn.close()
                    return False
            # Create booking
            cursor.execute(
                """INSERT INTO bookings (user_id, movie_id, theatre_id, seats_booked,
                show_time, total_amount, points_earned) VALUES(?, ?, ?, ?, ?, ?, ?)""",
                (user_id, movie_id, theatre_id, len(selected_seats), show_time, final_cost, points_earned)
            )      
            booking_id=cursor.lastrowid
            # Book individual seats
            for seat_row, seat_number in selected_seats:
                cursor.execute(
                    """INSERT INTO seats (theatre_id, movie_id, show_time, seat_row,
                    seat_number, is_booked, booking_id) VALUES (?, ?, ?, ?, ?, 1, ?)""",
                    (theatre_id, movie_id, show_time, seat_row, seat_number, booking_id)
                )
            # Update loyalty points (subtract redeemed points, add earned points)
            point_change=points_earned-points_to_redeem
            cursor.execute(
                "UPDATE users SET loyalty_points=loyalty_points + ? WHERE id=?",
                (point_change, user_id)
            )    
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            if 'conn' in locals():
                conn.close()
            return False    
        
class CinePredicta:
    def __init__(self):
        self.db = Database()
        self.admin = Admin(self.db)
        self.manager = Manager(self.db)
        self.user = User(self.db)
        self.current_user = None
        self.current_user_type = None
    def main_menu(self):
        try:
            while True:
                print("\n" + "="*50)
                print("🎬 WELCOME TO CINEPREDICTA 🎬")
                print("="*50)
                print("1. Admin Login/Signup")
                print("2. Manager Login/Signup")
                print("3. User Login/Signup")
                print("4. Exit")
                choice = input("\nEnter your choice: ")
                if choice == '1':
                    self.admin_menu()
                elif choice == '2':
                    self.manager_menu()
                elif choice == '3':
                    self.user_menu()
                elif choice == '4':
                    print("Thank you for using CinePredicta!")
                    break
                else:
                    print("Invalid choice! Please try again.")
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using CinePredicta! Goodbye!")    
    def admin_menu(self):
        while True:
            print("\n" + "="*30)
            print("ADMIN SECTION")
            print("="*30)
            print("1. Login")
            print("2. Signup")
            print("3. Back to Main Menu")
            choice = input("\nEnter your choice: ")
            if choice == '1':
                username = input("Username: ")
                password = input("Password: ")
                admin_data = self.admin.login(username, password)
                if admin_data:
                    self.current_user = admin_data
                    self.current_user_type = 'admin'
                    self.admin_dashboard()
                else:
                    print("Invalid credentials!")
            elif choice == '2':
                username = input("Username: ")
                password = input("Password: ")
                email = input("Email: ")
                if self.admin.signup(username, password, email):
                    print("Admin signup successful!")
                else:
                    print("Signup failed! Username or email already exists.")
            elif choice == '3':
                break
    def admin_dashboard(self): 
        while True:
            print(f"\n🔧 ADMIN DASHBOARD - Welcome {self.current_user['username']}!")
            print("1. Add Theatre")
            print("2. View All Users")
            print("3. View All Theatres")
            print("4. Delete Theatre")
            print("5. View All Reviews")
            print("6. Logout")
            choice = input("\nEnter your choice: ")
            if choice == '1':
                while True:
                    print("\n---ADD THEATRE---")
                    name = input("Theatre Name(or 'back' to return): ")
                    if name.lower()=='back':
                        break
                    location = input("Location(or 'back to return): ")
                    if location.lower()=='back':
                        break
                    try:
                        seats_input = input("Total Seats (or 'back' to return): ")
                        if seats_input.lower() == 'back':
                            break
                        total_seats = int(seats_input)
                        if self.admin.add_theatre(name, location, total_seats):
                            print("Theatre added successfully!")
                            break
                        else:
                            print("Failed to add theatre!")
                            break
                    except ValueError:
                        print("Invalid input for total seats!")
            elif choice == '2':
                while True:
                    print("\n--- ALL USERS ---")
                    users = self.admin.view_users()
                    print(f"Total Users: {len(users)}")
                    for user in users:
                        print(f"ID: {user['id']}, Username: {user['username']}, "
                            f"Email: {user['email']}, Points: {user['loyalty_points']}")
                    back_choice = input("\nPress Enter to go back to admin dashboard: ")
                    break
            elif choice == '3':
                while True:
                    print("\n--- ALL THEATRES ---")
                    theatres = self.admin.view_theatres()
                    print(f"Total Theatres: {len(theatres)}")
                    for theatre in theatres:
                        print(f"ID: {theatre['id']}, Name: {theatre['name']}, "
                            f"Location: {theatre['location']}, Seats: {theatre['total_seats']}")
                    back_choice = input("\nPress Enter to go back to admin dashboard: ")
                    break
            elif choice == '4':
                while True:
                    theatres = self.admin.view_theatres()
                    if not theatres:
                        print("No theatres available to delete!")
                        break
                    print("\n🏢 Available Theatres:")
                    for theatre in theatres:
                        print(f"ID: {theatre['id']}, Name: {theatre['name']}, "
                            f"Location: {theatre['location']}")
                    print("0. Back to Admin Dashboard")          
                    try:
                        theatre_choice = input("\nEnter Theatre ID to delete(or 0 to go back): ")
                        if theatre_choice=='0':
                            break
                        theatre_id=int(theatre_choice)
                        confirm = input(f"Are you sure you want to delete this theatre? This will also delete all related movies, bookings, and reviews. (y/n): ")
                        if confirm.lower() == 'y':
                            if self.admin.delete_theatre(theatre_id):
                                print("Theatre deleted successfully!")
                            else:
                                print("Failed to delete theatre or theatre not found!")
                        else:
                            print("Deletion cancelled.")
                    except ValueError:
                        print("Invalid theatre ID!")
            elif choice == '5':
                while True:
                    print("\n--- ALL REVIEWS ---")
                    reviews = self.admin.view_all_reviews()
                    print(f"Total Reviews: {len(reviews)}")
                    for review in reviews:
                        print(f"\nReview ID: {review['id']}")
                        print(f"Rating: {review['rating']}/5 | Type: {review['review_type']}")
                        print(f"User: {review['username']} | Theatre: {review['theatre_name']}")
                        if review['movie_title'] != 'N/A':
                            print(f"Movie: {review['movie_title']}")
                        print(f"Comment: {review['comment']}")
                        print(f"Date: {review['created_at']}")
                        print("-" * 50)
                    back_choice = input("\nPress Enter to go back to admin dashboard: ")
                    break
            elif choice == '6':
                self.current_user = None
                self.current_user_type = None
                break
    def manager_menu(self):
        while True:
            print("\n" + "="*30)
            print("MANAGER SECTION")
            print("="*30)
            print("1. Login")
            print("2. Signup")
            print("3. Back to Main Menu")
            choice = input("\nEnter your choice: ")
            if choice == '1':
                username = input("Username: ")
                password = input("Password: ")
                manager_data = self.manager.login(username, password)
                if manager_data:
                    self.current_user = manager_data
                    self.current_user_type = 'manager'
                    self.manager_dashboard()
                else:
                    print("Invalid credentials!")
            elif choice == '2':
                username = input("Username: ")
                password = input("Password: ")
                email = input("Email: ")
                # Show available theatres
                theatres = self.admin.view_theatres()
                if not theatres:
                    print("No theatres available. Please contact admin.")
                    continue
                print("\nAvailable Theatres:")
                for theatre in theatres:
                    print(f"ID: {theatre['id']}, Name: {theatre['name']}")
                theatre_id = int(input("Enter Theatre ID to manage: "))
                if self.manager.signup(username, password, email, theatre_id):
                    print("Manager signup successful!")
                else:
                    print("Signup failed! Username or email already exists.")
            elif choice == '3':
                break
    def manager_dashboard(self):
        while True:
            print(f"\n🎭 MANAGER DASHBOARD - Welcome {self.current_user['username']}!")
            print(f"Managing Theatre ID: {self.current_user['theatre_id']}")
            print("1. Add Movie")
            print("2. Add Snack")
            print("3. View Bookings")
            print("4. View Reviews")
            print("5. View Movies")
            print("6. Delete Movie")
            print("7. Edit Movie")
            print("8. View Snacks")
            print("9. Delete Snacks")
            print("10. Logout")
            choice = input("\nEnter your choice: ")
            if choice == '1':
                while True:
                    print("\n ---ADD MOVIE---")
                    title = input("Movie Title(or 'back to return): ")
                    if title.lower()=='back':
                        break
                # Handle duration input - allow both formats
                    duration_input = input("Duration (e.g., '149' for minutes or '2h 29m')(or 'back to return): ")
                    if duration_input.lower()=='back':
                        break
                    try:
                        if 'h' in duration_input.lower() or 'm' in duration_input.lower():
                        # Parse format like "2h 29m" or "2h" or "149m"
                            duration = self.parse_duration(duration_input)
                        else:
                        # Assume it's already in minutes
                            duration = int(duration_input)
                    except ValueError:
                        print("Invalid duration format! Please use minutes (e.g., 149) or format like '2h 29m'")
                        continue
                    cast_line = input("Cast(or 'back' to return): ")
                    if cast_line.lower()=='back':
                        break
                    genre = input("Genre (or 'back' to return): ")
                    if genre.lower()=='back':
                        break
                    show_times = input("Show Times (comma separated) (or 'back' to return): ")
                    if show_times.lower()=='back':
                        break
                    try:
                        price_input=input("Ticket Price:$ (or 'back' to return): ")
                        if price_input.lower()=='back':
                            break
                        ticket_price = float(price_input)
                        if self.manager.add_movie(title, duration, cast_line, genre, 
                                        show_times, ticket_price, self.current_user['theatre_id']):
                            print("Movie added successfully!")
                            break
                        else:
                            print("Failed to add movie!")
                            break
                    except ValueError:
                        print("Invalid ticket price!")        
            elif choice == '2':
                while True:
                    print("\n--- ADD SNACK ---")
                    name = input("Snack Name (or 'back' to return): ")
                    if name.lower() == 'back':
                        break
                    try:
                        price_input = input("Price: $ (or 'back' to return): ")
                        if price_input.lower() == 'back':
                            break
                        price = float(price_input)
                        if self.manager.add_snack(name, price, self.current_user['theatre_id']):
                            print("Snack added successfully!")
                            break
                        else:
                            print("Failed to add snack!")
                            break
                    except ValueError:
                        print("Invalid price!")
            elif choice == '3':
                while True:
                    print("\n--- VIEW BOOKINGS ---")
                    bookings = self.manager.view_bookings(self.current_user['theatre_id'])
                    print(f"Total Bookings: {len(bookings)}")
                    total_seats = sum(booking['seats_booked'] for booking in bookings)
                    print(f"Total Seats Booked: {total_seats}")
                    for booking in bookings:
                        print(f"Booking ID: {booking['booking_id']}, Movie: {booking['movie_title']}, "
                            f"User: {booking['username']}, Seats: {booking['seats_booked']}, "
                            f"Show: {booking['show_time']}, Amount: ${booking['total_amount']}")
                    back_choice = input("\nPress Enter to go back to manager dashboard: ")
                    break
            elif choice == '4':
                reviews = self.manager.view_reviews(self.current_user['theatre_id'])
                print(f"\n⭐ Total Reviews: {len(reviews)}")
                for review in reviews:
                    print(f"Rating: {review['rating']}/5, Type: {review['review_type']}, "
                          f"User: {review['username']}, Movie: {review['movie_title']}")
                    print(f"Comment: {review['comment']}\n")
                back_choice=input("\n Press Enter to go back to manager dashboard: ")
                break   
            elif choice=='5':
                while True:
                    print("\n---VIEW MOVIES---")
                    movies = self.manager.view_movies(self.current_user['theatre_id'])
                    if not movies:
                        print("No movies found!")
                        input("Press Enter to go back to manager dashboard: ")
                        break
                    print(f"Total Movies: {len(movies)}")
                    for movie in movies:
                        duration_hours = movie['duration'] // 60
                        duration_mins = movie['duration'] % 60
                        print(f"\nMovie ID: {movie['id']}")
                        print(f"Title: {movie['title']}")
                        print(f"Duration: {duration_hours}h {duration_mins}m")
                        print(f"Cast: {movie['cast_line']}")
                        print(f"Genre: {movie['genre']}")
                        print(f"Show Times: {movie['show_times']}")
                        print(f"Ticket Price: ${movie['ticket_price']}")
                        print("-" * 50)
                    back_choice = input("\nPress Enter to go back to manager dashboard: ")
                    break
            elif choice=='6':
                while True:
                    print("\n--- DELETE MOVIE ---")
                    movies = self.manager.view_movies(self.current_user['theatre_id'])
                    if not movies:
                        print("No movies found to delete!")
                        input("Press Enter to go back to manager dashboard: ")
                        break
                    print("Available Movies:")
                    for movie in movies:
                        print(f"ID: {movie['id']}, Title: {movie['title']}, Price: ${movie['ticket_price']}")
                    try:
                        movie_choice = input("\nEnter Movie ID to delete (or 'back' to return): ")
                        if movie_choice.lower() == 'back':
                            break                            
                        movie_id = int(movie_choice)
                        confirm = input("Are you sure you want to delete this movie? This will also delete all related bookings and reviews. (y/n): ")
                        if confirm.lower() == 'y':
                            if self.manager.delete_movie(movie_id, self.current_user['theatre_id']):
                                print("Movie deleted successfully!")
                            else:
                                print("Failed to delete movie or movie not found!")
                        else:
                            print("Deletion cancelled.")
                    except ValueError:
                        print("Invalid input!")
            elif choice=='7':
                while True:
                    print("\n--- EDIT MOVIE ---")
                    movies = self.manager.view_movies(self.current_user['theatre_id'])
                    if not movies:
                        print("No movies found to edit!")
                        input("Press Enter to go back to manager dashboard: ")
                        break
                    print("Available Movies:")
                    for movie in movies:
                        print(f"ID: {movie['id']}, Title: {movie['title']}")
                    try:
                        movie_choice = input("\nEnter Movie ID to edit (or 'back' to return): ")
                        if movie_choice.lower() == 'back':
                            break
                        movie_id = int(movie_choice)
                        # Find the movie to get current values
                        current_movie = None
                        for movie in movies:
                            if movie['id'] == movie_id:
                                current_movie = movie
                                break
                        if not current_movie:
                            print("Movie not found!")
                            continue
                        print(f"\nEditing: {current_movie['title']}")
                        print("Press Enter to keep current value, or type new value:")
                        title = input(f"Title [{current_movie['title']}]: ") or current_movie['title']
                        if title.lower() == 'back':
                            break
                        duration_input = input(f"Duration [{current_movie['duration']} mins]: ") or str(current_movie['duration'])
                        if duration_input.lower() == 'back':
                            break
                        try:
                            if 'h' in duration_input.lower() or 'm' in duration_input.lower():
                                duration = self.parse_duration(duration_input)
                            else:
                                duration = int(duration_input)
                        except ValueError:
                            print("Invalid duration format!")
                            continue
                        cast_line = input(f"Cast [{current_movie['cast_line']}]: ") or current_movie['cast_line']
                        if cast_line.lower() == 'back':
                            break
                        genre = input(f"Genre [{current_movie['genre']}]: ") or current_movie['genre']
                        if genre.lower() == 'back':
                            break
                        show_times = input(f"Show Times [{current_movie['show_times']}]: ") or current_movie['show_times']
                        if show_times.lower() == 'back':
                            break
                        price_input = input(f"Ticket Price [${current_movie['ticket_price']}]: ") or str(current_movie['ticket_price'])
                        if price_input.lower() == 'back':
                            break
                        try:
                            ticket_price = float(price_input)
                        except ValueError:
                            print("Invalid price!")
                            continue
                        if self.manager.update_movie(movie_id, title, duration, cast_line, 
                                                genre, show_times, ticket_price, self.current_user['theatre_id']):
                            print("Movie updated successfully!")
                            break
                        else:
                            print("Failed to update movie!")
                            break
                    except ValueError:
                        print("Invalid movie ID!")
            elif choice=='8':
                while True:
                    print("\n--- VIEW SNACKS ---")
                    snacks = self.manager.view_snacks(self.current_user['theatre_id'])
                    if not snacks:
                        print("No snacks found!")
                        input("Press Enter to go back to manager dashboard: ")
                        break
                    print(f"Total Snacks: {len(snacks)}")
                    for snack in snacks:
                        status = "Available" if snack['available'] else "Not Available"
                        print(f"ID: {snack['id']}, Name: {snack['name']}, "
                            f"Price: ${snack['price']}, Status: {status}")
                    back_choice = input("\nPress Enter to go back to manager dashboard: ")
                    break
            elif choice=='9':       
                while True:
                    print("\n--- DELETE SNACK ---")
                    snacks = self.manager.view_snacks(self.current_user['theatre_id'])
                    if not snacks:
                        print("No snacks found to delete!")
                        input("Press Enter to go back to manager dashboard: ")
                        break
                    print("Available Snacks:")
                    for snack in snacks:
                        print(f"ID: {snack['id']}, Name: {snack['name']}, Price: ${snack['price']}")
                    try:
                        snack_choice = input("\nEnter Snack ID to delete (or 'back' to return): ")
                        if snack_choice.lower() == 'back':
                            break
                        snack_id = int(snack_choice)
                        confirm = input("Are you sure you want to delete this snack? (y/n): ")
                        if confirm.lower() == 'y':
                            if self.manager.delete_snack(snack_id, self.current_user['theatre_id']):
                                print("Snack deleted successfully!")
                            else:
                                print("Failed to delete snack or snack not found!")
                        else:
                            print("Deletion cancelled.")       
                    except ValueError:
                        print("Invalid input!")         
            elif choice == '10':
                self.current_user = None
                self.current_user_type = None
                break
    def parse_duration(self, duration_str: str) -> int:
        """Parse duration string like '2h 29m' or '149m' into total minutes"""
        duration_str = duration_str.lower().replace(' ', '')
        total_minutes = 0
        # Extract hours
        if 'h' in duration_str:
            h_index = duration_str.index('h')
            hours = int(duration_str[:h_index])
            total_minutes += hours * 60
            duration_str = duration_str[h_index+1:]
        # Extract minutes
        if 'm' in duration_str:
            m_index = duration_str.index('m')
            if duration_str[:m_index]:  
                minutes = int(duration_str[:m_index])
                total_minutes += minutes
        return total_minutes
    def user_menu(self):
        while True:
            print("\n" + "="*30)
            print("USER SECTION")
            print("="*30)
            print("1. Login")
            print("2. Signup")
            print("3. Back to Main Menu")
            choice = input("\nEnter your choice: ")
            if choice == '1':
                username = input("Username: ")
                password = input("Password: ")
                user_data = self.user.login(username, password)
                if user_data:
                    self.current_user = user_data
                    self.current_user_type = 'user'
                    self.user_dashboard()
                else:
                    print("Invalid credentials!")
            elif choice == '2':
                username = input("Username: ")
                password = input("Password: ")
                email = input("Email: ")
                while True:
                    phone = input("Phone (optional): ")
                    if phone.isdigit() and len(phone)==10:
                        break
                    else:
                        print("Please enter 10 digits")
                if self.user.signup(username, password, email, phone):
                    print("User signup successful!")
                else:
                    print("Signup failed! Username or email already exists.")
            elif choice == '3':
                break
    def user_dashboard(self):
        while True:
            points = self.user.get_loyalty_points(self.current_user['id'])
            print(f"\n🎪 USER DASHBOARD - Welcome {self.current_user['username']}!")
            print(f"💎 Loyalty Points: {points}")
            print("1. Book Ticket")
            print("2. Order Food")
            print("3. Add Review")
            print("4. View Loyalty Points")
            print("5. Redeem Points")
            print("6. View My Tickets")
            print("7. View My Food Orders")
            print("8. Browse Reviews")
            print("9. Logout")
            choice = input("\nEnter your choice: ")
            if choice == '1':
                self.view_seat_arrangement_interface()
            elif choice == '2':
                self.order_food_interface()
            elif choice == '3':
                self.add_review_interface()
            elif choice == '4':
                points = self.user.get_loyalty_points(self.current_user['id'])
                print(f"Your current loyalty points: {points}")
                print("💡 Tip: You can redeem 100 points for $10 discount!")
            elif choice == '5':
                self.redeem_points_interface()
            elif choice == '6':
                while True:
                    print("\n--- MY TICKETS ---")
                    bookings = self.user.get_user_bookings(self.current_user['id'])
                    if not bookings:
                        print("No tickets found!")
                        input("Press Enter to go back to user dashboard: ")
                        break
                    
                    print(f"Total Bookings: {len(bookings)}")
                    for booking in bookings:
                        print(f"\nBooking ID: {booking['id']}")
                        print(f"Movie: {booking['movie_title']}")
                        print(f"Theatre: {booking['theatre_name']}")
                        print(f"Seats: {booking['seats_booked']}")
                        print(f"Show Time: {booking['show_time']}")
                        print(f"Amount Paid: ${booking['total_amount']}")
                        print(f"Booking Date: {booking['booking_date']}")
                        print("-" * 40)
                    
                    back_choice = input("\nPress Enter to go back to user dashboard: ")
                    break    
            elif choice == '7':
                while True:
                    print("\n--- MY FOOD ORDERS ---")
                    food_orders = self.user.get_user_food_orders(self.current_user['id'])
                    if not food_orders:
                        print("No food orders found!")
                        input("Press Enter to go back to user dashboard: ")
                        break
                    
                    print(f"Total Food Orders: {len(food_orders)}")
                    for order in food_orders:
                        print(f"\nOrder ID: {order['id']}")
                        print(f"Snack: {order['snack_name']}")
                        print(f"Quantity: {order['quantity']}")
                        print(f"Unit Price: ${order['unit_price']}")
                        print(f"Total Price: ${order['total_price']}")
                        print(f"Movie: {order['movie_title']}")
                        print(f"Booking ID: {order['booking_id']}")
                        print(f"Order Date: {order['order_date']}")
                        print("-" * 40)
                    
                    back_choice = input("\nPress Enter to go back to user dashboard: ")
                    break
            elif choice == '8':
                while True:
                    print("\n---BROWSE REVIEWS---")
                    print("1.View My Reviews")
                    print("2.View All Reviews")
                    print("3.Back to User Dashboard")
                    review_choice=input("\nEnter your choice: ")
                    if review_choice=='1':
                        print("\n---MY REVIEWS---")
                        reviews=self.user.get_user_reviews(self.current_user['id'])
                        if not reviews:
                            print("You haven't written any reviews yet!")
                        else:
                            print(f"Total Reviews Written: {len(reviews)}")
                            for review in reviews:
                                print(f"\nReview ID: {review['id']}")
                                print(f"Rating: {review['rating']}/5 ⭐")
                                print(f"Type: {review['review_type'].title()}")
                                print(f"Treatre: {review['theatre_name']}")
                                if review['movie_title'] !='N/A':
                                    print(f"Movie: {review['movie_title']}")
                                print(f"Comment: {review['comment']}")
                                print(f"Date: {review['created_at']}")
                                print("-" * 40)    
                        input("\nPress Enter to continue...") 
                    elif review_choice=='2':
                        print("\n---ALL REVIEWS---")
                        all_reviews=self.user.get_all_reviews()
                        if not all_reviews:
                            print("No reviews fount!")
                        else:
                            print(f"Total Reviews: {len(all_reviews)}")
                            for review in all_reviews:
                                print(f"\nRating: {review['rating']}/5 ⭐")
                                print(f"User: {review['username']}")
                                print(f"Type: {review['review_type'].title()}")
                                print(f"Theatre: {review['theatre_name']}")
                                if review['movie_title'] !='N/A':
                                    print(f"Movie: {review['movie_title']}")
                                print(f"Comment: {review['comment']}")
                                print(f"Date: {review['created_at']}")
                                print(f"-" * 40)
                        input("\nPress Enter to continue...")
                    elif review_choice=='3':
                        break
                    else:
                        print("Invalied choice")            
            elif choice == '9':
                self.current_user = None
                self.current_user_type = None
                break
    def order_food_interface(self):
            while True:
                print("\n--- ORDER FOOD ---")
                
                # First, show user's bookings to select from
                bookings = self.user.get_user_bookings(self.current_user['id'])
                if not bookings:
                    print("You need to book a ticket first before ordering food!")
                    input("Press Enter to go back to user dashboard: ")
                    break
                
                print("Your Bookings:")
                for i, booking in enumerate(bookings, 1):
                    print(f"{i}. Booking ID: {booking['id']} - {booking['movie_title']} at {booking['theatre_name']}")
                
                try:
                    booking_choice = input("\nSelect booking number (or 'back' to return): ")
                    if booking_choice.lower() == 'back':
                        break
                    
                    booking_index = int(booking_choice) - 1
                    if booking_index < 0 or booking_index >= len(bookings):
                        print("Invalid booking selection!")
                        continue
                    
                    selected_booking = bookings[booking_index]
                    booking_id = selected_booking['id']
                    
                    # Get theatre_id from the booking to show relevant snacks
                    conn = self.user.db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT theatre_id FROM bookings WHERE id = ?", (booking_id,))
                    theatre_result = cursor.fetchone()
                    conn.close()
                    
                    if not theatre_result:
                        print("Error: Could not find theatre information!")
                        continue
                        
                    theatre_id = theatre_result[0]
                    
                    # Show available snacks for this theatre
                    snacks = self.user.get_available_snacks(theatre_id)
                    if not snacks:
                        print("No snacks available for this theatre!")
                        continue
                    
                    print(f"\nAvailable Snacks at {selected_booking['theatre_name']}:")
                    for i, snack in enumerate(snacks, 1):
                        print(f"{i}. {snack['name']} - ${snack['price']}")
                    
                    snack_choice = input("\nSelect snack number (or 'back' to return): ")
                    if snack_choice.lower() == 'back':
                        continue
                    
                    snack_index = int(snack_choice) - 1
                    if snack_index < 0 or snack_index >= len(snacks):
                        print("Invalid snack selection!")
                        continue
                    
                    selected_snack = snacks[snack_index]
                    snack_id = selected_snack['id']
                    
                    quantity = input(f"Enter quantity for {selected_snack['name']} (or 'back' to return): ")
                    if quantity.lower() == 'back':
                        continue
                    
                    try:
                        quantity = int(quantity)
                        if quantity <= 0:
                            print("Quantity must be greater than 0!")
                            continue
                        
                        total_price = selected_snack['price'] * quantity
                        print(f"\nOrder Summary:")
                        print(f"Snack: {selected_snack['name']}")
                        print(f"Quantity: {quantity}")
                        print(f"Unit Price: ${selected_snack['price']}")
                        print(f"Total Price: ${total_price}")
                        print(f"For Movie: {selected_booking['movie_title']}")
                        
                        confirm = input("\nConfirm order? (y/n): ")
                        if confirm.lower() == 'y':
                            if self.user.order_food(self.current_user['id'], booking_id, snack_id, quantity):
                                print("Food order placed successfully!")
                                break
                            else:
                                print("Order failed!")
                        else:
                            print("Order cancelled.")
                            
                    except ValueError:
                        print("Invalid quantity!")
                        
                except ValueError:
                    print("Invalid input!")       
    def add_review_interface(self):
        print("1. Review Movie")
        print("2. Review Theatre")
        review_choice = input("Choose review type: ")
        rating = int(input("Rating (1-5): "))
        comment = input("Comment: ")
        theatre_id = int(input("Theatre ID: "))        
        if review_choice == '1':
            movie_id = int(input("Movie ID: "))
            review_type = 'movie'
        else:
            movie_id = None
            review_type = 'theatre'
        if self.user.add_review(self.current_user['id'], rating, comment, 
                              review_type, theatre_id, movie_id):
            print("Review added successfully! ⭐")
        else:
            print("Failed to add review!")    
    def redeem_points_interface(self):
        current_points = self.user.get_loyalty_points(self.current_user['id'])
        print(f"Current points: {current_points}")
        print("Redemption Options:")
        print("1. 100 points = $10 discount")
        print("2. 500 points = Free ticket")
        if current_points < 100:
            print("Insufficient points!")
            return        
        choice = input("Choose redemption option: ")
        
        if choice == '1' and current_points >= 100:
            if self.user.redeem_points(self.current_user['id'], 100):
                print("Redeemed 100 points for $10 discount! 💰")
        elif choice == '2' and current_points >= 500:
            if self.user.redeem_points(self.current_user['id'], 500):
                print("Redeemed 500 points for a free ticket! 🎟️")
        else:
            print("Invalid choice or insufficient points!")
    def view_seat_arrangement_interface(self):
        while True:
            print("\n🎭 AVAILABLE THEATRES:")
            
            # Show available theatres with movies
            theatres = self.user.get_available_theatres()
            if not theatres:
                print("No theatres with movies available!")
                input("Press Enter to go back: ")
                break

            print("Available Theatres:")
            for i, theatre in enumerate(theatres, 1):
                print(f"{i}. {theatre['name']} - {theatre['location']}")

            try:
                theatre_choice = input("\nSelect theatre number (or 'back' to return): ")
                if theatre_choice.lower() == 'back':
                    break

                theatre_index = int(theatre_choice) - 1
                if theatre_index < 0 or theatre_index >= len(theatres):
                    print("Invalid theatre selection!")
                    continue

                selected_theatre = theatres[theatre_index]

                # Show movies in selected theatre
                movies = self.user.get_movies_by_theatre(selected_theatre['id'])
                if not movies:
                    print("No movies available in this theatre!")
                    continue

                print(f"\nMovies at {selected_theatre['name']}:")
                for i, movie in enumerate(movies, 1):
                    print(f"{i}. {movie['title']} - ${movie['ticket_price']}")

                movie_choice = input("\nSelect movie number (or 'back' to return): ")
                if movie_choice.lower() == 'back':
                    continue

                movie_index = int(movie_choice) - 1
                if movie_index < 0 or movie_index >= len(movies):
                    print("Invalid movie selection!")
                    continue

                selected_movie = movies[movie_index]

                # Show available show times
                show_times = selected_movie['show_times'].split(',')
                print(f"\nShow Times for {selected_movie['title']}:")
                for i, show_time in enumerate(show_times, 1):
                    print(f"{i}. {show_time.strip()}")

                show_choice = input("\nSelect show time number (or 'back' to return): ")
                if show_choice.lower() == 'back':
                    continue

                show_index = int(show_choice) - 1
                if show_index < 0 or show_index >= len(show_times):
                    print("Invalid show time selection!")
                    continue

                selected_show_time = show_times[show_index].strip()

                # Display seat arrangement
                seat_info = self.user.get_seat_arrangement(
                    selected_theatre['id'], selected_movie['id'], selected_show_time
                )
                
                if not seat_info:
                    print("Could not load seat information!")
                    continue

                print(f"\n=== SEAT ARRANGEMENT ===")
                print(f"Theatre: {selected_theatre['name']}")
                print(f"Movie: {selected_movie['title']}")
                print(f"Show Time: {selected_show_time}")
                print(f"Total Seats: {seat_info['total_seats']}")
                print("\n[SCREEN]")
                print("="*50)
                
                seat_map = seat_info['seat_map']
                for row in sorted(seat_map.keys()):
                    row_display = f"Row {row}: "
                    for seat_num in sorted(seat_map[row].keys()):
                        status = seat_map[row][seat_num]
                        if status == 'Available':
                            row_display += f"[{seat_num:2}] "
                        else:
                            row_display += f"[XX] "
                    print(row_display)
                
                print("\nLegend: [XX] = Booked, [Number] = Available")
                
                # Ask if user wants to book seats
                book_choice = input("\nDo you want to book seats for this show? (y/n): ")
                if book_choice.lower() == 'y':
                    self.book_with_seat_selection(selected_theatre, selected_movie, selected_show_time, seat_info)
                
            except ValueError:
                print("Invalid input!")
    def book_with_seat_selection(self, theatre, movie, show_time, seat_info):
        """Handle seat selection and booking"""
        selected_seats = []
        seat_map = seat_info['seat_map'].copy()  # Make a copy to avoid modifying original
        
        print("\nSelect your seats:")
        print("- Enter one seat at a time (format: A1, B5, etc.)")
        print("- Or enter multiple seats separated by commas (A1,B2,C3)")
        print("- Type 'done' when finished, 'clear' to clear selection, or 'back' to return")
        
        while True:
            if selected_seats:
                selected_display = ", ".join([f"{row}{num}" for row, num in selected_seats])
                print(f"\nCurrently selected: {selected_display} ({len(selected_seats)} seats)")
            
            seat_input = input("Enter seat(s): ").upper().strip()
            
            if seat_input == 'BACK':
                return
            elif seat_input == 'CLEAR':
                selected_seats = []
                # Reset seat map
                seat_map = seat_info['seat_map'].copy()
                print("Selection cleared!")
                continue
            elif seat_input == 'DONE':
                if selected_seats:
                    break
                else:
                    print("Please select at least one seat!")
                    continue
            
            # Handle multiple seats separated by commas
            if ',' in seat_input:
                seat_list = [seat.strip() for seat in seat_input.split(',')]
            else:
                seat_list = [seat_input]
            
            # Process each seat
            for seat in seat_list:
                if not seat:  # Skip empty strings
                    continue
                    
                # Parse seat input (e.g., A1, B10)
                if len(seat) >= 2:
                    row = seat[0]
                    try:
                        seat_num = int(seat[1:])
                        
                        if row in seat_map and seat_num in seat_map[row]:
                            if seat_map[row][seat_num] == 'Available':
                                if (row, seat_num) not in selected_seats:
                                    selected_seats.append((row, seat_num))
                                    seat_map[row][seat_num] = 'Selected'
                                    print(f"Selected seat {row}{seat_num}")
                                else:
                                    print(f"Seat {row}{seat_num} already selected!")
                            else:
                                print(f"Seat {row}{seat_num} is not available!")
                        else:
                            print(f"Invalid seat {row}{seat_num}!")
                    except ValueError:
                        print(f"Invalid seat format: {seat}! Use format like A1, B5")
                else:
                    print(f"Invalid seat format: {seat}! Use format like A1, B5")
        
        # Confirm booking
        while True:
            total_cost = movie['ticket_price'] * len(selected_seats)
            selected_display = ", ".join([f"{row}{num}" for row, num in selected_seats])
            print(f"\nBooking Summary:")
            print(f"Theatre: {theatre['name']}")
            print(f"Movie: {movie['title']}")
            print(f"Show Time: {show_time}")
            print(f"Selected Seats: {selected_display}")
            print(f"Number of Seats: {len(selected_seats)}")
            print(f"Original Total: ${total_cost}")
            #Get current loyalty points
            current_points=self.user.get_loyalty_points(self.current_user['id'])
            print(f"Your Loyality Points: {current_points}")
            points_to_redeem=0
            final_cost=total_cost
            # Ask if user wants to redeem points
            if current_points>=100:
                max_redeemable=min(current_points//100, int(total_cost//10)) # Can't redeem more than ticket cost
                redeem_choice=input(f"\nDo you want to redeem your points for a discount? (y/n):").lower().strip()
                if redeem_choice in ['y','yes']:
                    print(f"\nYou have {current_points} points available.")
                    print(f"Each 100 points=$10 discount")
                    print(f"You can redeem up to {max_redeemable*100} points (${max_redeemable*10} discount)")
                    try:
                        sets_to_redeem=input(f"How many sets of 100 points would you like to redeem? (0-{max_redeemable}): ").strip()
                        sets_to_redeem=int(sets_to_redeem)
                        if 0<= sets_to_redeem <=max_redeemable:
                            points_to_redeem=sets_to_redeem*100
                            discount=sets_to_redeem*10
                            final_cost=total_cost-discount
                            print(f"\nDiscount Applied: ${discount}")
                            print(f"Points to be Redeemed: {points_to_redeem}")
                            print(f"Final Total: ${final_cost}")
                        else:
                            print("Invalid points amount! No points will be redeemed")
                    except ValueError:
                        print("Invalid input! No points will be redeemed.")
            else:
                print(f"\nYou need at least 100 points to get a discount. You currently have {current_points} points.")            
            confirm = input("\nConfirm booking? (y/n/back): ")
            if confirm.lower() == 'back':
                return
            elif confirm.lower() in ['y', 'yes']:
                if self.user.book_specific_seats_with_points(
                    self.current_user['id'], movie['id'], theatre['id'], 
                    show_time, selected_seats, points_to_redeem
                ):
                    print("Tickets booked successfully!")
                    points_earned = int(final_cost / 10)
                    print(f"Amount Paid: ${final_cost}")
                    print(f"You earned {points_earned} new loyalty points!")
                    if points_to_redeem>0:
                        print(f"Points Redeemed {points_to_redeem} points for ${points_to_redeem//10} discount!")
                        print(f"Discount Received: ${points_to_redeem//10}")
                    # Update current user's points in session
                    self.current_user['loyalty_points']=self.user.get_loyalty_points(self.current_user['id'])    
                    input("Press Enter to continue...")
                else:
                    print("Booking failed!")
                    input("Press Enter to continue...")
                return
            elif confirm.lower() in ['n', 'no']:
                print("Booking cancelled.")
                return
            else:
                print("Please enter 'y', 'n', or 'back'")     
if __name__ == "__main__":
    app = CinePredicta()
    app.main_menu()