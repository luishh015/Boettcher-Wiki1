#!/usr/bin/env python3
"""
Comprehensive File Upload System Tests for Böttcher Wiki
Tests file upload, download, validation, thumbnails, and attachment integration
"""

import requests
import json
import uuid
import base64
import io
from datetime import datetime
from PIL import Image
import os

# Get backend URL from environment
BACKEND_URL = "https://5f463c4f-105f-4102-90ec-a413bdeb91a6.preview.emergentagent.com/api"

class FileUploadTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.auth_token = None
        self.uploaded_files = []
        self.created_entries = []
        
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
        
    def authenticate(self):
        """Authenticate as admin to get token"""
        try:
            login_data = {
                "username": "admin",
                "password": "boettcher2024"
            }
            
            response = requests.post(
                f"{self.base_url}/admin/login",
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                if self.auth_token:
                    self.log_test("Authentication", True, f"Successfully authenticated as {data.get('username')}")
                    return True
                else:
                    self.log_test("Authentication", False, "No access token in response")
            else:
                self.log_test("Authentication", False, f"Status code: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Authentication", False, f"Error: {str(e)}")
        return False
        
    def get_auth_headers(self):
        """Get authorization headers"""
        if not self.auth_token:
            return {}
        return {"Authorization": f"Bearer {self.auth_token}"}
        
    def create_test_image(self, width=100, height=100, format='PNG'):
        """Create a test image file"""
        image = Image.new('RGB', (width, height), color='red')
        img_buffer = io.BytesIO()
        image.save(img_buffer, format=format)
        img_buffer.seek(0)
        return img_buffer.getvalue()
        
    def create_test_pdf(self):
        """Create a simple test PDF content"""
        # Simple PDF header (minimal valid PDF)
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
301
%%EOF"""
        return pdf_content
        
    def test_upload_without_auth(self):
        """Test file upload without authentication (should fail)"""
        try:
            # Create test image
            image_data = self.create_test_image()
            
            files = {
                'file': ('test_image.png', image_data, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                timeout=10
            )
            
            if response.status_code == 401:
                self.log_test("Upload Without Auth", True, "Correctly rejected unauthorized upload")
                return True
            else:
                self.log_test("Upload Without Auth", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Upload Without Auth", False, f"Error: {str(e)}")
        return False
        
    def test_upload_image_file(self):
        """Test uploading image files with thumbnail generation"""
        if not self.auth_token:
            self.log_test("Upload Image File", False, "No authentication token")
            return False
            
        try:
            # Create test image
            image_data = self.create_test_image(300, 200, 'PNG')
            
            files = {
                'file': ('test_image.png', image_data, 'image/png')
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'filename', 'file_type', 'file_size', 'content_type', 'file_data', 'uploaded_at']
                
                if all(field in data for field in required_fields):
                    # Check if thumbnail was generated for image
                    if data.get('thumbnail') and data.get('file_type') == 'images':
                        self.uploaded_files.append(data)
                        self.log_test("Upload Image File", True, f"Successfully uploaded image with thumbnail. ID: {data['id']}")
                        return True
                    else:
                        self.log_test("Upload Image File", False, "Image uploaded but no thumbnail generated")
                else:
                    self.log_test("Upload Image File", False, f"Missing required fields: {data}")
            else:
                self.log_test("Upload Image File", False, f"Status code: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Upload Image File", False, f"Error: {str(e)}")
        return False
        
    def test_upload_pdf_file(self):
        """Test uploading PDF files"""
        if not self.auth_token:
            self.log_test("Upload PDF File", False, "No authentication token")
            return False
            
        try:
            # Create test PDF
            pdf_data = self.create_test_pdf()
            
            files = {
                'file': ('test_document.pdf', pdf_data, 'application/pdf')
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ['id', 'filename', 'file_type', 'file_size', 'content_type', 'file_data', 'uploaded_at']
                
                if all(field in data for field in required_fields):
                    # PDF should not have thumbnail
                    if data.get('file_type') == 'documents' and not data.get('thumbnail'):
                        self.uploaded_files.append(data)
                        self.log_test("Upload PDF File", True, f"Successfully uploaded PDF. ID: {data['id']}")
                        return True
                    else:
                        self.log_test("Upload PDF File", False, f"Unexpected file type or thumbnail: {data}")
                else:
                    self.log_test("Upload PDF File", False, f"Missing required fields: {data}")
            else:
                self.log_test("Upload PDF File", False, f"Status code: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Upload PDF File", False, f"Error: {str(e)}")
        return False
        
    def test_file_size_validation(self):
        """Test file size validation (should reject files > 10MB)"""
        if not self.auth_token:
            self.log_test("File Size Validation", False, "No authentication token")
            return False
            
        try:
            # Create large file (11MB)
            large_data = b'x' * (11 * 1024 * 1024)
            
            files = {
                'file': ('large_file.txt', large_data, 'text/plain')
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=self.get_auth_headers(),
                timeout=30  # Longer timeout for large file
            )
            
            if response.status_code == 413:
                self.log_test("File Size Validation", True, "Correctly rejected file > 10MB")
                return True
            else:
                self.log_test("File Size Validation", False, f"Expected 413, got {response.status_code}")
                
        except Exception as e:
            self.log_test("File Size Validation", False, f"Error: {str(e)}")
        return False
        
    def test_file_type_validation(self):
        """Test file type validation (should reject unsupported types)"""
        if not self.auth_token:
            self.log_test("File Type Validation", False, "No authentication token")
            return False
            
        try:
            # Create unsupported file type
            unsupported_data = b'This is an unsupported file type'
            
            files = {
                'file': ('test.xyz', unsupported_data, 'application/xyz')
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            if response.status_code == 400:
                self.log_test("File Type Validation", True, "Correctly rejected unsupported file type")
                return True
            else:
                self.log_test("File Type Validation", False, f"Expected 400, got {response.status_code}")
                
        except Exception as e:
            self.log_test("File Type Validation", False, f"Error: {str(e)}")
        return False
        
    def test_empty_file_validation(self):
        """Test empty file validation"""
        if not self.auth_token:
            self.log_test("Empty File Validation", False, "No authentication token")
            return False
            
        try:
            # Create empty file
            empty_data = b''
            
            files = {
                'file': ('empty.txt', empty_data, 'text/plain')
            }
            
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            # Should either reject empty file or handle gracefully
            if response.status_code in [400, 413]:
                self.log_test("Empty File Validation", True, "Correctly handled empty file")
                return True
            elif response.status_code == 200:
                # If it accepts empty files, that's also valid
                self.log_test("Empty File Validation", True, "Accepted empty file (valid behavior)")
                return True
            else:
                self.log_test("Empty File Validation", False, f"Unexpected status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Empty File Validation", False, f"Error: {str(e)}")
        return False
        
    def test_create_knowledge_entry_with_attachments(self):
        """Test creating knowledge entries with file attachments"""
        if not self.auth_token or not self.uploaded_files:
            self.log_test("Knowledge Entry with Attachments", False, "No auth token or uploaded files")
            return False
            
        try:
            # Create knowledge entry with attachments
            entry_data = {
                "question": "Wie verwende ich die neue Schweißmaschine?",
                "answer": "Siehe beigefügte Anleitung und Sicherheitshinweise in den Dokumenten.",
                "category": "Produktion",
                "tags": ["schweißen", "anleitung", "sicherheit"],
                "attachments": self.uploaded_files[:2]  # Use first 2 uploaded files
            }
            
            response = requests.post(
                f"{self.base_url}/knowledge",
                json=entry_data,
                headers={**self.get_auth_headers(), "Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("id") and data.get("attachments"):
                    attachments = data["attachments"]
                    if len(attachments) == len(self.uploaded_files[:2]):
                        self.created_entries.append(data["id"])
                        self.log_test("Knowledge Entry with Attachments", True, f"Created entry with {len(attachments)} attachments")
                        return True
                    else:
                        self.log_test("Knowledge Entry with Attachments", False, f"Attachment count mismatch: {len(attachments)}")
                else:
                    self.log_test("Knowledge Entry with Attachments", False, "Missing ID or attachments in response")
            else:
                self.log_test("Knowledge Entry with Attachments", False, f"Status code: {response.status_code}, Response: {response.text}")
                
        except Exception as e:
            self.log_test("Knowledge Entry with Attachments", False, f"Error: {str(e)}")
        return False
        
    def test_retrieve_knowledge_with_attachments(self):
        """Test retrieving knowledge entries with attachments"""
        if not self.created_entries:
            self.log_test("Retrieve Knowledge with Attachments", False, "No entries with attachments created")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/knowledge", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Find our created entry
                entry_with_attachments = None
                for entry in data:
                    if entry.get("id") in self.created_entries and entry.get("attachments"):
                        entry_with_attachments = entry
                        break
                        
                if entry_with_attachments:
                    attachments = entry_with_attachments["attachments"]
                    # Verify attachment structure
                    required_attachment_fields = ['id', 'filename', 'file_type', 'file_size', 'content_type']
                    
                    if all(all(field in att for field in required_attachment_fields) for att in attachments):
                        self.log_test("Retrieve Knowledge with Attachments", True, f"Retrieved entry with {len(attachments)} properly structured attachments")
                        return True
                    else:
                        self.log_test("Retrieve Knowledge with Attachments", False, "Attachments missing required fields")
                else:
                    self.log_test("Retrieve Knowledge with Attachments", False, "Could not find entry with attachments")
            else:
                self.log_test("Retrieve Knowledge with Attachments", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Retrieve Knowledge with Attachments", False, f"Error: {str(e)}")
        return False
        
    def test_file_download(self):
        """Test file download functionality"""
        if not self.uploaded_files:
            self.log_test("File Download", False, "No uploaded files to download")
            return False
            
        try:
            # Try to download the first uploaded file
            file_id = self.uploaded_files[0]['id']
            
            response = requests.get(
                f"{self.base_url}/files/{file_id}/download",
                timeout=10
            )
            
            if response.status_code == 200:
                # Check headers
                content_disposition = response.headers.get('Content-Disposition', '')
                content_type = response.headers.get('Content-Type', '')
                
                if 'attachment' in content_disposition and content_type:
                    # Check if we got file content
                    if len(response.content) > 0:
                        self.log_test("File Download", True, f"Successfully downloaded file {file_id}")
                        return True
                    else:
                        self.log_test("File Download", False, "Downloaded file is empty")
                else:
                    self.log_test("File Download", False, f"Missing proper headers: {response.headers}")
            else:
                self.log_test("File Download", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("File Download", False, f"Error: {str(e)}")
        return False
        
    def test_download_nonexistent_file(self):
        """Test downloading non-existent file (should return 404)"""
        try:
            fake_file_id = str(uuid.uuid4())
            
            response = requests.get(
                f"{self.base_url}/files/{fake_file_id}/download",
                timeout=10
            )
            
            if response.status_code == 404:
                self.log_test("Download Non-existent File", True, "Correctly returned 404 for non-existent file")
                return True
            else:
                self.log_test("Download Non-existent File", False, f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Download Non-existent File", False, f"Error: {str(e)}")
        return False
        
    def test_stats_include_attachments(self):
        """Test that statistics include total_attachments count"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'total_attachments' in data:
                    total_attachments = data['total_attachments']
                    if isinstance(total_attachments, int) and total_attachments >= 0:
                        self.log_test("Stats Include Attachments", True, f"Stats include total_attachments: {total_attachments}")
                        return True
                    else:
                        self.log_test("Stats Include Attachments", False, f"Invalid total_attachments value: {total_attachments}")
                else:
                    self.log_test("Stats Include Attachments", False, "total_attachments field missing from stats")
            else:
                self.log_test("Stats Include Attachments", False, f"Status code: {response.status_code}")
                
        except Exception as e:
            self.log_test("Stats Include Attachments", False, f"Error: {str(e)}")
        return False
        
    def test_multiple_file_types(self):
        """Test uploading different file types"""
        if not self.auth_token:
            self.log_test("Multiple File Types", False, "No authentication token")
            return False
            
        test_files = [
            ('test.jpg', self.create_test_image(format='JPEG'), 'image/jpeg'),
            ('test.txt', b'This is a text file content', 'text/plain'),
            ('test.csv', b'name,age,city\nJohn,30,Berlin\nJane,25,Munich', 'text/csv')
        ]
        
        success_count = 0
        
        for filename, file_data, content_type in test_files:
            try:
                files = {
                    'file': (filename, file_data, content_type)
                }
                
                response = requests.post(
                    f"{self.base_url}/upload",
                    files=files,
                    headers=self.get_auth_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('filename') == filename:
                        success_count += 1
                        self.log_test(f"Upload {filename}", True, f"Successfully uploaded {filename}")
                    else:
                        self.log_test(f"Upload {filename}", False, "Filename mismatch in response")
                else:
                    self.log_test(f"Upload {filename}", False, f"Status code: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"Upload {filename}", False, f"Error: {str(e)}")
                
        if success_count >= 2:  # At least 2 out of 3 should work
            self.log_test("Multiple File Types", True, f"Successfully uploaded {success_count}/3 different file types")
            return True
        else:
            self.log_test("Multiple File Types", False, f"Only {success_count}/3 file types uploaded successfully")
            return False
        
    def run_all_tests(self):
        """Run all file upload tests in sequence"""
        print("=" * 70)
        print("📁 BÖTTCHER WIKI FILE UPLOAD SYSTEM TESTS")
        print("=" * 70)
        print(f"Testing against: {self.base_url}")
        print()
        
        # First authenticate
        if not self.authenticate():
            print("❌ Authentication failed - cannot proceed with file upload tests")
            return 0, 1
            
        test_functions = [
            ("Upload Without Auth", self.test_upload_without_auth),
            ("Upload Image File", self.test_upload_image_file),
            ("Upload PDF File", self.test_upload_pdf_file),
            ("File Size Validation", self.test_file_size_validation),
            ("File Type Validation", self.test_file_type_validation),
            ("Empty File Validation", self.test_empty_file_validation),
            ("Multiple File Types", self.test_multiple_file_types),
            ("Knowledge Entry with Attachments", self.test_create_knowledge_entry_with_attachments),
            ("Retrieve Knowledge with Attachments", self.test_retrieve_knowledge_with_attachments),
            ("File Download", self.test_file_download),
            ("Download Non-existent File", self.test_download_nonexistent_file),
            ("Stats Include Attachments", self.test_stats_include_attachments)
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
        print("📊 FILE UPLOAD TEST SUMMARY")
        print("=" * 70)
        print(f"Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 ALL FILE UPLOAD TESTS PASSED!")
        elif passed_tests >= total_tests * 0.8:
            print("✅ MOST FILE UPLOAD TESTS PASSED - System is largely functional")
        elif passed_tests >= total_tests * 0.5:
            print("⚠️  SOME FILE UPLOAD TESTS FAILED - System has issues")
        else:
            print("❌ MANY FILE UPLOAD TESTS FAILED - System has critical issues")
            
        return passed_tests, total_tests

if __name__ == "__main__":
    tester = FileUploadTester()
    passed, total = tester.run_all_tests()
    
    # Exit with appropriate code
    if passed == total:
        exit(0)  # All tests passed
    elif passed >= total * 0.8:
        exit(1)  # Most tests passed
    else:
        exit(2)  # Many tests failed