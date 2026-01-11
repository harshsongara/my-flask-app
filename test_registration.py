import requests
from bs4 import BeautifulSoup

# Base URL
BASE_URL = "http://localhost:5000"

# Start a session to maintain cookies
session = requests.Session()

print("Testing User Registration")
print("=" * 50)

# Step 1: Get the registration page to extract CSRF token
print("\n1. Fetching registration page...")
register_page = session.get(f"{BASE_URL}/register")
print(f"   Status: {register_page.status_code}")

# Parse HTML to get CSRF token
soup = BeautifulSoup(register_page.content, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']
print(f"   CSRF Token: {csrf_token[:20]}...")

# Step 2: Register a new user
print("\n2. Registering new user...")
test_user = {
    'username': 'testuser',
    'email': 'test@example.com',
    'password': 'TestPassword123!',
    'confirm_password': 'TestPassword123!',
    'csrf_token': csrf_token
}

register_response = session.post(
    f"{BASE_URL}/register",
    data=test_user,
    allow_redirects=False
)

print(f"   Status Code: {register_response.status_code}")
print(f"   Headers: {dict(register_response.headers)}")

if register_response.status_code == 302:
    print(f"   ✓ SUCCESS: User registered! Redirected to: {register_response.headers.get('Location')}")
elif register_response.status_code == 200:
    # Check for error messages
    soup = BeautifulSoup(register_response.content, 'html.parser')
    errors = soup.find_all('div', class_='alert')
    
    # Also check for field-specific errors
    field_errors = soup.find_all('span', class_='error-message')
    
    if errors or field_errors:
        print(f"   ✗ Registration failed with errors:")
        for error in errors:
            print(f"      - {error.text.strip()}")
        for error in field_errors:
            print(f"      - {error.text.strip()}")
    else:
        # Print the full response for debugging
        print(f"   ✗ Registration returned 200 but no redirect")
        print(f"   Response preview: {register_response.text[:500]}")
else:
    print(f"   ✗ Unexpected status code: {register_response.status_code}")
    print(f"   Response: {register_response.text[:500]}")

# Step 3: Verify user can login
print("\n3. Testing login with registered credentials...")
login_page = session.get(f"{BASE_URL}/login")
soup = BeautifulSoup(login_page.content, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

login_data = {
    'username': 'testuser',
    'password': 'TestPassword123!',
    'csrf_token': csrf_token
}

login_response = session.post(
    f"{BASE_URL}/login",
    data=login_data,
    allow_redirects=False
)

print(f"   Status Code: {login_response.status_code}")
if login_response.status_code == 302:
    print(f"   ✓ SUCCESS: Login successful! Redirected to: {login_response.headers.get('Location')}")
    
    # Step 4: Access dashboard
    print("\n4. Accessing dashboard...")
    dashboard = session.get(f"{BASE_URL}/dashboard")
    print(f"   Status Code: {dashboard.status_code}")
    
    if dashboard.status_code == 200:
        soup = BeautifulSoup(dashboard.content, 'html.parser')
        username_display = soup.find('span', class_='user-name')
        if username_display:
            print(f"   ✓ Dashboard loaded! Logged in as: {username_display.text}")
        else:
            print(f"   ✓ Dashboard loaded successfully")
    else:
        print(f"   ✗ Failed to access dashboard")
else:
    print(f"   ✗ Login failed")
    soup = BeautifulSoup(login_response.content, 'html.parser')
    errors = soup.find_all('div', class_='alert')
    if errors:
        for error in errors:
            print(f"      - {error.text.strip()}")

print("\n" + "=" * 50)
print("Test Complete!")
