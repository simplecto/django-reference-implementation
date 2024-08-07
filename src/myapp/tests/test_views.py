from django.test import TestCase


class TestViews(TestCase):
    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")

    def test_health_check(self):
        response = self.client.get("/health-check/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")

    def test_flash_message(self):
        response = self.client.get("/?test_flash=true")
        messages = list(response.context["messages"])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "This is a test flash message.")
