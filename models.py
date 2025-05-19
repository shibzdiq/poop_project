from datetime import datetime
from typing import Optional, List

class Store:
    def __init__(self, id: Optional[int] = None, name: str = "", category: str = "",
                 floor: int = 1, area: float = 0.0, status: str = "Active"):
        self.id = id
        self.name = name
        self.category = category
        self.floor = floor
        self.area = area
        self.status = status
        self.rental = None  # One-to-One relationship with Rental

    def add(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                INSERT INTO stores (name, category, floor, area, status)
                VALUES (?, ?, ?, ?, ?)
            """, (self.name, self.category, self.floor, self.area, self.status))
            db_connection.commit()
            self.id = cursor.lastrowid
            return True
        except Exception as e:
            print(f"Error adding store: {str(e)}")
            return False

    def edit(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                UPDATE stores 
                SET name=?, category=?, floor=?, area=?, status=?
                WHERE id=?
            """, (self.name, self.category, self.floor, self.area, self.status, self.id))
            db_connection.commit()
            return True
        except Exception as e:
            print(f"Error editing store: {str(e)}")
            return False

    def delete(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("DELETE FROM stores WHERE id=?", (self.id,))
            db_connection.commit()
            return True
        except Exception as e:
            print(f"Error deleting store: {str(e)}")
            return False

    @staticmethod
    def search(db_connection, search_term: str, search_type: str) -> List['Store']:
        try:
            cursor = db_connection.cursor()
            if search_type == 'name':
                cursor.execute("SELECT * FROM stores WHERE name LIKE ?", (f'%{search_term}%',))
            elif search_type == 'category':
                cursor.execute("SELECT * FROM stores WHERE category LIKE ?", (f'%{search_term}%',))
            else:
                cursor.execute("SELECT * FROM stores")
            
            stores = []
            for row in cursor.fetchall():
                store = Store(
                    id=row[0],
                    name=row[1],
                    category=row[2],
                    floor=row[3],
                    area=row[4],
                    status=row[5]
                )
                stores.append(store)
            return stores
        except Exception as e:
            print(f"Error searching stores: {str(e)}")
            return []

class User:
    def __init__(self, id: Optional[int] = None, name: str = "", email: str = "",
                 password: str = "", role: str = "user", phone: str = ""):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
        self.phone = phone

    def login(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("SELECT * FROM users WHERE email=? AND password=?", 
                         (self.email, self.password))
            user = cursor.fetchone()
            return user is not None
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False

    def register(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                INSERT INTO users (name, email, password, role, phone)
                VALUES (?, ?, ?, ?, ?)
            """, (self.name, self.email, self.password, self.role, self.phone))
            db_connection.commit()
            self.id = cursor.lastrowid
            return True
        except Exception as e:
            print(f"Error registering user: {str(e)}")
            return False

class Event:
    def __init__(self, id: Optional[int] = None, title: str = "", description: str = "",
                 start_date: str = "", end_date: str = "", location: str = "",
                 status: str = "Upcoming"):
        self.id = id
        self.title = title
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.location = location
        self.status = status

    def create(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                INSERT INTO events (title, description, start_date, end_date, location, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.title, self.description, self.start_date, self.end_date, 
                 self.location, self.status))
            db_connection.commit()
            self.id = cursor.lastrowid
            return True
        except Exception as e:
            print(f"Error creating event: {str(e)}")
            return False

    def update(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                UPDATE events 
                SET title=?, description=?, start_date=?, end_date=?, location=?, status=?
                WHERE id=?
            """, (self.title, self.description, self.start_date, self.end_date,
                 self.location, self.status, self.id))
            db_connection.commit()
            return True
        except Exception as e:
            print(f"Error updating event: {str(e)}")
            return False

    def cancel(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("UPDATE events SET status='Cancelled' WHERE id=?", (self.id,))
            db_connection.commit()
            self.status = 'Cancelled'
            return True
        except Exception as e:
            print(f"Error cancelling event: {str(e)}")
            return False

class Maintenance:
    def __init__(self, id: Optional[int] = None, store_id: int = 0, issue_type: str = "",
                 description: str = "", reported_date: str = "", status: str = "Pending",
                 resolved_date: Optional[str] = None):
        self.id = id
        self.store_id = store_id
        self.issue_type = issue_type
        self.description = description
        self.reported_date = reported_date
        self.status = status
        self.resolved_date = resolved_date

    def report(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                INSERT INTO maintenance (store_id, issue_type, description, reported_date, status)
                VALUES (?, ?, ?, ?, ?)
            """, (self.store_id, self.issue_type, self.description, 
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.status))
            db_connection.commit()
            self.id = cursor.lastrowid
            return True
        except Exception as e:
            print(f"Error reporting maintenance issue: {str(e)}")
            return False

    def update_status(self, db_connection, new_status: str) -> bool:
        try:
            cursor = db_connection.cursor()
            resolved_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if new_status == 'Resolved' else None
            cursor.execute("""
                UPDATE maintenance 
                SET status=?, resolved_date=?
                WHERE id=?
            """, (new_status, resolved_date, self.id))
            db_connection.commit()
            self.status = new_status
            self.resolved_date = resolved_date
            return True
        except Exception as e:
            print(f"Error updating maintenance status: {str(e)}")
            return False

class Rental:
    def __init__(self, store_id: int = 0, owner_name: str = "", owner_phone: str = "",
                 owner_email: str = "", rent_start_date: str = "", rent_end_date: str = "",
                 monthly_rent: float = 0.0):
        self.store_id = store_id
        self.owner_name = owner_name
        self.owner_phone = owner_phone
        self.owner_email = owner_email
        self.rent_start_date = rent_start_date
        self.rent_end_date = rent_end_date
        self.monthly_rent = monthly_rent

    def create_contract(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                UPDATE stores 
                SET owner_name=?, owner_phone=?, owner_email=?, 
                    rent_start_date=?, rent_end_date=?, monthly_rent=?
                WHERE id=?
            """, (self.owner_name, self.owner_phone, self.owner_email,
                 self.rent_start_date, self.rent_end_date, self.monthly_rent,
                 self.store_id))
            db_connection.commit()
            return True
        except Exception as e:
            print(f"Error creating rental contract: {str(e)}")
            return False

    def update_contract(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                UPDATE stores 
                SET owner_name=?, owner_phone=?, owner_email=?, 
                    rent_start_date=?, rent_end_date=?, monthly_rent=?
                WHERE id=?
            """, (self.owner_name, self.owner_phone, self.owner_email,
                 self.rent_start_date, self.rent_end_date, self.monthly_rent,
                 self.store_id))
            db_connection.commit()
            return True
        except Exception as e:
            print(f"Error updating rental contract: {str(e)}")
            return False

    def terminate_contract(self, db_connection) -> bool:
        try:
            cursor = db_connection.cursor()
            cursor.execute("""
                UPDATE stores 
                SET owner_name=NULL, owner_phone=NULL, owner_email=NULL,
                    rent_start_date=NULL, rent_end_date=NULL, monthly_rent=NULL
                WHERE id=?
            """, (self.store_id,))
            db_connection.commit()
            return True
        except Exception as e:
            print(f"Error terminating rental contract: {str(e)}")
            return False 