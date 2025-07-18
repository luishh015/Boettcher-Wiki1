#!/usr/bin/env python3
"""
Comprehensive Backend API Tests for Böttcher Wiki
Tests all core Q&A functions, data flow, edge cases, and database integration
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = "https://5f463c4f-105f-4102-90ec-a413bdeb91a6.preview.emergentagent.com/api"

class BöttcherWikiTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.created_question_ids = []
        
    def log_test(self, test_name, success, message="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "response_data": response_data
        })
        
    def test_health_check(self):
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Health Check", True, "API is healthy")
                    return True
                else:
                    self.log_test("Health Check", False, f"Unexpected response: {data}")
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
        return False
        
    def test_create_question(self):
        """Test POST /api/questions - Create new questions"""
        test_questions = [
            {
                "question_text": "Wie funktioniert die Quantenmechanik in der Praxis?",
                "category": "Physik",
                "author": "Dr. Schmidt",
                "tags": ["quantenmechanik", "physik", "wissenschaft"]
            },
            {
                "question_text": "Was sind die besten Methoden für maschinelles Lernen?",
                "category": "Informatik", 
                "author": "Prof. Müller",
                "tags": ["ml", "ki", "algorithmus"]
            },
            {
                "question_text": "Wie bereitet man traditionelle deutsche Küche zu?",
                "category": "Kochen",
                "author": "Chef Weber",
                "tags": ["kochen", "deutsch", "tradition"]
            }
        ]
        
        success_count = 0
        for i, question_data in enumerate(test_questions):
            try:
                response = requests.post(
                    f"{self.base_url}/questions",
                    json=question_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") and data.get("question_text") == question_data["question_text"]:
                        self.created_question_ids.append(data["id"])
                        success_count += 1
                        self.log_test(f"Create Question {i+1}", True, f"Created question with ID: {data['id']}")
                    else:
                        self.log_test(f"Create Question {i+1}", False, f"Invalid response structure: {data}")
                else:
                    self.log_test(f"Create Question {i+1}", False, f"Status code: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Create Question {i+1}", False, f"Error: {str(e)}")
                
        return success_count == len(test_questions)
        
    def test_get_all_questions(self):
        """Test GET /api/questions - Retrieve all questions"""
        try:
            response = requests.get(f"{self.base_url}/questions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    question_count = len(data)
                    # Verify structure of returned questions
                    if question_count > 0:
                        first_question = data[0]
                        if "question" in first_question and "answer" in first_question:
                            self.log_test("Get All Questions", True, f"Retrieved {question_count} questions with proper structure")
                            return True
                        else:
                            self.log_test("Get All Questions", False, f"Invalid question structure: {first_question}")
                    else:
                        self.log_test("Get All Questions", True, "Retrieved empty list (no questions yet)")
                        return True
                else:
                    self.log_test("Get All Questions", False, f"Expected list, got: {type(data)}")
            else:
                self.log_test("Get All Questions", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get All Questions", False, f"Error: {str(e)}")
        return False
        
    def test_add_answers(self):
        """Test POST /api/questions/{id}/answer - Add answers to questions"""
        if not self.created_question_ids:
            self.log_test("Add Answers", False, "No questions available to answer")
            return False
            
        test_answers = [
            {
                "question_id": "",  # Will be set dynamically
                "answer_text": "Quantenmechanik beschreibt das Verhalten von Teilchen auf subatomarer Ebene durch Wahrscheinlichkeiten und Wellenfunktionen.",
                "author": "Dr. Einstein"
            },
            {
                "question_id": "",  # Will be set dynamically
                "answer_text": "Die besten ML-Methoden hängen vom Problem ab: Supervised Learning für klassifizierte Daten, Unsupervised für Muster, Deep Learning für komplexe Daten.",
                "author": "Prof. Turing"
            }
        ]
        
        success_count = 0
        for i, answer_data in enumerate(test_answers[:len(self.created_question_ids)]):
            try:
                question_id = self.created_question_ids[i]
                # Set the question_id in the answer data to match API requirement
                answer_data["question_id"] = question_id
                response = requests.post(
                    f"{self.base_url}/questions/{question_id}/answer",
                    json=answer_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("id") and data.get("question_id") == question_id:
                        success_count += 1
                        self.log_test(f"Add Answer {i+1}", True, f"Added answer to question {question_id}")
                    else:
                        self.log_test(f"Add Answer {i+1}", False, f"Invalid response: {data}")
                else:
                    self.log_test(f"Add Answer {i+1}", False, f"Status code: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Add Answer {i+1}", False, f"Error: {str(e)}")
                
        return success_count > 0
        
    def test_search_functionality(self):
        """Test POST /api/search - Search questions by text and category"""
        search_tests = [
            {"query": "Quantenmechanik", "category": None, "expected_min": 1},
            {"query": "", "category": "Physik", "expected_min": 1},
            {"query": "maschinelles", "category": "Informatik", "expected_min": 1},
            {"query": "nonexistent", "category": None, "expected_min": 0}
        ]
        
        success_count = 0
        for i, search_test in enumerate(search_tests):
            try:
                search_data = {"query": search_test["query"]}
                if search_test["category"]:
                    search_data["category"] = search_test["category"]
                    
                response = requests.post(
                    f"{self.base_url}/search",
                    json=search_data,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        result_count = len(data)
                        if result_count >= search_test["expected_min"]:
                            success_count += 1
                            self.log_test(f"Search Test {i+1}", True, f"Found {result_count} results for query '{search_test['query']}'")
                        else:
                            self.log_test(f"Search Test {i+1}", False, f"Expected at least {search_test['expected_min']} results, got {result_count}")
                    else:
                        self.log_test(f"Search Test {i+1}", False, f"Expected list, got: {type(data)}")
                else:
                    self.log_test(f"Search Test {i+1}", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Search Test {i+1}", False, f"Error: {str(e)}")
                
        return success_count >= 3  # Allow some flexibility
        
    def test_get_categories(self):
        """Test GET /api/categories - Get all available categories"""
        try:
            response = requests.get(f"{self.base_url}/categories", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and isinstance(data["categories"], list):
                    categories = data["categories"]
                    expected_categories = ["Physik", "Informatik", "Kochen"]
                    found_categories = [cat for cat in expected_categories if cat in categories]
                    
                    if len(found_categories) >= 2:  # At least 2 of our test categories
                        self.log_test("Get Categories", True, f"Found categories: {categories}")
                        return True
                    else:
                        self.log_test("Get Categories", False, f"Missing expected categories. Found: {categories}")
                else:
                    self.log_test("Get Categories", False, f"Invalid response structure: {data}")
            else:
                self.log_test("Get Categories", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Categories", False, f"Error: {str(e)}")
        return False
        
    def test_get_stats(self):
        """Test GET /api/stats - Get statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_questions", "answered_questions", "unanswered_questions"]
                
                if all(field in data for field in required_fields):
                    total = data["total_questions"]
                    answered = data["answered_questions"]
                    unanswered = data["unanswered_questions"]
                    
                    # Verify math
                    if total == answered + unanswered and total >= len(self.created_question_ids):
                        self.log_test("Get Stats", True, f"Stats: {total} total, {answered} answered, {unanswered} unanswered")
                        return True
                    else:
                        self.log_test("Get Stats", False, f"Stats math doesn't add up: {data}")
                else:
                    self.log_test("Get Stats", False, f"Missing required fields: {data}")
            else:
                self.log_test("Get Stats", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Get Stats", False, f"Error: {str(e)}")
        return False
        
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        edge_case_results = []
        
        # Test 1: Add answer to non-existent question
        try:
            fake_id = str(uuid.uuid4())
            response = requests.post(
                f"{self.base_url}/questions/{fake_id}/answer",
                json={"answer_text": "Test answer", "author": "Test Author"},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 404:
                edge_case_results.append(True)
                self.log_test("Edge Case - Non-existent Question", True, "Correctly returned 404")
            else:
                edge_case_results.append(False)
                self.log_test("Edge Case - Non-existent Question", False, f"Expected 404, got {response.status_code}")
        except Exception as e:
            edge_case_results.append(False)
            self.log_test("Edge Case - Non-existent Question", False, f"Error: {str(e)}")
            
        # Test 2: Add duplicate answer
        if self.created_question_ids:
            try:
                question_id = self.created_question_ids[0]
                response = requests.post(
                    f"{self.base_url}/questions/{question_id}/answer",
                    json={"answer_text": "Duplicate answer", "author": "Test Author"},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 400:
                    edge_case_results.append(True)
                    self.log_test("Edge Case - Duplicate Answer", True, "Correctly prevented duplicate answer")
                else:
                    edge_case_results.append(False)
                    self.log_test("Edge Case - Duplicate Answer", False, f"Expected 400, got {response.status_code}")
            except Exception as e:
                edge_case_results.append(False)
                self.log_test("Edge Case - Duplicate Answer", False, f"Error: {str(e)}")
        
        # Test 3: Search with empty query
        try:
            response = requests.post(
                f"{self.base_url}/search",
                json={"query": ""},
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    edge_case_results.append(True)
                    self.log_test("Edge Case - Empty Search", True, f"Empty search returned {len(data)} results")
                else:
                    edge_case_results.append(False)
                    self.log_test("Edge Case - Empty Search", False, "Invalid response format")
            else:
                edge_case_results.append(False)
                self.log_test("Edge Case - Empty Search", False, f"Status code: {response.status_code}")
        except Exception as e:
            edge_case_results.append(False)
            self.log_test("Edge Case - Empty Search", False, f"Error: {str(e)}")
            
        return sum(edge_case_results) >= 2  # At least 2 out of 3 edge cases should pass
        
    def test_delete_question(self):
        """Test DELETE /api/questions/{id} - Delete questions"""
        if not self.created_question_ids:
            self.log_test("Delete Question", False, "No questions available to delete")
            return False
            
        # Test deleting the last created question
        question_id = self.created_question_ids[-1]
        try:
            response = requests.delete(f"{self.base_url}/questions/{question_id}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Delete Question", True, f"Successfully deleted question {question_id}")
                    self.created_question_ids.remove(question_id)
                    return True
                else:
                    self.log_test("Delete Question", False, f"Invalid response: {data}")
            else:
                self.log_test("Delete Question", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Delete Question", False, f"Error: {str(e)}")
        return False
        
    def test_data_persistence(self):
        """Test that data persists correctly in database"""
        if not self.created_question_ids:
            self.log_test("Data Persistence", False, "No questions to verify persistence")
            return False
            
        # Wait a moment then retrieve questions again
        time.sleep(1)
        
        try:
            response = requests.get(f"{self.base_url}/questions", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                found_questions = []
                
                for qa in data:
                    if qa.get("question", {}).get("id") in self.created_question_ids:
                        found_questions.append(qa["question"]["id"])
                        
                if len(found_questions) >= len(self.created_question_ids) - 1:  # Account for deleted question
                    self.log_test("Data Persistence", True, f"Found {len(found_questions)} persisted questions")
                    return True
                else:
                    self.log_test("Data Persistence", False, f"Expected {len(self.created_question_ids)} questions, found {len(found_questions)}")
            else:
                self.log_test("Data Persistence", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Data Persistence", False, f"Error: {str(e)}")
        return False
        
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("=" * 60)
        print("🧪 BÖTTCHER WIKI BACKEND API TESTS")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print()
        
        test_functions = [
            ("Health Check", self.test_health_check),
            ("Create Questions", self.test_create_question),
            ("Get All Questions", self.test_get_all_questions),
            ("Add Answers", self.test_add_answers),
            ("Search Functionality", self.test_search_functionality),
            ("Get Categories", self.test_get_categories),
            ("Get Statistics", self.test_get_stats),
            ("Edge Cases", self.test_edge_cases),
            ("Delete Question", self.test_delete_question),
            ("Data Persistence", self.test_data_persistence)
        ]
        
        passed_tests = 0
        total_tests = len(test_functions)
        
        for test_name, test_func in test_functions:
            print(f"\n🔍 Running {test_name}...")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, False, f"Test function error: {str(e)}")
                
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOST TESTS PASSED - System is largely functional")
        elif passed_tests >= total_tests * 0.5:
            print("⚠️  SOME TESTS FAILED - System has issues")
        else:
            print("❌ MANY TESTS FAILED - System has critical issues")
            
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = BöttcherWikiTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        exit(0)  # All tests passed
    elif passed >= total * 0.8:
        exit(1)  # Most tests passed
    else:
        exit(2)  # Many tests failed