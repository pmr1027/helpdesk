from server import app
import unittest

class Test(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def tearDown(self):
        pass

    def test_businesses_status_code(self):
        result = self.app.get('/businesses')
        self.assertEqual(result.status_code, 200)

    def test_events_status_code(self):
        result = self.app.get('/events')
        self.assertEqual(result.status_code, 200)

    def test_businesses_post(self):
        result = self.app.post('/businesses',data=dict(
        name='Unit Test',
        openingHours='Mon-Fri: 8:00-9:00',
        description='This is a unit test',
        cat=2,
        streetAddress='140 Test Street',
        postalCode=27514,
        state='NC',
        city='Chapel Hill'
    ), follow_redirects=True)
        assert b'Unit Test' in result.data
        self.assertEqual(result.status_code, 201)

    def test_businesses_post_fail(self):
        result = self.app.post('/businesses',data=dict(
        name='Unit Test',
        openingHours='Mon-Fri: 8:00-9:00',
        description='This is a unit test',
        cat=2,
        streetAddress='140 Test Street',
        postalCode=27514,
        city='Chapel Hill'
    ), follow_redirects=True)
        assert b'\'state\' is a required value' in result.data
        self.assertEqual(result.status_code, 400)

    # def test_events_post_pass(self):
    #     result = self.app.post('/events',data=dict(
    #     name='Unit Test Event',
    #     openingHours='Mon-Fri: 8:00-9:00',
    #     description='This is a unit test',
    #     cat=2,
    #     streetAddress='140 Test Street',
    #     postalCode=27514,
    #     state='NC',
    #     city='Chapel Hill'
    # ), follow_redirects=True)
    #     self.assertEqual(result.status_code, 400)

    def test_events_post_fail(self):
        result = self.app.post('/events',data=dict(
        name='Unit Test Event',
        openingHours='Mon-Fri: 8:00-9:00',
        description='This is a unit test',
        cat=2,
        streetAddress='140 Test Street',
        postalCode=27514,
        state='NC',
        city='Chapel Hill'
    ), follow_redirects=True)
        self.assertEqual(result.status_code, 400)


if __name__ == '__main__':
    unittest.main()
