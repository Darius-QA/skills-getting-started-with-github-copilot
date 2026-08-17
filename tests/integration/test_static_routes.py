"""
Integration tests for static routes.

Tests the root endpoint (GET /) and static file serving.
All tests follow the AAA (Arrange-Act-Assert) pattern.
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        ARRANGE: Client fixture with fresh app
        ACT: Make GET request to /
        ASSERT: Response is a redirect to /static/index.html
        """
        # ACT: Request root endpoint
        response = client.get("/", follow_redirects=False)
        
        # ASSERT: Verify redirect response
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers.get("location", "")
    
    def test_root_follow_redirect_reaches_static_page(self, client):
        """
        ARRANGE: Client fixture
        ACT: Make GET request to / with follow_redirects=True
        ASSERT: Final response is the static index.html page
        """
        # ACT: Request root endpoint and follow redirects
        response = client.get("/", follow_redirects=True)
        
        # ASSERT: Verify we get the static page
        assert response.status_code == 200
        # ASSERT: Verify HTML content is returned
        assert "text/html" in response.headers.get("content-type", "")


class TestStaticFilesServing:
    """Tests for static file serving"""
    
    def test_static_files_directory_mounted(self, client):
        """
        ARRANGE: Client fixture with app that has static files mounted
        ACT: Request a static file path
        ASSERT: Static files directory is properly mounted and accessible
        """
        # ACT: Try to access a static file (index.html)
        response = client.get("/static/index.html")
        
        # ASSERT: Verify successful response
        assert response.status_code == 200
    
    def test_static_index_html_content_type(self, client):
        """
        ARRANGE: Client fixture
        ACT: Request /static/index.html
        ASSERT: Response has correct HTML content-type
        """
        # ACT: Request static index.html
        response = client.get("/static/index.html")
        
        # ASSERT: Verify HTML content type
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
    
    def test_static_css_served(self, client):
        """
        ARRANGE: Client fixture
        ACT: Request static CSS file
        ASSERT: CSS file is served with correct content-type
        """
        # ACT: Request static CSS file
        response = client.get("/static/styles.css")
        
        # ASSERT: Verify CSS is served
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")
    
    def test_static_js_served(self, client):
        """
        ARRANGE: Client fixture
        ACT: Request static JavaScript file
        ASSERT: JavaScript file is served with correct content-type
        """
        # ACT: Request static JavaScript file
        response = client.get("/static/app.js")
        
        # ASSERT: Verify JavaScript is served
        assert response.status_code == 200
        assert "javascript" in response.headers.get("content-type", "").lower()
    
    def test_nonexistent_static_file_returns_404(self, client):
        """
        ARRANGE: Client fixture
        ACT: Request a static file that doesn't exist
        ASSERT: Request returns 404 error
        """
        # ACT: Request non-existent static file
        response = client.get("/static/nonexistent-file.txt")
        
        # ASSERT: Verify 404 error
        assert response.status_code == 404
