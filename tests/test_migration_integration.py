import unittest
import os
import sqlite3
from flask import Flask
from init_db import init_database, db
from sqlalchemy import text, inspect

class TestMigrationIntegration(unittest.TestCase):
    def setUp(self):
        self.db_path = 'test_migration.db'
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

        # Create an "old" database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Create users table with MISSING columns (only id)
        # This simulates a database from a very old version
        cursor.execute("CREATE TABLE users (id VARCHAR(36) PRIMARY KEY)")
        # Insert a dummy user to ensure data is preserved
        cursor.execute("INSERT INTO users (id) VALUES ('user1')")
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_migration_adds_columns(self):
        app = Flask(__name__)
        # Use absolute path for sqlite to avoid CWD issues
        db_abspath = os.path.abspath(self.db_path)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_abspath}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {} # Reset options

        # Run initialization (create_all + migrate)
        try:
            init_database(app)
        except Exception as e:
            self.fail(f"init_database failed: {e}")

        with app.app_context():
            # Verify columns were added
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('users')]

            print(f"Columns in users table: {columns}")

            required_columns = ['username', 'password_hash', 'role', 'created_at', 'is_active']
            for col in required_columns:
                self.assertIn(col, columns, f"Column '{col}' was not added to users table")

            # Verify data preservation
            result = db.session.execute(text("SELECT id FROM users WHERE id='user1'")).scalar()
            self.assertEqual(result, 'user1', "Existing data was lost!")

            # Check if default values were applied for new columns
            # The migration adds columns with defaults.
            # SQLite applies defaults to existing rows when adding columns.

            # Check role (default 'user')
            role = db.session.execute(text("SELECT role FROM users WHERE id='user1'")).scalar()
            self.assertEqual(role, 'user', "Default value for role not applied")

            # Check is_active (default True/1)
            is_active = db.session.execute(text("SELECT is_active FROM users WHERE id='user1'")).scalar()
            # SQLite stores boolean as 1/0
            self.assertTrue(is_active in [1, True], f"Default value for is_active not applied: {is_active}")

if __name__ == '__main__':
    unittest.main()
