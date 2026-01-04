# create_test_data.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.users.models import Utilisateur
from apps.publications.models import Publication
from apps.groups.models import Groupe
from django.contrib.auth.hashers import make_password

# Create test user
user = Utilisateur.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User'
)

# Create test publication
pub = Publication.objects.create(
    title='Test Publication',
    abstract='This is a test abstract',
    status='published',
    publication_type='article',
    main_author=user
)

# Create test group
group = Groupe.objects.create(
    name='Test Group',
    creator=user
)

print("✅ Created test data!")
print(f"Users: {Utilisateur.objects.count()}")
print(f"Publications: {Publication.objects.count()}")
print(f"Groups: {Groupe.objects.count()}")
