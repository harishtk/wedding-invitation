import os
import unittest
from unittest.mock import patch
from app import create_app


class InvitationTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {'WEDDING_DATE': ''})
        self.env.start()
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 'test-only-secret', 'INVITATION_PASSWORD': 'test-password'})
        self.client = self.app.test_client()

    def tearDown(self):
        self.env.stop()

    def login(self, password='test-password'):
        self.client.get('/login')
        with self.client.session_transaction() as session:
            token = session['csrf']
        return self.client.post('/login', data={'csrf': token, 'password': password})

    def test_auth_and_pending_date(self):
        self.assertEqual(self.client.get('/').status_code, 302)
        self.assertEqual(self.client.get('/static/photos/private.jpg').status_code, 302)
        self.assertEqual(self.client.get('/health').status_code, 200)
        self.assertEqual(self.login('incorrect').status_code, 200)
        self.assertEqual(self.client.get('/').status_code, 302)
        self.assertEqual(self.login().status_code, 302)
        response = self.client.get('/')
        self.assertIn(b'An auspicious date', response.data)
        self.assertEqual(response.headers['Cache-Control'], 'no-store')

    def test_csrf_logout_and_password_rotation(self):
        self.assertEqual(self.client.post('/login', data={'password': 'test-password'}).status_code, 400)
        self.login()
        self.assertEqual(self.client.post('/logout').status_code, 400)
        with self.client.session_transaction() as session:
            token = session['csrf']
        self.client.post('/logout', data={'csrf': token})
        self.assertEqual(self.client.get('/').status_code, 302)
        self.login()
        self.app.config['INVITATION_PASSWORD'] = 'changed'
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_configuration(self):
        with self.assertRaises(RuntimeError):
            create_app({'SECRET_KEY': None})
        with patch.dict(os.environ, {'WEDDING_DATE': '2027-02-14T09:30:00'}):
            with self.assertRaises(ValueError):
                create_app(self.app.config)
        with patch.dict(os.environ, {'WEDDING_DATE': '2027-02-14T09:30:00+05:30'}):
            client = create_app(self.app.config).test_client()
            with client.session_transaction() as session:
                import hashlib, hmac
                session['access'] = hmac.new(b'test-only-secret', b'test-password', hashlib.sha256).hexdigest()
            response = client.get('/')
            self.assertIn(b'14 February 2027', response.data)
            self.assertIn(b'2027-02-14T09:30:00+05:30', response.data)


if __name__ == '__main__':
    unittest.main()
