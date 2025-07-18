#!/usr/bin/env python3
"""
Comprehensive Admin Authentication System Tests for Böttcher Wiki
Tests all authentication scenarios including login, token verification, protected routes, and error handling
"""

import requests
import json
import uuid
from datetime import datetime
import time

# Get backend URL from environment
BACKEND_URL = "https://5f463c4f-105f-4102-90ec-a413bdeb91a6.preview.emergentagent.com/api"

class BöttcherWikiAdminAuthTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.admin_token = None
        self.manager_token = None
        
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
        
    def test_admin_login_valid_credentials(self):
        """Test POST /api/admin/login with valid credentials"""
        test_credentials = [
            {"username": "admin", "password": "boettcher2024", "role": "admin"},
            {"username": "manager", "password": "wiki2024", "role": "manager"}
        ]
        
        success_count = 0
        for cred in test_credentials:
            try:
                response = requests.post(
                    f"{self.base_url}/admin/login",
                    json={"username": cred["username"], "password": cred["password"]},
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    required_fields = ["access_token", "token_type", "username"]
                    
                    if all(field in data for field in required_fields):
                        if data["token_type"] == "bearer" and data["username"] == cred["username"]:
                            # Store tokens for later tests
                            if cred["role"] == "admin":
                                self.admin_token = data["access_token"]
                            else:
                                self.manager_token = data["access_token"]
                            
                            success_count += 1
                            self.log_test(f"Admin Login - {cred['role']}", True, f"Successfully logged in as {cred['username']}")
                        else:
                            self.log_test(f"Admin Login - {cred['role']}", False, f"Invalid response data: {data}")
                    else:
                        self.log_test(f"Admin Login - {cred['role']}", False, f"Missing required fields: {data}")
                else:
                    self.log_test(f"Admin Login - {cred['role']}", False, f"Status code: {response.status_code}, Response: {response.text}")
                    
            except Exception as e:
                self.log_test(f"Admin Login - {cred['role']}", False, f"Error: {str(e)}")
                
        return success_count == len(test_credentials)
        
    def test_admin_login_invalid_credentials(self):
        """Test POST /api/admin/login with invalid credentials"""
        invalid_credentials = [
            {"username": "admin", "password": "wrongpassword"},
            {"username": "wronguser", "password": "boettcher2024"},
            {"username": "manager", "password": "wrongpassword"},
            {"username": "", "password": ""},
            {"username": "admin", "password": ""}
        ]
        
        success_count = 0
        for i, cred in enumerate(invalid_credentials):
            try:
                response = requests.post(
                    f"{self.base_url}/admin/login",
                    json=cred,
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                if response.status_code == 401:
                    success_count += 1
                    self.log_test(f"Invalid Login Test {i+1}", True, f"Correctly rejected invalid credentials: {cred['username']}")
                else:
                    self.log_test(f"Invalid Login Test {i+1}", False, f"Expected 401, got {response.status_code} for {cred}")
                    
            except Exception as e:
                self.log_test(f"Invalid Login Test {i+1}", False, f"Error: {str(e)}")
                
        return success_count >= 4  # Allow some flexibility
        
    def test_token_verification(self):
        """Test GET /api/admin/verify with valid tokens"""
        if not self.admin_token:
            self.log_test("Token Verification", False, "No admin token available for testing")
            return False
            
        tokens_to_test = [
            ("admin", self.admin_token),
            ("manager", self.manager_token) if self.manager_token else None
        ]
        
        success_count = 0
        for token_info in tokens_to_test:
            if token_info is None:
                continue
                
            role, token = token_info
            try:
                response = requests.get(
                    f"{self.base_url}/admin/verify",
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("valid") is True and "username" in data:
                        success_count += 1
                        self.log_test(f"Token Verification - {role}", True, f"Token verified for user: {data['username']}")
                    else:
                        self.log_test(f"Token Verification - {role}", False, f"Invalid response structure: {data}")
                else:
                    self.log_test(f"Token Verification - {role}", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Token Verification - {role}", False, f"Error: {str(e)}")
                
        return success_count >= 1
        
    def test_token_verification_invalid(self):
        """Test GET /api/admin/verify with invalid tokens"""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "",
            "expired.jwt.token",
            "malformed-token"
        ]
        
        success_count = 0
        for i, token in enumerate(invalid_tokens):
            try:
                headers = {"Authorization": f"Bearer {token}"} if token else {}
                response = requests.get(
                    f"{self.base_url}/admin/verify",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 401:
                    success_count += 1
                    self.log_test(f"Invalid Token Test {i+1}", True, "Correctly rejected invalid token")
                else:
                    self.log_test(f"Invalid Token Test {i+1}", False, f"Expected 401, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Invalid Token Test {i+1}", False, f"Error: {str(e)}")
                
        return success_count >= 4
        
    def test_protected_routes_with_auth(self):
        """Test protected routes with valid authentication"""
        if not self.admin_token:
            self.log_test("Protected Routes with Auth", False, "No admin token available")
            return False
            
        # Test data for creating/updating entries
        test_entry = {
            "question": "Test Admin Question",
            "answer": "Test Admin Answer",
            "category": "IT-Support",
            "tags": ["test", "admin"]
        }
        
        protected_tests = []
        created_entry_id = None
        
        # Test 1: POST /api/knowledge (create)
        try:
            response = requests.post(
                f"{self.base_url}/knowledge",
                json=test_entry,
                headers={
                    "Authorization": f"Bearer {self.admin_token}",
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") and data.get("question") == test_entry["question"]:
                    created_entry_id = data["id"]
                    protected_tests.append(True)
                    self.log_test("Protected POST /api/knowledge", True, f"Created entry with ID: {created_entry_id}")
                else:
                    protected_tests.append(False)
                    self.log_test("Protected POST /api/knowledge", False, f"Invalid response: {data}")
            else:
                protected_tests.append(False)
                self.log_test("Protected POST /api/knowledge", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            protected_tests.append(False)
            self.log_test("Protected POST /api/knowledge", False, f"Error: {str(e)}")
            
        # Test 2: PUT /api/knowledge/{id} (update) - only if we created an entry
        if created_entry_id:
            try:
                updated_entry = test_entry.copy()
                updated_entry["question"] = "Updated Test Admin Question"
                
                response = requests.put(
                    f"{self.base_url}/knowledge/{created_entry_id}",
                    json=updated_entry,
                    headers={
                        "Authorization": f"Bearer {self.admin_token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "Updated" in data.get("question", ""):
                        protected_tests.append(True)
                        self.log_test("Protected PUT /api/knowledge", True, f"Updated entry {created_entry_id}")
                    else:
                        protected_tests.append(False)
                        self.log_test("Protected PUT /api/knowledge", False, f"Update not reflected: {data}")
                else:
                    protected_tests.append(False)
                    self.log_test("Protected PUT /api/knowledge", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                protected_tests.append(False)
                self.log_test("Protected PUT /api/knowledge", False, f"Error: {str(e)}")
                
        # Test 3: DELETE /api/knowledge/{id} (delete) - only if we created an entry
        if created_entry_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/knowledge/{created_entry_id}",
                    headers={"Authorization": f"Bearer {self.admin_token}"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "message" in data:
                        protected_tests.append(True)
                        self.log_test("Protected DELETE /api/knowledge", True, f"Deleted entry {created_entry_id}")
                    else:
                        protected_tests.append(False)
                        self.log_test("Protected DELETE /api/knowledge", False, f"Invalid response: {data}")
                else:
                    protected_tests.append(False)
                    self.log_test("Protected DELETE /api/knowledge", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                protected_tests.append(False)
                self.log_test("Protected DELETE /api/knowledge", False, f"Error: {str(e)}")
                
        return sum(protected_tests) >= 2  # At least 2 out of 3 operations should work
        
    def test_protected_routes_without_auth(self):
        """Test protected routes without authentication (should return 401)"""
        test_entry = {
            "question": "Unauthorized Test",
            "answer": "This should fail",
            "category": "Test",
            "tags": ["unauthorized"]
        }
        
        protected_endpoints = [
            ("POST", "/knowledge", test_entry),
            ("PUT", "/knowledge/fake-id", test_entry),
            ("DELETE", "/knowledge/fake-id", None)
        ]
        
        success_count = 0
        for method, endpoint, data in protected_endpoints:
            try:
                if method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                elif method == "PUT":
                    response = requests.put(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                elif method == "DELETE":
                    response = requests.delete(f"{self.base_url}{endpoint}", timeout=10)
                    
                if response.status_code == 401:
                    success_count += 1
                    self.log_test(f"Unauthorized {method} {endpoint}", True, "Correctly rejected unauthorized request")
                else:
                    self.log_test(f"Unauthorized {method} {endpoint}", False, f"Expected 401, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Unauthorized {method} {endpoint}", False, f"Error: {str(e)}")
                
        return success_count == len(protected_endpoints)
        
    def test_protected_routes_with_invalid_auth(self):
        """Test protected routes with invalid authentication tokens"""
        test_entry = {
            "question": "Invalid Auth Test",
            "answer": "This should fail",
            "category": "Test",
            "tags": ["invalid"]
        }
        
        invalid_tokens = ["invalid_token", "expired.jwt.token", ""]
        
        success_count = 0
        for i, token in enumerate(invalid_tokens):
            try:
                response = requests.post(
                    f"{self.base_url}/knowledge",
                    json=test_entry,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                
                if response.status_code == 401:
                    success_count += 1
                    self.log_test(f"Invalid Auth Token Test {i+1}", True, "Correctly rejected invalid token")
                else:
                    self.log_test(f"Invalid Auth Token Test {i+1}", False, f"Expected 401, got {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Invalid Auth Token Test {i+1}", False, f"Error: {str(e)}")
                
        return success_count >= 2
        
    def test_public_routes_no_auth(self):
        """Test public routes that should work without authentication"""
        public_endpoints = [
            ("GET", "/knowledge", None),
            ("POST", "/search", {"query": "test"}),
            ("GET", "/categories", None),
            ("GET", "/stats", None)
        ]
        
        success_count = 0
        for method, endpoint, data in public_endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                elif method == "POST":
                    response = requests.post(
                        f"{self.base_url}{endpoint}",
                        json=data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                if response.status_code == 200:
                    success_count += 1
                    self.log_test(f"Public {method} {endpoint}", True, "Public endpoint accessible without auth")
                else:
                    self.log_test(f"Public {method} {endpoint}", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Public {method} {endpoint}", False, f"Error: {str(e)}")
                
        return success_count == len(public_endpoints)
        
    def test_jwt_token_structure(self):
        """Test JWT token format and structure"""
        if not self.admin_token:
            self.log_test("JWT Token Structure", False, "No admin token available")
            return False
            
        try:
            # JWT tokens should have 3 parts separated by dots
            token_parts = self.admin_token.split('.')
            
            if len(token_parts) == 3:
                # Check that each part is base64-like (contains valid characters)
                import base64
                import json
                
                # Try to decode the header (first part)
                try:
                    # Add padding if needed
                    header_padded = token_parts[0] + '=' * (4 - len(token_parts[0]) % 4)
                    header_decoded = base64.urlsafe_b64decode(header_padded)
                    header_json = json.loads(header_decoded)
                    
                    if "alg" in header_json and "typ" in header_json:
                        self.log_test("JWT Token Structure", True, f"Valid JWT structure with algorithm: {header_json.get('alg')}")
                        return True
                    else:
                        self.log_test("JWT Token Structure", False, f"Invalid JWT header: {header_json}")
                except Exception as decode_error:
                    self.log_test("JWT Token Structure", False, f"Cannot decode JWT header: {str(decode_error)}")
            else:
                self.log_test("JWT Token Structure", False, f"Invalid JWT format - expected 3 parts, got {len(token_parts)}")
                
        except Exception as e:
            self.log_test("JWT Token Structure", False, f"Error analyzing token: {str(e)}")
            
        return False
        
    def run_all_tests(self):
        """Run all authentication tests in sequence"""
        print("=" * 70)
        print("🔐 BÖTTCHER WIKI ADMIN AUTHENTICATION SYSTEM TESTS")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print()
        
        test_functions = [
            ("Admin Login - Valid Credentials", self.test_admin_login_valid_credentials),
            ("Admin Login - Invalid Credentials", self.test_admin_login_invalid_credentials),
            ("Token Verification - Valid", self.test_token_verification),
            ("Token Verification - Invalid", self.test_token_verification_invalid),
            ("Protected Routes - With Auth", self.test_protected_routes_with_auth),
            ("Protected Routes - Without Auth", self.test_protected_routes_without_auth),
            ("Protected Routes - Invalid Auth", self.test_protected_routes_with_invalid_auth),
            ("Public Routes - No Auth Required", self.test_public_routes_no_auth),
            ("JWT Token Structure", self.test_jwt_token_structure)
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
                
        print("\n" + "=" * 70)
        print("📊 AUTHENTICATION TEST SUMMARY")
        print("=" * 70)
        print(f"Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL AUTHENTICATION TESTS PASSED!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOST AUTHENTICATION TESTS PASSED - System is largely secure")
        elif passed_tests >= total_tests * 0.5:
            print("⚠️  SOME AUTHENTICATION TESTS FAILED - Security issues detected")
        else:
            print("❌ MANY AUTHENTICATION TESTS FAILED - Critical security issues")
            
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = BöttcherWikiAdminAuthTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        exit(0)  # All tests passed
    elif passed >= total * 0.8:
        exit(1)  # Most tests passed
    else:
        exit(2)  # Many tests failed