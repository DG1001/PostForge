#!/usr/bin/env python3
"""
Standalone database migration script for PostForge
Can be run independently to migrate existing databases
"""

import os
import sys
import sqlite3
from pathlib import Path

def migrate_database():
    """Migrate existing database to latest schema"""
    
    # Find database file
    db_paths = [
        'instance/linkedin_posts.db',
        'linkedin_posts.db',
        'app/instance/linkedin_posts.db',
        '/app/instance/linkedin_posts.db'
    ]
    
    db_path = None
    for path in db_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No database file found")
        return False
    
    print(f"📁 Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(posts)")
        post_columns = [column[1] for column in cursor.fetchall()]
        print(f"📊 Posts table columns: {post_columns}")
        
        cursor.execute("PRAGMA table_info(images)")
        image_columns = [column[1] for column in cursor.fetchall()]
        print(f"📊 Images table columns: {image_columns}")
        
        migrations_applied = 0
        
        # Migrate posts table
        if 'share_token' not in post_columns:
            print("🔄 Adding share_token column...")
            cursor.execute('ALTER TABLE posts ADD COLUMN share_token VARCHAR(64)')
            migrations_applied += 1
            print("✅ Added share_token column")
        
        if 'is_shared' not in post_columns:
            print("🔄 Adding is_shared column...")
            cursor.execute('ALTER TABLE posts ADD COLUMN is_shared BOOLEAN DEFAULT 0')
            migrations_applied += 1
            print("✅ Added is_shared column")
        
        # Create unique index
        try:
            cursor.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_posts_share_token ON posts(share_token)')
            print("✅ Created unique index for share_token")
        except sqlite3.OperationalError as e:
            if 'already exists' not in str(e):
                print(f"⚠️  Warning: Could not create index: {e}")
        
        # Migrate images table
        if 'file_path' not in image_columns:
            print("🔄 Adding file_path column...")
            cursor.execute('ALTER TABLE images ADD COLUMN file_path VARCHAR(500)')
            migrations_applied += 1
            print("✅ Added file_path column")
            
        if 'file_size' not in image_columns:
            print("🔄 Adding file_size column...")
            cursor.execute('ALTER TABLE images ADD COLUMN file_size INTEGER')
            migrations_applied += 1
            print("✅ Added file_size column")
            
        if 'mime_type' not in image_columns:
            print("🔄 Adding mime_type column...")
            cursor.execute('ALTER TABLE images ADD COLUMN mime_type VARCHAR(100)')
            migrations_applied += 1
            print("✅ Added mime_type column")
        
        conn.commit()
        conn.close()
        
        if migrations_applied > 0:
            print(f"🎉 Applied {migrations_applied} migrations successfully!")
        else:
            print("✅ Database is already up to date")
            
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass
        return False

if __name__ == '__main__':
    print("🚀 PostForge Database Migration")
    print("=" * 40)
    
    if migrate_database():
        print("✅ Migration completed successfully!")
        sys.exit(0)
    else:
        print("❌ Migration failed!")
        sys.exit(1)