from django.test import TestCase


class CommonViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
