from django.test import TestCase


class GraffitiTest(TestCase):
    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # def test_view(self):
    #     response = self.client.get('/graffiti/')
    #     self.assertEqual(response.status_code, 200)