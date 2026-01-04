import os
import django
import random
from faker import Faker
from django.utils import timezone

# -- Django Setup --
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# -- Model Imports --
from django.contrib.auth import get_user_model
from apps.groups.models import Groupe
from apps.posts.models import Post
from apps.comments.models import Commentaire
from apps.publications.models import Publication

# -- Database Imports --
from config.mongodb import get_collection as get_mongo_collection
from apps.recommendations.neo4j_service import get_neo4j_driver
from apps.recommendations.neo4j_queries import RecommendationEngine

Utilisateur = get_user_model()
fake = Faker('fr_FR')

# --- Configuration ---
NUM_USERS = 25
NUM_GROUPS = 8
NUM_POSTS_PER_USER = 2
NUM_COMMENTS_PER_POST = 3
NUM_PUBLICATIONS_PER_USER = 1

# List of specific topics to use
TOPICS_LIST = ['Data', 'Science', 'Network', 'Development', 'Engineering', 'AI', 'Security', 'Cloud']

def clear_databases():
    """
    Clears all data. 
    IMPORTANT: Does NOT close the Neo4j driver, as it is needed for seeding.
    """
    # 1. Clear Neo4j
    print("1. Clearing Neo4j database...")
    driver = get_neo4j_driver()
    try:
        with driver.get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("   ✓ Neo4j cleared.")
    except Exception as e:
        print(f"   ✗ Error clearing Neo4j: {e}")
    # DO NOT CALL driver.close() HERE!

    # 2. Clear MongoDB
    print("2. Clearing MongoDB database...")
    collections_to_drop = ['publications', 'users', 'groups']
    for coll_name in collections_to_drop:
        try:
            collection = get_mongo_collection(coll_name)
            if collection:
                collection.drop()
        except Exception:
            pass
    print("   ✓ MongoDB cleared.")

    # 3. Clear SQL
    print("3. Clearing SQL database...")
    Commentaire.objects.all().delete()
    Post.objects.all().delete()
    Publication.objects.all().delete()
    Groupe.objects.all().delete()
    # We delete all users to ensure a clean slate for specific accounts
    Utilisateur.objects.all().delete()
    print("   ✓ SQL cleared.")

def seed_users():
    print("\n4. Seeding Users (This may take a moment for password hashing)...")
    users = []
    recommendation_engine = RecommendationEngine()

    # Specific Accounts
    specific_accounts = [
        ('sfn', True), ('amine', False), ('youssef', False), ('ayman', False)
    ]

    for username, is_superuser in specific_accounts:
        email = f"{username}@example.com"
        password = '1234'
        
        profile_data = {
            'first_name': username.capitalize(),
            'last_name': "Admin" if is_superuser else "Tester",
            'bio': "System Admin" if is_superuser else f"Tester {username}",
            'institution': "Admin HQ" if is_superuser else fake.company(),
            'department': "IT" if is_superuser else fake.job(),
            'research_interests': "Testing, Neo4j, Django",
        }

        try:
            # Create in Django SQL
            if is_superuser:
                user = Utilisateur.objects.create_superuser(username=username, email=email, password=password, **profile_data)
            else:
                user = Utilisateur.objects.create_user(username=username, email=email, password=password, **profile_data)
            
            users.append(user)
            
            # Sync to Neo4j
            try:
                if recommendation_engine.driver:
                    recommendation_engine.sync_user_to_neo4j(user.id, user.username, user.email)
                    print(f"   ✓ Created & Synced: {username}")
                else:
                    print(f"   ✓ Created SQL: {username} (Neo4j Driver missing)")
            except Exception as e:
                print(f"   ⚠ Created SQL: {username}, but Neo4j Sync Failed: {e}")

        except Exception as e:
            print(f"   ✗ FAILED to create {username}: {e}")

    # Random Users
    remaining_count = max(0, NUM_USERS - len(users))
    print(f"   ... Generating {remaining_count} random users ...")
    
    for i in range(remaining_count):
        try:
            username = f"{fake.user_name()}{random.randint(1, 10000)}"
            user = Utilisateur.objects.create_user(
                username=username,
                email=fake.email(),
                password='password',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                institution=fake.company()
            )
            users.append(user)
            
            # Sync to Neo4j
            if recommendation_engine.driver:
                recommendation_engine.sync_user_to_neo4j(user.id, user.username, user.email)
        except Exception:
            pass
            
    print(f"   ✓ Total {len(users)} users created.")
    return users

def seed_groups(users):
    print("\n5. Seeding Groups...")
    groups = []
    if not users: return groups

    admin_user = users[0] # sfn
    
    # Specific Admin Group
    try:
        g, _ = Groupe.objects.get_or_create(
            name="Groupe Administration", 
            defaults={'description': "Official Admin Group", 'creator': admin_user}
        )
        if hasattr(g, 'members'):
            g.members.add(*users[:4]) # Add specific users
        groups.append(g)
        print(f"   ✓ Created 'Groupe Administration'")
    except Exception as e:
        print(f"   ✗ Failed to create Admin Group: {e}")

    # Random Groups
    for _ in range(NUM_GROUPS - 1):
        try:
            creator = random.choice(users)
            group = Groupe.objects.create(
                name=f"{fake.company()} Group {random.randint(1,999)}",
                description=fake.paragraph(nb_sentences=2),
                creator=creator
            )
            if hasattr(group, 'members'):
                group.members.add(*random.sample(users, random.randint(1, 5)))
            groups.append(group)
        except Exception as e:
            pass
    
    print(f"   ✓ Total {len(groups)} groups created.")
    return groups

