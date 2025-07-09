import requests
import time
import uuid
from datetime import datetime

class NotesAPITester:
    def __init__(self, base_url="https://500f2558-fa01-47bc-ba0b-4dd1bfc9170e.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_note_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.text:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                return success, None
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, None

    def test_health_check(self):
        """Test API health check endpoint"""
        return self.run_test(
            "API Health Check",
            "GET",
            "",
            200
        )

    def test_get_notes(self):
        """Test getting all notes"""
        return self.run_test(
            "Get All Notes",
            "GET",
            "notes",
            200
        )

    def test_create_note(self, title, content):
        """Test creating a new note"""
        success, response = self.run_test(
            "Create Note",
            "POST",
            "notes",
            200,
            data={"title": title, "content": content}
        )
        if success and response and 'id' in response:
            self.test_note_id = response['id']
            print(f"Created note with ID: {self.test_note_id}")
        return success, response

    def test_get_note_by_id(self):
        """Test getting a specific note by ID"""
        if not self.test_note_id:
            print("❌ Cannot test get_note_by_id: No test note ID available")
            return False, None
        
        return self.run_test(
            "Get Note by ID",
            "GET",
            f"notes/{self.test_note_id}",
            200
        )

    def test_update_note(self, title, content):
        """Test updating a note"""
        if not self.test_note_id:
            print("❌ Cannot test update_note: No test note ID available")
            return False, None
        
        return self.run_test(
            "Update Note",
            "PUT",
            f"notes/{self.test_note_id}",
            200,
            data={"title": title, "content": content}
        )

    def test_delete_note(self):
        """Test deleting a note"""
        if not self.test_note_id:
            print("❌ Cannot test delete_note: No test note ID available")
            return False, None
        
        return self.run_test(
            "Delete Note",
            "DELETE",
            f"notes/{self.test_note_id}",
            200
        )

    def test_get_nonexistent_note(self):
        """Test getting a note that doesn't exist"""
        random_id = str(uuid.uuid4())
        return self.run_test(
            "Get Nonexistent Note",
            "GET",
            f"notes/{random_id}",
            404
        )

    def test_update_nonexistent_note(self):
        """Test updating a note that doesn't exist"""
        random_id = str(uuid.uuid4())
        return self.run_test(
            "Update Nonexistent Note",
            "PUT",
            f"notes/{random_id}",
            404,
            data={"title": "Updated Title", "content": "Updated Content"}
        )

    def test_delete_nonexistent_note(self):
        """Test deleting a note that doesn't exist"""
        random_id = str(uuid.uuid4())
        return self.run_test(
            "Delete Nonexistent Note",
            "DELETE",
            f"notes/{random_id}",
            404
        )

    def run_all_tests(self):
        """Run all API tests"""
        print(f"🚀 Starting Notes API tests against {self.api_url}")
        
        # Test health check
        self.test_health_check()
        
        # Test getting all notes
        self.test_get_notes()
        
        # Test creating a note
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_create_note(f"Test Note {timestamp}", f"<p>This is a test note created at {timestamp}</p>")
        
        # Test getting the created note
        self.test_get_note_by_id()
        
        # Test updating the note
        updated_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_update_note(f"Updated Test Note {updated_timestamp}", f"<p>This note was updated at {updated_timestamp}</p>")
        
        # Test error cases
        self.test_get_nonexistent_note()
        self.test_update_nonexistent_note()
        self.test_delete_nonexistent_note()
        
        # Test deleting the note
        self.test_delete_note()
        
        # Print results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = NotesAPITester()
    tester.run_all_tests()