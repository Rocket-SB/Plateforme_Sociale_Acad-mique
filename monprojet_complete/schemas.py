# utils/schemas.py
from bson import ObjectId
from datetime import datetime
from typing import List, Optional, Dict, Any

# Publication Document (EMBED heavy)
PUBLICATION_SCHEMA = {
    "_id": ObjectId(),
    "mysql_id": "123",  # Link back to MySQL
    "title": "Article Title",
    "slug": "article-title",
    "abstract": "Full abstract...",
    "doi": "10.1234/abc",
    
    # EMBEDDED
    "metadata": {
        "keywords": ["AI", "ML"],
        "subjects": ["Computer Science"],
        "language": "fr",
        "license": "CC-BY-4.0",
        "version": "1.0"
    },
    "images": [  # EMBEDDED
        {"url": "image1.jpg", "alt": "Figure 1", "caption": "..."}
    ],
    "citations_made": [  # EMBEDDED (citations this pub made)
        {"title": "Cited Work", "doi": "10.123", "year": 2023}
    ],
    "authors": [  # EMBEDDED (full author info)
        {"mysql_id": "user1", "name": "John Doe", "affiliation": "Univ", "orcid": "1234"}
    ],
    
    # LINKED
    "cited_by": ["pub_id_1", "pub_id_2"],  # Array of ObjectIds
    "main_author_id": ObjectId("user_obj_id"),  # LINK to users collection
    
    "created_at": datetime.utcnow(),
    "updated_at": datetime.utcnow()
}

# User Document (EMBED profile)
USER_SCHEMA = {
    "_id": ObjectId(),
    "mysql_id": "123",
    
    # EMBEDDED Profile
    "profile": {
        "bio": "Researcher in AI...",
        "research_interests": ["AI", "NLP"],
        "website": "researcher.com",
        "orcid": "0000-1234-5678-9012",
        "affiliations": ["University X"],
        "location": "Morocco"
    },
    
    # LINKED Publications & Groups
    "publications": ["pub_id_1", "pub_id_2"],  # Array of ObjectIds
    "groups": ["group_id_1"],  # Array of ObjectIds
    
    "created_at": datetime.utcnow()
}

# Group Document
GROUP_SCHEMA = {
    "_id": ObjectId(),
    "mysql_id": "123",
    "name": "AI Research Group",
    "description": "AI researchers...",
    "members": ["user_id_1", "user_id_2"],  # LINKED users
    "admins": ["user_id_1"],
    "created_at": datetime.utcnow()
}
