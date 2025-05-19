import sqlite3
from datetime import datetime

def init_database():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # Create stores table
    conn.execute('''CREATE TABLE IF NOT EXISTS stores 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         category TEXT NOT NULL,
         floor INTEGER NOT NULL,
         area REAL NOT NULL,
         owner_name TEXT,
         owner_phone TEXT,
         owner_email TEXT UNIQUE,
         rent_start_date TEXT,
         rent_end_date TEXT,
         monthly_rent REAL,
         status TEXT DEFAULT 'Active',
         created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT NOT NULL,
         email TEXT UNIQUE NOT NULL,
         password TEXT NOT NULL,
         role TEXT DEFAULT 'user',
         phone TEXT,
         created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create events table
    conn.execute('''CREATE TABLE IF NOT EXISTS events 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT NOT NULL,
         description TEXT,
         start_date TEXT NOT NULL,
         end_date TEXT NOT NULL,
         location TEXT NOT NULL,
         status TEXT DEFAULT 'Upcoming',
         created_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create maintenance table
    conn.execute('''CREATE TABLE IF NOT EXISTS maintenance 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         store_id INTEGER NOT NULL,
         issue_type TEXT NOT NULL,
         description TEXT NOT NULL,
         reported_date TEXT NOT NULL,
         status TEXT DEFAULT 'Pending',
         resolved_date TEXT,
         created_at TEXT DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (store_id) REFERENCES stores(id) ON DELETE CASCADE)''')
    
    # Create audit_log table for tracking changes
    conn.execute('''CREATE TABLE IF NOT EXISTS audit_log 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         table_name TEXT NOT NULL,
         record_id INTEGER NOT NULL,
         action TEXT NOT NULL,
         old_values TEXT,
         new_values TEXT,
         user_id INTEGER,
         timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
         FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Insert default admin user if not exists
    try:
        conn.execute("""
            INSERT INTO users (name, email, password, role)
            SELECT 'Admin', 'admin@mall.com', 'admin', 'admin'
            WHERE NOT EXISTS (
                SELECT 1 FROM users WHERE email = 'admin@mall.com'
            )
        """)
        conn.commit()
    except sqlite3.IntegrityError:
        print("Admin user already exists")
    
    # Create indexes for better performance
    conn.execute('CREATE INDEX IF NOT EXISTS idx_stores_name ON stores(name)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_stores_category ON stores(category)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_events_dates ON events(start_date, end_date)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_store ON maintenance(store_id)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance(status)')
    
    print("Tables and indexes created successfully")
    conn.close()

def create_triggers():
    conn = sqlite3.connect('database.db')
    
    # Trigger for stores table
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS stores_audit_trigger
        AFTER UPDATE ON stores
        BEGIN
            INSERT INTO audit_log (table_name, record_id, action, old_values, new_values)
            VALUES (
                'stores',
                NEW.id,
                'UPDATE',
                json_object(
                    'name', OLD.name,
                    'category', OLD.category,
                    'floor', OLD.floor,
                    'area', OLD.area,
                    'status', OLD.status
                ),
                json_object(
                    'name', NEW.name,
                    'category', NEW.category,
                    'floor', NEW.floor,
                    'area', NEW.area,
                    'status', NEW.status
                )
            );
        END;
    ''')
    
    # Trigger for events table
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS events_audit_trigger
        AFTER UPDATE ON events
        BEGIN
            INSERT INTO audit_log (table_name, record_id, action, old_values, new_values)
            VALUES (
                'events',
                NEW.id,
                'UPDATE',
                json_object(
                    'title', OLD.title,
                    'status', OLD.status,
                    'start_date', OLD.start_date,
                    'end_date', OLD.end_date
                ),
                json_object(
                    'title', NEW.title,
                    'status', NEW.status,
                    'start_date', NEW.start_date,
                    'end_date', NEW.end_date
                )
            );
        END;
    ''')
    
    # Trigger for maintenance table
    conn.execute('''
        CREATE TRIGGER IF NOT EXISTS maintenance_audit_trigger
        AFTER UPDATE ON maintenance
        BEGIN
            INSERT INTO audit_log (table_name, record_id, action, old_values, new_values)
            VALUES (
                'maintenance',
                NEW.id,
                'UPDATE',
                json_object(
                    'status', OLD.status,
                    'resolved_date', OLD.resolved_date
                ),
                json_object(
                    'status', NEW.status,
                    'resolved_date', NEW.resolved_date
                )
            );
        END;
    ''')
    
    print("Triggers created successfully")
    conn.close()

if __name__ == '__main__':
    init_database()
    create_triggers()
    print("Database initialization completed") 