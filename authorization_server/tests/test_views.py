from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse
from authorization_server.models import Role, Permission, Platform, User as AuthUser

# Create your tests here.


class ViewsTestCase(TestCase):
    data = {
        "user": {"username": "CoreTestUser", "password": "123"},
    }

    def setUp(self):

        # User by default acces_level="RESTRICTED" and customer will be null
        User.objects.create_user(**self.data["user"])
        self.client.login(**self.data["user"])

    def test_get_user_info(self):
        auth_user = AuthUser.objects.create(
            user_id="TestUsername", email="TestUser@email.com"
        )

        url = reverse(
            "authorization_server_get_user_info", kwargs={"user_id": "TestUsername"}
        )
        response = self.client.get(
            url,
        )

        # Only super user has access
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        roles = Role.objects.create(role_name="TestRole")
        perms = Permission.objects.create(permission_name="TestPermission")
        plats = Platform.objects.create(platform_name="TestPlatform")

        user = User.objects.get(username=self.data["user"]["username"])
        user.is_superuser = True
        user.save()

        auth_user.roles.add(roles)
        auth_user.permissions.add(perms)
        auth_user.platforms.add(plats)
        auth_user.save()

        # Lest create some access control

        response = self.client.get(
            url,
        )

        # Only super user has access
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user_id"], "TestUsername")
        self.assertEqual(response.data["email"], "TestUser@email.com")
        self.assertEqual(response.data["roles"], ["TestRole"])
        self.assertEqual(response.data["permissions"], ["TestPermission"])
        self.assertEqual(response.data["platforms"], ["TestPlatform"])

        return response
