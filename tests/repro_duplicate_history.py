import requests
import time
import uuid
import unittest
import string
import random

BASE_URL = "http://localhost:9899"

class TestHistoryFeatures(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Register a unique user for this test run
        cls.username = f"test_user_{int(time.time())}"
        cls.password = "password123"
        
        # Register
        try:
            requests.post(f"{BASE_URL}/register", json={"username": cls.username, "password": cls.password})
            # Login
            res = requests.post(f"{BASE_URL}/login", json={"username": cls.username, "password": cls.password})
            cls.token = res.json()['token']
            print(f"Setup complete. User: {cls.username}")
        except Exception as e:
            print(f"Setup failed. Is the server running? Error: {e}")
            raise

    def test_01_distinct_conversations(self):
        """Verify that two new conversations result in distinct IDs and content."""
        print("\nTest 01: Distinct Conversations")
        
        # Conv 1
        msg1 = "First conversation message"
        res1 = requests.post(f"{BASE_URL}/message", json={"token": self.token, "message": msg1})
        cid1 = res1.json().get('conversation_id')
        self.assertIsNotNone(cid1)
        
        # Conv 2
        msg2 = "Second conversation message"
        res2 = requests.post(f"{BASE_URL}/message", json={"token": self.token, "message": msg2})
        cid2 = res2.json().get('conversation_id')
        self.assertIsNotNone(cid2)
        
        self.assertNotEqual(cid1, cid2, "Conversation IDs should be different")
        
        # Verify content
        detail1 = requests.get(f"{BASE_URL}/conversations?token={self.token}&id={cid1}").json()['data']
        detail2 = requests.get(f"{BASE_URL}/conversations?token={self.token}&id={cid2}").json()['data']
        
        content1 = detail1['messages'][0]['content']
        content2 = detail2['messages'][0]['content']
        
        self.assertEqual(content1, msg1)
        self.assertEqual(content2, msg2)
        print("Success: Conversations are distinct")

    def test_02_short_conversation_title(self):
        """Verify title generation for short messages."""
        print("\nTest 02: Short Conversation Title")
        msg = "Hi"
        res = requests.post(f"{BASE_URL}/message", json={"token": self.token, "message": msg})
        cid = res.json().get('conversation_id')
        
        detail = requests.get(f"{BASE_URL}/conversations?token={self.token}&id={cid}").json()['data']
        self.assertEqual(detail['title'], "Hi", "Title should match short message exactly")
        print("Success: Short title correct")

    def test_03_long_conversation_title(self):
        """Verify title truncation for long messages."""
        print("\nTest 03: Long Conversation Title")
        # Generate 100 chars
        long_msg = ''.join(random.choices(string.ascii_letters, k=100))
        res = requests.post(f"{BASE_URL}/message", json={"token": self.token, "message": long_msg})
        cid = res.json().get('conversation_id')
        
        detail = requests.get(f"{BASE_URL}/conversations?token={self.token}&id={cid}").json()['data']
        title = detail['title']
        
        # Logic says title = prompt[:20]
        self.assertEqual(len(title), 20, "Title should be truncated to 20 chars")
        self.assertEqual(title, long_msg[:20], "Title should match first 20 chars")
        
        # Check full content is saved
        saved_msg = detail['messages'][0]['content']
        self.assertEqual(saved_msg, long_msg, "Full message content should be preserved")
        print("Success: Long title truncated and content preserved")

    def test_04_empty_conversation(self):
        """Verify handling of empty messages."""
        print("\nTest 04: Empty Conversation")
        # Empty string
        res = requests.post(f"{BASE_URL}/message", json={"token": self.token, "message": ""})
        # Assuming the backend might either reject it or create a default title
        # Based on code: prompt[:20] if prompt else "New Conversation"
        
        cid = res.json().get('conversation_id')
        self.assertIsNotNone(cid)
        
        detail = requests.get(f"{BASE_URL}/conversations?token={self.token}&id={cid}").json()['data']
        self.assertEqual(detail['title'], "New Conversation", "Should use default title for empty message")
        print("Success: Empty message handled gracefully")

    def test_05_crud_delete(self):
        """Verify conversation deletion."""
        print("\nTest 05: CRUD Delete")
        # Create one to delete
        res = requests.post(f"{BASE_URL}/message", json={"token": self.token, "message": "To be deleted"})
        cid = res.json().get('conversation_id')
        
        # Verify it exists
        list_res = requests.get(f"{BASE_URL}/conversations?token={self.token}")
        ids = [c['id'] for c in list_res.json()['data']]
        self.assertIn(cid, ids)
        
        # Delete it
        del_res = requests.delete(f"{BASE_URL}/conversations?token={self.token}&id={cid}")
        self.assertEqual(del_res.json()['status'], 'success')
        
        # Verify it's gone
        list_res_after = requests.get(f"{BASE_URL}/conversations?token={self.token}")
        ids_after = [c['id'] for c in list_res_after.json()['data']]
        self.assertNotIn(cid, ids_after)
        print("Success: Conversation deleted")

if __name__ == "__main__":
    unittest.main()
