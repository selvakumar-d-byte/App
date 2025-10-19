import requests
import sys
import json
from datetime import datetime

class LevelUpHiveAPITester:
    def __init__(self, base_url="https://certify-hub-15.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "status": "PASS" if success else "FAIL",
            "details": details
        }
        self.test_results.append(result)
        
        status_icon = "✅" if success else "❌"
        print(f"{status_icon} {name}: {details}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}"
            
            if not success:
                details += f" (Expected {expected_status})"
                if response.text:
                    try:
                        error_data = response.json()
                        details += f" - {error_data.get('detail', 'Unknown error')}"
                    except:
                        details += f" - {response.text[:100]}"

            self.log_test(name, success, details)
            return success, response.json() if success and response.text else {}

        except Exception as e:
            self.log_test(name, False, f"Error: {str(e)}")
            return False, {}

    def test_auth_flow(self):
        """Test complete authentication flow"""
        print("\n🔐 Testing Authentication Flow...")
        
        # Test user registration
        test_user = {
            "name": f"Test User {datetime.now().strftime('%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data=test_user
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['id']
            self.log_test("Token Received", True, "Authentication token obtained")
        else:
            self.log_test("Token Received", False, "No token in response")
            return False

        # Test login with same credentials
        login_data = {
            "email": test_user["email"],
            "password": test_user["password"]
        }
        
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        # Test get current user
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        return True

    def test_courses_api(self):
        """Test courses API endpoints"""
        print("\n📚 Testing Courses API...")
        
        # Get all courses
        success, courses = self.run_test(
            "Get All Courses",
            "GET",
            "courses",
            200
        )
        
        if not success or not courses:
            self.log_test("Courses Available", False, "No courses found")
            return False
        
        self.log_test("Courses Available", True, f"Found {len(courses)} courses")
        
        # Test search functionality
        if courses:
            first_course = courses[0]
            search_term = first_course['name'][:5]  # First 5 characters
            
            success, filtered_courses = self.run_test(
                "Search Courses",
                "GET",
                f"courses?search={search_term}",
                200
            )
            
            # Test language filter
            success, tamil_courses = self.run_test(
                "Filter by Tamil",
                "GET",
                "courses?language=tamil",
                200
            )
            
            success, english_courses = self.run_test(
                "Filter by English",
                "GET",
                "courses?language=english",
                200
            )
            
            # Test get specific course
            course_id = first_course['id']
            success, course_detail = self.run_test(
                "Get Course Detail",
                "GET",
                f"courses/{course_id}",
                200
            )
            
            # Test get course videos
            success, videos = self.run_test(
                "Get Course Videos",
                "GET",
                f"courses/{course_id}/videos",
                200
            )
            
            if success and videos:
                self.log_test("Videos Available", True, f"Found {len(videos)} videos")
                return course_id, videos
            else:
                self.log_test("Videos Available", False, "No videos found")
                
        return None, []

    def test_progress_api(self, course_id, videos):
        """Test progress tracking API"""
        print("\n📊 Testing Progress API...")
        
        if not course_id or not videos or not self.user_id:
            self.log_test("Progress Test Setup", False, "Missing required data")
            return
        
        video = videos[0]
        
        # Update progress
        progress_data = {
            "user_id": self.user_id,
            "course_id": course_id,
            "video_id": video['id'],
            "watched_duration": 30,
            "completed": False
        }
        
        success, response = self.run_test(
            "Update Video Progress",
            "POST",
            "progress/update",
            200,
            data=progress_data
        )
        
        # Get user progress
        success, progress = self.run_test(
            "Get User Progress",
            "GET",
            f"progress/user/{self.user_id}/course/{course_id}",
            200
        )
        
        if success and progress:
            self.log_test("Progress Tracking", True, f"Progress saved for {len(progress)} videos")
        
        # Mark video as completed
        progress_data['completed'] = True
        progress_data['watched_duration'] = video['duration']
        
        success, response = self.run_test(
            "Complete Video",
            "POST",
            "progress/update",
            200,
            data=progress_data
        )

    def test_certificate_api(self, course_id):
        """Test certificate generation API"""
        print("\n🏆 Testing Certificate API...")
        
        if not course_id or not self.user_id:
            self.log_test("Certificate Test Setup", False, "Missing required data")
            return
        
        # Generate certificate
        success, certificate = self.run_test(
            "Generate Certificate",
            "POST",
            f"certificates/generate?user_id={self.user_id}&course_id={course_id}",
            200
        )
        
        if success and certificate:
            self.log_test("Certificate Generated", True, f"Certificate ID: {certificate.get('id', 'N/A')[:8]}")
            
            # Get certificate
            success, retrieved_cert = self.run_test(
                "Get Certificate",
                "GET",
                f"certificates/user/{self.user_id}/course/{course_id}",
                200
            )
            
            if success and retrieved_cert:
                self.log_test("Certificate Retrieval", True, "Certificate retrieved successfully")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting LevelUpHive API Tests...")
        print(f"Testing against: {self.api_url}")
        
        # Test authentication
        if not self.test_auth_flow():
            print("❌ Authentication failed, stopping tests")
            return False
        
        # Test courses
        course_id, videos = self.test_courses_api()
        
        # Test progress tracking
        if course_id and videos:
            self.test_progress_api(course_id, videos)
            
            # Test certificate generation
            self.test_certificate_api(course_id)
        
        # Print summary
        print(f"\n📊 Test Summary:")
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed == self.tests_run

def main():
    tester = LevelUpHiveAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'tests_run': tester.tests_run,
                'tests_passed': tester.tests_passed,
                'success_rate': (tester.tests_passed/tester.tests_run)*100 if tester.tests_run > 0 else 0
            },
            'results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())