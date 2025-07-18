"""
Database migration utilities for PostForge
Handles automatic database schema updates on app startup
"""

import sqlite3
import os
from flask import current_app
from app import db


def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    try:
        # Get database path
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri or not db_uri.startswith('sqlite:///'):
            return False
            
        db_path = db_uri.replace('sqlite:///', '')
        
        # Convert relative path to absolute
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
            
        if not os.path.exists(db_path):
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [column[1] for column in cursor.fetchall()]
        
        conn.close()
        return column_name in columns
        
    except Exception as e:
        print(f"Error checking column existence: {e}")
        return False


def run_migrations():
    """Run all necessary database migrations"""
    try:
        print("🔄 Checking database migrations...")
        
        # Get database path
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not db_uri or not db_uri.startswith('sqlite:///'):
            print("❌ No SQLite database configured")
            return False
            
        db_path = db_uri.replace('sqlite:///', '')
        
        # Convert relative path to absolute
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)
            
        print(f"📁 Database path: {db_path}")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"📁 Database path is absolute: {os.path.isabs(db_path)}")
        
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            print(f"📁 Database directory created/verified: {db_dir}")
            print(f"📁 Directory exists: {os.path.exists(db_dir)}")
            print(f"📁 Directory is writable: {os.access(db_dir, os.W_OK)}")
        else:
            print("📁 Database is in current directory")
        
        # Create all tables first
        try:
            db.create_all()
            print("✅ Database tables created/verified")
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            # Try direct sqlite3 creation if SQLAlchemy fails
            print("🔄 Attempting direct sqlite3 database initialization...")
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                conn.execute("CREATE TABLE IF NOT EXISTS _init (id INTEGER)")
                conn.commit()
                conn.close()
                print("✅ Database initialized via direct sqlite3")
                # Try SQLAlchemy again
                db.create_all()
                print("✅ Database tables created after initialization")
            except Exception as e2:
                print(f"❌ Direct sqlite3 initialization failed: {e2}")
                return False
        
        # Verify database file exists after creation
        if not os.path.exists(db_path):
            print(f"❌ Database file not found after creation: {db_path}")
            print("🔄 Attempting to create database file with table creation...")
            # Force database creation by creating a table and inserting data
            try:
                with db.engine.connect() as connection:
                    # Create a temporary table to force file creation
                    connection.execute(db.text("CREATE TABLE IF NOT EXISTS _migration_test (id INTEGER PRIMARY KEY)"))
                    connection.execute(db.text("INSERT OR IGNORE INTO _migration_test (id) VALUES (1)"))
                    connection.execute(db.text("SELECT * FROM _migration_test"))
                    connection.commit()
                
                # Verify the file was created
                if os.path.exists(db_path):
                    print("✅ Database file created via table creation")
                    # Clean up the test table
                    try:
                        with db.engine.connect() as connection:
                            connection.execute(db.text("DROP TABLE _migration_test"))
                            connection.commit()
                    except:
                        pass
                else:
                    print("❌ Database file still not found after table creation")
                    # Try using sqlite3 directly as last resort
                    print("🔄 Attempting direct sqlite3 database creation...")
                    try:
                        import sqlite3
                        conn = sqlite3.connect(db_path)
                        conn.execute("CREATE TABLE IF NOT EXISTS _test (id INTEGER)")
                        conn.commit()
                        conn.close()
                        if os.path.exists(db_path):
                            print("✅ Database file created via direct sqlite3")
                        else:
                            print("❌ Failed to create database file with all methods")
                            return False
                    except Exception as e:
                        print(f"❌ Direct sqlite3 creation failed: {e}")
                        return False
            except Exception as e:
                print(f"❌ Failed to create database file: {e}")
                return False
        else:
            print(f"✅ Database file exists: {db_path}")
        
        # Verify database connection
        try:
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT 1"))
                result.fetchone()
            print("✅ Database connection verified")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        # Use SQLAlchemy for migrations to avoid path issues
        migrations_applied = 0
        
        # Check and add columns using SQLAlchemy
        try:
            # Check if columns exist by attempting to query them
            with db.engine.connect() as connection:
                # Start a transaction for all migrations
                trans = connection.begin()
                
                try:
                    # Check posts table columns
                    try:
                        connection.execute(db.text("SELECT share_token FROM posts LIMIT 1"))
                        print("✅ share_token column already exists")
                    except Exception:
                        print("🔄 Adding share_token column to posts table...")
                        connection.execute(db.text("ALTER TABLE posts ADD COLUMN share_token VARCHAR(64)"))
                        migrations_applied += 1
                        print("✅ Added share_token column")
                    
                    try:
                        connection.execute(db.text("SELECT is_shared FROM posts LIMIT 1"))
                        print("✅ is_shared column already exists")
                    except Exception:
                        print("🔄 Adding is_shared column to posts table...")
                        connection.execute(db.text("ALTER TABLE posts ADD COLUMN is_shared BOOLEAN DEFAULT 0"))
                        migrations_applied += 1
                        print("✅ Added is_shared column")
                    
                    # Create unique index for share_token
                    try:
                        connection.execute(db.text("CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_share_token ON posts(share_token)"))
                        print("✅ Created/verified unique index for share_token")
                    except Exception as e:
                        if 'already exists' not in str(e):
                            print(f"⚠️  Warning: Could not create index: {e}")
                    
                    # Check images table columns
                    try:
                        connection.execute(db.text("SELECT file_path FROM images LIMIT 1"))
                        print("✅ file_path column already exists")
                    except Exception:
                        print("🔄 Adding file_path column to images table...")
                        connection.execute(db.text("ALTER TABLE images ADD COLUMN file_path VARCHAR(500)"))
                        migrations_applied += 1
                        print("✅ Added file_path column")
                    
                    try:
                        connection.execute(db.text("SELECT file_size FROM images LIMIT 1"))
                        print("✅ file_size column already exists")
                    except Exception:
                        print("🔄 Adding file_size column to images table...")
                        connection.execute(db.text("ALTER TABLE images ADD COLUMN file_size INTEGER"))
                        migrations_applied += 1
                        print("✅ Added file_size column")
                    
                    try:
                        connection.execute(db.text("SELECT mime_type FROM images LIMIT 1"))
                        print("✅ mime_type column already exists")
                    except Exception:
                        print("🔄 Adding mime_type column to images table...")
                        connection.execute(db.text("ALTER TABLE images ADD COLUMN mime_type VARCHAR(100)"))
                        migrations_applied += 1
                        print("✅ Added mime_type column")
                    
                    # Commit all migrations
                    trans.commit()
                    print("✅ All migrations committed successfully")
                    
                except Exception as e:
                    trans.rollback()
                    print(f"❌ Error during migrations, rolling back: {e}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error during migrations: {e}")
            return False
        
        if migrations_applied > 0:
            print(f"✅ Applied {migrations_applied} database migrations successfully")
        else:
            print("✅ Database is up to date, no migrations needed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False


def verify_database_schema():
    """Verify that all required columns exist"""
    try:
        required_columns = {
            'posts': ['share_token', 'is_shared'],
            'images': ['file_path', 'file_size', 'mime_type']
        }
        
        for table, columns in required_columns.items():
            for column in columns:
                if not check_column_exists(table, column):
                    print(f"❌ Missing column: {table}.{column}")
                    return False
        
        print("✅ Database schema verification passed")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying database schema: {e}")
        return False