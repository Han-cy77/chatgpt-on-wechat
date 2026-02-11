import requests
import time
import json
import sys

BASE_URL = "http://localhost:9899"

def test_history_filter():
    print("Testing History Filter API...")
    
    # 1. Register & Login
    username = f"filter_user_{int(time.time())}"
    password = "password123"
    
    try:
        requests.post(f"{BASE_URL}/register", json={"username": username, "password": password})
        res = requests.post(f"{BASE_URL}/login", json={"username": username, "password": password})
        data = res.json()
        if data.get('status') != 'success':
            print("Login failed")
            return
        token = data['token']
        print(f"Logged in as {username}")
    except Exception as e:
        print(f"Failed to connect: {e}")
        return

    # 2. Create Conversations
    # Conv 1: Python
    print("Creating Conversation 1 (Python)...")
    create_conversation(token, "Python Help")
    time.sleep(2)
    
    # Conv 2: Java
    print("Creating Conversation 2 (Java)...")
    create_conversation(token, "Java Help")
    time.sleep(2)
    
    # Conv 3: Rust
    print("Creating Conversation 3 (Rust)...")
    create_conversation(token, "Rust Help")
    time.sleep(2)

    # 3. Test List All
    print("\n[Test] List All Conversations")
    convs = get_conversations(token)
    print(f"Total conversations: {len(convs)}")
    if len(convs) < 3:
        print("FAIL: Expected at least 3 conversations")
    else:
        print("PASS: List All")

    # 4. Test Keyword Search
    print("\n[Test] Search Keyword 'Python'")
    convs = get_conversations(token, keyword="Python")
    print(f"Found: {len(convs)}")
    if len(convs) == 1 and "Python" in convs[0]['title']:
        print("PASS: Keyword Search")
    else:
        print(f"FAIL: Expected 1 result with 'Python', got {len(convs)}")
        for c in convs:
            print(f" - {c['title']}")

    # 5. Test Date Range
    # We need timestamps. 
    # Current time is T.
    # Conv 3 is T-2s. Conv 2 is T-4s. Conv 1 is T-6s.
    now = time.time()
    start_time = now - 5 # Should include Conv 3 and maybe Conv 2
    end_time = now + 10
    
    print(f"\n[Test] Date Range: {start_time} to {end_time}")
    convs = get_conversations(token, start_date=start_time, end_date=end_time)
    print(f"Found: {len(convs)}")
    # Should find Conv 3 (Rust) and maybe Conv 2 (Java) depending on timing
    # Conv 1 (Python) was created > 6s ago, so it should be excluded if start_time is now-5
    
    titles = [c['title'] for c in convs]
    print(f"Titles found: {titles}")
    
    if "Rust" in str(titles) and "Python" not in str(titles):
        print("PASS: Date Range (approx)")
    else:
        print("FAIL: Date Range logic check failed")

    # 6. Test Pagination
    print("\n[Test] Pagination (Limit 1, Offset 0)")
    convs = get_conversations(token, limit=1, offset=0)
    if len(convs) == 1:
        print(f"Page 1: {convs[0]['title']}")
        print("PASS: Pagination Page 1")
    else:
        print(f"FAIL: Expected 1, got {len(convs)}")

    print("\n[Test] Pagination (Limit 1, Offset 1)")
    convs = get_conversations(token, limit=1, offset=1)
    if len(convs) == 1:
        print(f"Page 2: {convs[0]['title']}")
        print("PASS: Pagination Page 2")
    else:
        print(f"FAIL: Expected 1, got {len(convs)}")

def create_conversation(token, message):
    session_id = f"sess_{int(time.time())}_{message[:5]}"
    payload = {
        "session_id": session_id,
        "message": message,
        "token": token
    }
    requests.post(f"{BASE_URL}/message", json=payload)
    # Wait for async processing
    time.sleep(1)

def get_conversations(token, **kwargs):
    params = {"token": token}
    params.update(kwargs)
    res = requests.get(f"{BASE_URL}/conversations", params=params)
    data = res.json()
    if data['status'] == 'success':
        return data['data']
    return []

if __name__ == "__main__":
    test_history_filter()
