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
            
        # Create database file if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create all tables first
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Check if database file exists
        if not os.path.exists(db_path):
            print("❌ Database file not found after creation")
            return False
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        migrations_applied = 0
        
        # Migration 1: Add share_token and is_shared columns to posts table
        if not check_column_exists('posts', 'share_token'):
            print("🔄 Adding share_token column to posts table...")
            cursor.execute('ALTER TABLE posts ADD COLUMN share_token VARCHAR(64)')
            migrations_applied += 1
            print("✅ Added share_token column")
        
        if not check_column_exists('posts', 'is_shared'):
            print("🔄 Adding is_shared column to posts table...")
            cursor.execute('ALTER TABLE posts ADD COLUMN is_shared BOOLEAN DEFAULT 0')
            migrations_applied += 1
            print("✅ Added is_shared column")
        
        # Create unique index for share_token if it doesn't exist
        try:
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_share_token ON posts(share_token)')
            print("✅ Created/verified unique index for share_token")
        except sqlite3.OperationalError as e:
            if 'already exists' not in str(e):
                print(f"⚠️  Warning: Could not create index: {e}")
        
        # Migration 2: Check if images table has required columns
        if not check_column_exists('images', 'file_path'):
            print("🔄 Adding file_path column to images table...")
            cursor.execute('ALTER TABLE images ADD COLUMN file_path VARCHAR(500)')
            migrations_applied += 1
            print("✅ Added file_path column")
            
        if not check_column_exists('images', 'file_size'):
            print("🔄 Adding file_size column to images table...")
            cursor.execute('ALTER TABLE images ADD COLUMN file_size INTEGER')
            migrations_applied += 1
            print("✅ Added file_size column")
            
        if not check_column_exists('images', 'mime_type'):
            print("🔄 Adding mime_type column to images table...")
            cursor.execute('ALTER TABLE images ADD COLUMN mime_type VARCHAR(100)')
            migrations_applied += 1
            print("✅ Added mime_type column")
        
        conn.commit()
        conn.close()
        
        if migrations_applied > 0:
            print(f"✅ Applied {migrations_applied} database migrations successfully")
        else:
            print("✅ Database is up to date, no migrations needed")
            
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
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