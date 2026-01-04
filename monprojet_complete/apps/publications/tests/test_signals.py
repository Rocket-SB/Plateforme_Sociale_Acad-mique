from django.test import TestCase
from apps.publications.models import Publication
from apps.users.models import Utilisateur
from config.mongodb import get_collection, close_connection
from bson.objectid import ObjectId

class PublicationSignalTests(TestCase):
    def setUp(self):
        self.publications_collection = get_collection('publications')
        self.publications_collection.delete_many({})
        
        # Create a user for the publication
        self.user = Utilisateur.objects.create_user(
            username='testuser', 
            password='testpassword'
        )

    def tearDown(self):
        close_connection()

    def test_publication_post_save_creates_mongo_document(self):
        # Create a new Publication
        publication = Publication.objects.create(
            title='Test Publication',
            main_author=self.user,
        )
        
        # Check that the document was created in MongoDB
        mongo_doc = self.publications_collection.find_one({'mysql_id': publication.id})
        self.assertIsNotNone(mongo_doc)
        self.assertEqual(mongo_doc['title'], 'Test Publication')
        
        # Check that the mongo_id was saved to the instance
        publication.refresh_from_db()
        self.assertIsNotNone(publication.mongo_id)
        self.assertEqual(ObjectId(publication.mongo_id), mongo_doc['_id'])

    def test_publication_post_save_updates_mongo_document(self):
        # Create a publication and verify it's in MongoDB
        publication = Publication.objects.create(
            title='Initial Title',
            main_author=self.user,
        )
        publication.refresh_from_db()
        self.assertIsNotNone(publication.mongo_id)
        
        # Update the publication
        publication.title = 'Updated Title'
        publication.save()
        
        # Check that the document was updated in MongoDB
        mongo_doc = self.publications_collection.find_one({'_id': ObjectId(publication.mongo_id)})
        self.assertIsNotNone(mongo_doc)
        self.assertEqual(mongo_doc['title'], 'Updated Title')

    def test_publication_post_delete_removes_mongo_document(self):
        # Create a publication
        publication = Publication.objects.create(
            title='To Be Deleted',
            main_author=self.user,
        )
        publication.refresh_from_db()
        mongo_id = publication.mongo_id
        self.assertIsNotNone(mongo_id)
        
        # Delete the publication
        publication.delete()
        
        # Check that the document was removed from MongoDB
        mongo_doc = self.publications_collection.find_one({'_id': ObjectId(mongo_id)})
        self.assertIsNone(mongo_doc)
