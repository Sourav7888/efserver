from core.tests.utils import BaseTest
from django.urls import reverse
from rest_framework import status
from django.contrib import auth


class ViewsTestCase(BaseTest):
    def test_get_generated_hc(self):
        self.client.login(username="CoreTestUser", password="123")
        url = reverse("get-generated-hc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = auth.get_user(self.client)
        user.is_superuser = True
        user.save()

        url = reverse("get-generated-hc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
