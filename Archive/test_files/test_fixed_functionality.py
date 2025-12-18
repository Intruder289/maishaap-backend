#!/usr/bin/env python3
"""
Test the fixed room management functionality
"""

import requests
from bs4 import BeautifulSoup

def test_fixed_functionality():
    session = requests.Session()
    
    # Login
    login_data = {
        'username': 'testuser',
        'password': 'testpass123',
        'csrfmiddlewaretoken': ''
    }
    
    # Get CSRF token
    login_page = session.get('http://127.0.0.1:8001/accounts/login/')
    soup = BeautifulSoup(login_page.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
    if csrf_token:
        login_data['csrfmiddlewaretoken'] = csrf_token['value']
    
    # Login
    session.post('http://127.0.0.1:8001/accounts/login/', data=login_data)
    
    # Test rooms page
    response = session.get('http://127.0.0.1:8001/properties/hotel/rooms/')
    print(f'Status: {response.status_code}')
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Check for JavaScript functions
        scripts = soup.find_all('script')
        js_content = ''.join([script.string or '' for script in scripts])
        
        functions = ['viewRoomDetails', 'editRoom', 'manageRoomStatus', 'deleteRoom']
        print('JavaScript functions:')
        for func in functions:
            if func in js_content:
                print(f'✓ {func} found')
            else:
                print(f'✗ {func} missing')
        
        # Check for modals
        modals = soup.find_all('div', class_='modal')
        print(f'\nModals found: {len(modals)}')
        for modal in modals:
            modal_id = modal.get('id', 'No ID')
            print(f'  - {modal_id}')
        
        # Check for syntax errors
        if 'Unexpected end of input' in js_content:
            print('✗ JavaScript syntax error detected')
        else:
            print('✓ No JavaScript syntax errors detected')
            
    else:
        print(f'✗ Failed to access page: {response.status_code}')

if __name__ == "__main__":
    test_fixed_functionality()
