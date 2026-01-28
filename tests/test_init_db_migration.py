import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from init_db import migrate_database, db
from flask import Flask

class TestMigration(unittest.TestCase):
    def test_dynamic_migration(self):
        # Create a real app to satisfy db.engine access
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        db.init_app(app)

        # Mock inspector
        mock_inspector = MagicMock()
        # Mock table names: users exists
        mock_inspector.get_table_names.return_value = ['users', 'companies']

        # Mock columns: users has only id, companies has id and name
        # Missing in users: username, password_hash, etc.
        # Missing in companies: user_id, address, etc.
        def get_columns_side_effect(table_name):
            if table_name == 'users':
                return [{'name': 'id'}]
            if table_name == 'companies':
                return [{'name': 'id'}, {'name': 'name'}]
            return []

        mock_inspector.get_columns.side_effect = get_columns_side_effect
        mock_inspector.get_indexes.return_value = []

        with patch('init_db.inspect', return_value=mock_inspector), \
             patch.object(db.session, 'execute') as mock_execute, \
             patch.object(db.session, 'commit'):

            migrate_database(app)

            # Collect executed SQL statements
            executed_sql = []
            for call in mock_execute.call_args_list:
                args, _ = call
                sql_obj = args[0]
                executed_sql.append(str(sql_obj))

            # Verification
            print("\nExecuted SQL Statements:")
            for sql in executed_sql:
                print(f"- {sql}")

            # Check for specific missing columns

            # 1. Manual migrations (companies.user_id is in manual list)
            # Since companies is in our mock, this should trigger.
            companies_user_id_sql = [s for s in executed_sql if "ALTER TABLE companies ADD COLUMN IF NOT EXISTS user_id" in s]
            self.assertTrue(len(companies_user_id_sql) >= 1, "Manual migration for companies.user_id missing")

            # Verify it wasn't executed twice (once manual, once dynamic)
            # Actually, since we mocked inspector to always say it's missing, if we didn't have 'handled_columns' check, it would run twice.
            # But the SQL string is identical? No, manual SQL might differ slightly from dynamic SQL.
            # Manual: ALTER TABLE companies ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id)
            # Dynamic: ALTER TABLE companies ADD COLUMN IF NOT EXISTS user_id VARCHAR(36) REFERENCES users(id) (generated)
            # They look identical.
            # But we can check if it appears twice.
            self.assertEqual(len(companies_user_id_sql), 1, "companies.user_id migration executed multiple times (should be handled once)")

            # 2. Dynamic migrations for columns NOT in manual list
            # users.username
            self.assertTrue(any("ALTER TABLE users ADD COLUMN username VARCHAR(100)" in sql for sql in executed_sql), "Dynamic migration for users.username missing")

            # companies.address
            self.assertTrue(any("ALTER TABLE companies ADD COLUMN address TEXT DEFAULT ''" in sql for sql in executed_sql), "Dynamic migration for companies.address missing")

if __name__ == '__main__':
    unittest.main()
