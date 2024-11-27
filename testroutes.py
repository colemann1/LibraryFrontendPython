import unittest
import os
from flask import Flask
from frontend import app  # Import the Flask app from frontend.py

# Mocked file paths for testing
TEST_BOOK_FILE_PATH = 'TestData/Books.csv'
TEST_USER_FILE_PATH = 'TestData/Users.csv'
TEST_CHECKOUT_FILE_PATH = 'TestData/Checkouts.csv'

class FlaskTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Modify the app config for testing
        app.config['BOOK_FILE_PATH'] = TEST_BOOK_FILE_PATH
        app.config['USER_FILE_PATH'] = TEST_USER_FILE_PATH
        app.config['CHECKOUT_FILE_PATH'] = TEST_CHECKOUT_FILE_PATH
        app.config['TESTING'] = True  # Enable testing mode
        app.secret_key = 'test_secret_key'
        
    def setUp(self):
        #Before each test,  initialize a Flask test client
        self.client = app.test_client()

    def tearDown(self):
        # Clean up after each test.
        if os.path.exists(TEST_BOOK_FILE_PATH):
            os.remove(TEST_BOOK_FILE_PATH)
        
        if os.path.exists(TEST_USER_FILE_PATH):
            os.remove(TEST_USER_FILE_PATH)
        
        if os.path.exists(TEST_CHECKOUT_FILE_PATH):
            os.remove(TEST_CHECKOUT_FILE_PATH)
            
    def test_add_book(self):
        #Test adding a book.
        response = self.client.post('/addbook', data={
            'title': 'Test Book',
            'author': 'Author Name',
            'isbn': '1234567890'
        })
        self.assertEqual(response.status_code, 302)  # Check redirect after post
        
    def test_add_book_invalid(self):
        # Test adding a book with missing fields.
        response = self.client.post('/addbook', data={
            'title': '',
            'author': 'Author Name',
            'isbn': '1234567890'
        })
        self.assertEqual(response.status_code, 200)
        
    def test_all_books(self):
        #Test displaying all books.
        response = self.client.get('/all_books')
        self.assertEqual(response.status_code, 302)

    def test_edit_book(self):
        # Test editing a book.
        # Assuming a book with ID 1 exists
        response = self.client.post('/edit_book/1', data={
            'title': 'Updated Book Title',
            'author': 'Updated Author',
            'isbn': '9876543210'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect

    def test_delete_book(self):
        # Test deleting a book.
        # Assuming a book with ID 1 exists
        response = self.client.post('/delete_book/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        # Test adding a user.
        response = self.client.post('/add_user', data={
            'name': 'Test User',
            'email': 'testuser@example.com'
        })
        self.assertEqual(response.status_code, 302)

    def test_add_user_invalid(self):
        # Test adding a user with invalid data.
        response = self.client.post('/add_user', data={
            'name': '',
            'email': 'testuser@example.com'
        })
        self.assertEqual(response.status_code, 200)
        
    def test_checkout_book(self):
        # Test checking out a book.
        # Assuming a book with ID 1 exists and is available
        response = self.client.post('/checkout_book/1', data={
            'user_id': '1'
        })
        self.assertEqual(response.status_code, 302)  # Check for redirect

    def test_return_book(self):
        # Test returning a book.
        # Assuming a book with ID 1 Checked out
        response = self.client.post('/return_book/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_checkout_book_invalid_user(self):
        # Test checking out a book with an invalid user.
        response = self.client.post('/checkout_book/1', data={
            'user_id': '9999'  # Assume user doesn't exist
        })
        self.assertEqual(response.status_code, 302)
