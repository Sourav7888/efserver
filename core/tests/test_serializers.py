from core.tests.utils import BaseTest
from django.contrib.auth.models import User
from core.serializers import model_to_dict


class CoreTestCase(BaseTest):
    def test_model_to_dict(self):
        # Test that a model is converted to dict correctly
        user = User.objects.get(username="CoreTestUser")
        self.assertEqual(model_to_dict(user)["username"], "CoreTestUser")
