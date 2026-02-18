import os
import sys
import django

# Add the src directory to python path
project_root = os.getcwd()
sys.path.append(os.path.join(project_root, 'src'))

# Configure settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    username = 'admin'
    email = 'admin@example.com'
    password = 'adminpass'
    
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser '{username}'...")
        try:
            User.objects.create_superuser(username, email, password)
            print(f"Superuser '{username}' created successfully.")
        except Exception as e:
            print(f"Error creating superuser: {e}")
            sys.exit(1)
    else:
        print(f"Superuser '{username}' already exists.")

if __name__ == '__main__':
    create_admin()
