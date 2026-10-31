import unittest
from app import app
from database import init_db, get_db

class DCoolCafeTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'D COOL CAFE', response.data)
        self.assertIn(b'@d_cool_cafe', response.data)
        self.assertIn(b'vintage vibe', response.data.lower())

    def test_menu_page(self):
        response = self.client.get('/menu')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Signature Cold Coffee', response.data)
        self.assertIn(b'Handcrafted Pizzas', response.data)

    def test_menu_category_filter(self):
        response = self.client.get('/menu?category=Handcrafted+Pizzas')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Margherita Gold Pizza', response.data)

    def test_reservation_page(self):
        response = self.client.get('/reserve')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Reserve Your Table', response.data)

    def test_reservation_submit(self):
        payload = {
            'guest_name': 'Subham Mishra',
            'email': 'subham@example.com',
            'phone': '9876543210',
            'reservation_date': '2026-11-01',
            'reservation_time': '07:00 PM',
            'guests_count': 4,
            'occasion': 'Birthday Celebration',
            'special_requests': 'Please arrange balloons and birthday music track.'
        }
        response = self.client.post('/reserve', data=payload, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Subham Mishra', response.data)
        self.assertIn(b'Booking Confirmed', response.data)

    def test_gallery_page(self):
        response = self.client.get('/gallery')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The Vintage Gallery', response.data)
        self.assertIn(b'd_cool_cafe', response.data)

    def test_about_page(self):
        response = self.client.get('/about')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Brewed with Love in Burla', response.data)

    def test_contact_page(self):
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Daily Market, Near NAC Office', response.data)

    def test_api_menu(self):
        response = self.client.get('/api/menu')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('items', json_data)
        self.assertTrue(len(json_data['items']) > 0)

    def test_api_status(self):
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn('is_open', json_data)
        self.assertIn('hours', json_data)

    def test_admin_flow(self):
        # Visit login
        res = self.client.get('/admin/login')
        self.assertEqual(res.status_code, 200)
        
        # Post correct login credentials
        res = self.client.post('/admin/login', data={'username': 'admin', 'password': 'dcool123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'D Cool Cafe Operations', response_data := res.data)

if __name__ == '__main__':
    unittest.main()