def seed_publications(users):
    print("\n6. Seeding Publications...")
    publications = []
    if not users: return publications

    rec_engine = RecommendationEngine()
    pub_coll = get_mongo_collection('publications')

    # Specific Doc (Using 'Engineering' and 'Development')
    admin_user = users[0]
    
    try:
        specific_keywords = ['Development', 'Engineering', 'Django']
        pub, _ = Publication.objects.get_or_create(
            title="Documentation Officielle",
            defaults={
                'abstract': "Technical documentation for the Research Platform architecture.", 
                'publication_date': timezone.now().date(),
                'main_author': admin_user 
            }
        )
        if hasattr(pub, 'authors'):
            pub.authors.add(admin_user)
        publications.append(pub)
        
        # Sync Specific Doc
        if pub_coll:
            pub_coll.insert_one({'title': pub.title, 'sql_id': pub.id, 'keywords': specific_keywords})
        if rec_engine.driver:
            rec_engine.sync_publication_to_neo4j(pub.id, pub.title, admin_user.id, specific_keywords)
    except Exception as e:
        print(f"   ✗ Failed specific publication: {e}")

    # Random Pubs
    for i in range(20):
        try:
            user = random.choice(users)
            
            # Select 2-3 random topics from our defined list
            random_topics = random.sample(TOPICS_LIST, k=random.randint(2, 3))

            p = Publication.objects.create(
                title=f"{random.choice(random_topics)}: {fake.catch_phrase()}",
                abstract=fake.paragraph(nb_sentences=3),
                publication_date=fake.date_of_birth(),
                main_author=user 
            )
            if hasattr(p, 'authors'):
                p.authors.add(user)
            publications.append(p)
            
            # Sync
            if pub_coll:
                pub_coll.insert_one({'title': p.title, 'sql_id': p.id, 'keywords': random_topics})
            if rec_engine.driver:
                rec_engine.sync_publication_to_neo4j(p.id, p.title, user.id, random_topics)
        except Exception as e:
            if i == 0: print(f"   ✗ Failed random publication: {e}")
            pass

    print(f"   ✓ Total {len(publications)} publications created.")
    return publications

def seed_social(users, publications, groups):
    print("\n7. Seeding Social Graph (Neo4j Relationships)...")
    rec_engine = RecommendationEngine()
    
    if not rec_engine.driver:
        print("   ✗ Neo4j driver unavailable. Skipping relationships.")
        return

    count = 0
    for user in users:
        # Follows
        targets = random.sample([u for u in users if u != user], random.randint(0, 5))
        for t in targets:
            rec_engine.create_follow_relationship(user.id, t.id)
            count += 1
            
        # Likes
        if publications:
            liked = random.sample(publications, random.randint(0, 3))
            for p in liked:
                rec_engine.create_like_relationship(user.id, p.id)
                count += 1
                
        # Groups
        if groups:
            joined = random.sample(groups, random.randint(0, 2))
            for g in joined:
                rec_engine.create_membership_relationship(user.id, g.id)
                count += 1

    print(f"   ✓ Created {count} relationships in Neo4j.")

def seed_posts_and_comments(users, groups):
    print("\n8. Seeding Posts & Comments...")
    if not users: return

    admin_user = users[0]

    # Specific Welcome Post
    try:
        welcome_post, _ = Post.objects.get_or_create(
            author=admin_user,
            content="Bienvenue sur la plateforme ! Discutez de Data, Science et Engineering ici.",
            defaults={'group': None}
        )
        for u in users[:4]:
            if u != admin_user:
                Commentaire.objects.create(content_object=welcome_post, author=u, content="Merci !")
    except Exception:
        pass

    # Random Posts
    for user in users:
        for _ in range(NUM_POSTS_PER_USER):
            try:
                group = random.choice(groups) if groups and random.choice([True, False]) else None
                post = Post.objects.create(author=user, group=group, content=fake.paragraph(nb_sentences=2))
                
                # Comments
                commenters = random.sample(users, random.randint(0, 3))
                for c_user in commenters:
                    Commentaire.objects.create(content_object=post, author=c_user, content=fake.sentence())
            except Exception:
                pass
    print("   ✓ Posts seeded.")


def main():
    driver = get_neo4j_driver()
    if driver._driver is None:
        print("!!! NEO4J CONNECTION FAILED. Check .env password !!!")
        return

    clear_databases()
    users = seed_users()
    groups = seed_groups(users)
    pubs = seed_publications(users)
    seed_posts_and_comments(users, groups)
    seed_social(users, pubs, groups)
    
    print("\n" + "="*40)
    print("SEEDING COMPLETE".center(40))
    print("="*40 + "\n")

if __name__ == '__main__':
    main()