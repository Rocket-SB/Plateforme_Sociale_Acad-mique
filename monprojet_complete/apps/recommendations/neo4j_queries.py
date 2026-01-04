from .neo4j_service import get_neo4j_driver

class RecommendationEngine:
    def __init__(self):
        self.driver = get_neo4j_driver()

    # ===== USER RECOMMENDATIONS =====

    def recommend_users_to_follow(self, user_id, limit=10):
        """
        Recommend users based on:
        1. Friends of friends (2nd degree connections)
        2. Users with shared topics/interests
        """
        session = self.driver.get_session()
        if not session:
            return []
        query = """
        MATCH (u:Utilisateur {user_id: $user_id})
        MATCH (u)-[:FOLLOWS]-&gt;(:Utilisateur)-[:FOLLOWS]-&gt;(rec:Utilisateur)
        WHERE NOT (u)-[:FOLLOWS]-&gt;(rec) AND u &lt;&gt; rec
        WITH rec, COUNT(DISTINCT u) AS mutual_connections
        
        OPTIONAL MATCH (u)-[:INTERESTED_IN]-&gt;(:Topic)&lt;-[:INTERESTED_IN]-(rec)
        WITH rec, mutual_connections, COUNT(*) AS shared_topics
        
        RETURN rec.user_id AS user_id, rec.username AS username,
               mutual_connections, shared_topics,
               (mutual_connections + shared_topics * 2) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        try:
            result = session.run(query, user_id=user_id, limit=limit)
            return [dict(record) for record in result]
        except Exception as e:
            print(f"Error in recommend_users_to_follow: {e}")
            return []
        finally:
            if session:
                session.close()

    # ===== PUBLICATION RECOMMENDATIONS =====

    def recommend_publications(self, user_id, limit=10):
        """
        Recommend publications based on:
        1. What similar users liked
        2. Publications in user's topics
        """
        session = self.driver.get_session()
        if not session:
            return []
        # This query uses a UNION subquery to combine scores from two different recommendation approaches.
        # 1. Publications liked by users with similar interests.
        # 2. Publications that have topics the current user is interested in.
        # Each approach is given a 'weight' and the final score is an aggregation of these weights.
        query = """
        MATCH (u:Utilisateur {user_id: $user_id})
        CALL {
            WITH u
            // Score Part 1: Publications liked by similar users
            MATCH (u)-[:INTERESTED_IN]->(t:Topic)<-[:INTERESTED_IN]-(similar:Utilisateur)
            WHERE u <> similar
            MATCH (similar)-[:LIKED]->(p:Publication)
            WHERE NOT (u)-[:LIKED]->(p)
            RETURN p, 1.0 AS weight
            UNION ALL
            WITH u
            // Score Part 2: Publications in user's interested topics
            MATCH (u)-[:INTERESTED_IN]->(t:Topic)<-[:HAS_TOPIC]-(p:Publication)
            WHERE NOT (u)-[:LIKED]->(p)
            RETURN p, 1.5 AS weight
        }
        // Aggregate scores and return final recommendations
        WITH p, SUM(weight) AS score
        RETURN p.pub_id AS publication_id, p.title AS title, score
        ORDER BY score DESC
        LIMIT $limit
        """
        try:
            result = session.run(query, user_id=user_id, limit=limit)
            return [dict(record) for record in result]
        except Exception as e:
            print(f"Error in recommend_publications: {e}")
            return []
        finally:
            if session:
                session.close()

    def recommend_users_for_publication(self, publication_id, user_id, limit=5):
        """
        Recommend users who are interested in the same topics as the publication.
        """
        session = self.driver.get_session()
        if not session:
            return []
        query = """
        MATCH (p:Publication {pub_id: $publication_id})-[:HAS_TOPIC]->(t:Topic)<-[:INTERESTED_IN]-(u:Utilisateur)
        WHERE u.user_id <> $user_id
        WITH u, COLLECT(t.name) AS shared_topics, COUNT(t) AS num_shared_topics
        RETURN u.user_id AS user_id, u.username AS username, shared_topics, num_shared_topics
        ORDER BY num_shared_topics DESC
        LIMIT $limit
        """
        try:
            result = session.run(query, publication_id=publication_id, user_id=user_id, limit=limit)
            return [dict(record) for record in result]
        except Exception as e:
            print(f"Error in recommend_users_for_publication: {e}")
            return []
        finally:
            if session:
                session.close()

    def recommend_similar_publications(self, publication_id, limit=3):
        """
        Recommend similar publications based on shared topics.
        """
        session = self.driver.get_session()
        if not session:
            return []
        query = """
        MATCH (current:Publication {pub_id: $publication_id})-[:HAS_TOPIC]->(topic:Topic)
        MATCH (rec:Publication)-[:HAS_TOPIC]->(topic)
        WHERE current <> rec
        WITH rec, COUNT(topic) AS shared_topics
        RETURN rec.pub_id AS publication_id, rec.title AS title, shared_topics
        ORDER BY shared_topics DESC
        LIMIT $limit
        """
        try:
            result = session.run(query, publication_id=publication_id, limit=limit)
            return [dict(record) for record in result]
        except Exception as e:
            print(f"Error in recommend_similar_publications: {e}")
            return []
        finally:
            if session:
                session.close()

    # ===== GROUP RECOMMENDATIONS =====

    def recommend_groups(self, user_id, limit=10):
        """
        Recommend groups based on:
        1. Groups where followed users are members
        2. Groups with similar topics
        """
        session = self.driver.get_session()
        if not session:
            return []
        query = """
        MATCH (u:Utilisateur {user_id: $user_id})
        
        // Groups joined by followed users
        MATCH (u)-[:FOLLOWS]-&gt;(:Utilisateur)-[:MEMBER_OF]-&gt;(group:Group)
        WHERE NOT (u)-[:MEMBER_OF]-&gt;(group)
        
        WITH group, COUNT(*) AS friends_in_group
        
        // Groups with matching topics
        OPTIONAL MATCH (u)-[:INTERESTED_IN]-&gt;(:Topic)&lt;-[:HAS_TOPIC]-(group)
        WITH group, friends_in_group, COUNT(*) AS topic_match
        
        RETURN group.group_id AS group_id,
               group.name AS group_name,
               friends_in_group,
               COALESCE(topic_match, 0) AS topic_match,
               (friends_in_group + COALESCE(topic_match, 0) * 2) AS score
        ORDER BY score DESC
        LIMIT $limit
        """
        try:
            result = session.run(query, user_id=user_id, limit=limit)
            return [dict(record) for record in result]
        except Exception as e:
            print(f"Error in recommend_groups: {e}")
            return []
        finally:
            if session:
                session.close()

    # ===== SYNC DATA TO NEO4J =====

    def sync_user_to_neo4j(self, user_id, username, email):
        """Create/update user node in Neo4j"""
        session = self.driver.get_session()
        if not session:
            return
        query = """
        MERGE (u:Utilisateur {user_id: $user_id})
        SET u.username = $username, u.email = $email, u.synced_at = datetime()
        RETURN u
        """
        try:
            session.run(query, user_id=user_id, username=username, email=email)
        except Exception as e:
            print(f"Error syncing user: {e}")
        finally:
            if session:
                session.close()

    def sync_publication_to_neo4j(self, pub_id, title, author_id, topics_list=[]):
        """Create/update publication node and link topics"""
        session = self.driver.get_session()
        if not session:
            return
        
        # Create publication and link topics in one query
        query = """
        MATCH (u:Utilisateur {user_id: $author_id})
        MERGE (p:Publication {pub_id: $pub_id})
        SET p.title = $title, p.synced_at = datetime()
        MERGE (u)-[:AUTHOR_OF]->(p)
        WITH p
        UNWIND $topics as topic_name
        MERGE (t:Topic {name: topic_name})
        MERGE (p)-[:HAS_TOPIC]->(t)
        """
        try:
            session.run(query, pub_id=pub_id, title=title, author_id=author_id, topics=topics_list)
            self.sync_user_interests(author_id)
        except Exception as e:
            print(f"Error syncing publication to Neo4j: {e}")
        finally:
            if session:
                session.close()

    def sync_user_interests(self, user_id):
        """
        Sync user interests based on the topics of their authored publications.
        """
        session = self.driver.get_session()
        if not session:
            return
        query = """
        MATCH (u:Utilisateur {user_id: $user_id})-[:AUTHOR_OF]->(p:Publication)-[:HAS_TOPIC]->(t:Topic)
        MERGE (u)-[r:INTERESTED_IN]->(t)
        SET r.created_at = datetime()
        """
        try:
            session.run(query, user_id=user_id)
        except Exception as e:
            print(f"Error syncing user interests: {e}")
        finally:
            if session:
                session.close()

    def create_follow_relationship(self, follower_id, followee_id):
        """Create FOLLOWS relationship"""
        session = self.driver.get_session()
        if not session:
            return
        query = """
        MATCH (follower:Utilisateur {user_id: $follower_id})
        MATCH (followee:Utilisateur {user_id: $followee_id})
        MERGE (follower)-[:FOLLOWS {created_at: datetime()}]-&gt;(followee)
        """
        try:
            session.run(query, follower_id=follower_id, followee_id=followee_id)
        except Exception as e:
            print(f"Error creating follow: {e}")
        finally:
            if session:
                session.close()

    def create_like_relationship(self, user_id, pub_id):
        """Create LIKED relationship"""
        session = self.driver.get_session()
        if not session:
            return
        query = """
        MATCH (u:Utilisateur {user_id: $user_id})
        MATCH (p:Publication {pub_id: $pub_id})
        MERGE (u)-[:LIKED {created_at: datetime()}]-&gt;(p)
        """
        try:
            session.run(query, user_id=user_id, pub_id=pub_id)
        except Exception as e:
            print(f"Error creating like: {e}")
        finally:
            if session:
                session.close()

    def create_membership_relationship(self, user_id, group_id):
        """Create MEMBER_OF relationship"""
        session = self.driver.get_session()
        if not session:
            return
        query = """
        MATCH (u:Utilisateur {user_id: $user_id})
        MATCH (g:Group {group_id: $group_id})
        MERGE (u)-[:MEMBER_OF {joined_at: datetime()}]-&gt;(g)
        """
        try:
            session.run(query, user_id=user_id, group_id=group_id)
        except Exception as e:
            print(f"Error creating membership: {e}")
        finally:
            if session:
                session.close()
