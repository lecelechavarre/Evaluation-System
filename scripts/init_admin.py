import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from file_store import FileStore
from auth import AuthManager
from config import USERS_FILE
import getpass


def init_admin():
    """Create default admin account."""
    print("=" * 60)
    print("Performance Evaluation System - Admin Initialization")
    print("=" * 60)
    
    user_store = FileStore(USERS_FILE)
    auth_manager = AuthManager(user_store)
    
    # Check if admin already exists
    existing_admins = user_store.find_by(role='admin')
    if existing_admins:
        print("\n⚠️  Admin account(s) already exist:")
        for admin in existing_admins:
            print(f"   - {admin['username']} ({admin['full_name']})")
        
        response = input("\nCreate another admin account? (y/n): ")
        if response.lower() != 'y':
            print("Initialization cancelled.")
            return
    
    print("\nCreate Admin Account")
    print("-" * 60)
    
    username = input("Username (default: admin): ").strip() or "admin"
    password = getpass.getpass("Password (default: Admin@123): ") or "Admin@123"
    full_name = input("Full Name (default: System Administrator): ").strip() or "System Administrator"
    email = input("Email (default: admin@example.com): ").strip() or "admin@example.com"
    
    try:
        user_id = auth_manager.create_user(
            username=username,
            password=password,
            role='admin',
            full_name=full_name,
            email=email
        )
        
        if user_id:
            print(f"\n✅ Admin account created successfully!")
            print(f"   Username: {username}")
            print(f"   User ID: {user_id}")
            print("\n⚠️  Please change the password after first login!")
        else:
            print("\n❌ Failed to create admin account. Username may already exist.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == '__main__':
    init_admin()
