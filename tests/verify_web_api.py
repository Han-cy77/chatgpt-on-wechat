import requests
import time
import json
import sys

BASE_URL = "http://localhost:9899"

def test_web_channel():
    print("Testing Web Channel API...")
    
    # 1. Register
    username = f"testuser_{int(time.time())}"
    password = "password123"
    print(f"Registering user: {username}")
    
    try:
        res = requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
        print(f"Register response: {res.json()}")
    except Exception as e:
        print(f"Failed to register (might already exist or server down): {e}")
        return
    
    # 2. Login
    print("Logging in...")
    res = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
    data = res.json()
    print(f"Login response: {data}")
    
    if data['status'] != 'success':
        print("Login failed, aborting tests")
        return
        
    token = data['token']
    
    # 3. Create a conversation (via sending a message)
    print("Sending message to create conversation...")
    session_id = f"session_{int(time.time())}"
    msg_data = {
        "session_id": session_id,
        "message": "Hello, this is a test message for history",
        "timestamp": time.time(),
        "token": token
    }
    
    # Send message 1
    res = requests.post(f"{BASE_URL}/message", json=msg_data)
    resp_data = res.json()
    print(f"Message 1 response: {resp_data}")
    conversation_id = resp_data.get('conversation_id')
    print(f"Conversation ID from response: {conversation_id}")
    
    # Wait for processing and DB save
    print("Waiting 5 seconds for async processing...")
    time.sleep(5)
    
    # Send message 2 (in same conversation)
    if conversation_id:
        msg_data['conversation_id'] = conversation_id
        msg_data['message'] = "Second message in same conversation"
        print("Sending second message...")
        res = requests.post(f"{BASE_URL}/message", json=msg_data)
        print(f"Message 2 response: {res.json()}")
        time.sleep(2)

    # 4. List conversations
    print("Listing conversations...")
    res = requests.get(f"{BASE_URL}/conversations?token={token}")
    list_data = res.json()
    print(f"Conversations list: {json.dumps(list_data, indent=2)}")
    
    conversations = list_data.get('data', [])
    if not conversations:
        print("ERROR: No conversations found!")
    else:
        # Verify content
        cid = conversations[0]['id']
        print(f"Fetching details for conversation {cid}...")
        res = requests.get(f"{BASE_URL}/conversations?token={token}&id={cid}")
        detail_data = res.json()
        print(f"Conversation details: {json.dumps(detail_data, indent=2)}")
        
        # 5. Search conversations
        print("Searching conversations with keyword 'Hello'...")
        res = requests.get(f"{BASE_URL}/conversations?token={token}&keyword=Hello")
        search_data = res.json()
        print(f"Search results: {len(search_data.get('data', []))} found")
        
        # 6. Pagination
        print("Testing pagination (limit=1)...")
        res = requests.get(f"{BASE_URL}/conversations?token={token}&limit=1")
        page_data = res.json()
        print(f"Pagination result: {page_data.get('pagination')}")
        
        # 7. Delete conversation
        print(f"Deleting conversation {cid}...")
        res = requests.delete(f"{BASE_URL}/conversations?token={token}&id={cid}")
        print(f"Delete response: {res.json()}")
        
        # Verify deletion
        res = requests.get(f"{BASE_URL}/conversations?token={token}")
        remaining = res.json().get('data', [])
        print(f"Remaining conversations: {len(remaining)}")

if __name__ == "__main__":
    test_web_channel()
