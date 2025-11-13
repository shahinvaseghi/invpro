from django.test import TestCase

from shared import models


class SharedModelTests(TestCase):
    def setUp(self):
        self.user = models.User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="secure-pass",
            first_name="Test",
            last_name="User",
        )
        self.company = models.Company.objects.create(
            public_code="00000001",
            legal_name="Test Legal Name Ltd.",
            display_name="Test Company",
            is_enabled=1,
        )
        self.access_level = models.AccessLevel.objects.create(
            code="inventory_manager",
            name="Inventory Manager",
            is_enabled=1,
        )

    def test_user_str_returns_full_name(self):
        self.assertEqual(str(self.user), "Test User")

    def test_company_str_returns_display_name(self):
        self.assertEqual(str(self.company), "Test Company")

    def test_person_auto_populates_company_code(self):
        person = models.Person.objects.create(
            company=self.company,
            public_code="00000001",
            username="person1",
            first_name="Ali",
            last_name="Ahmadi",
            is_enabled=1,
            sort_order=1,
        )
        self.assertEqual(person.company_code, self.company.public_code)

    def test_user_company_access_str(self):
        access = models.UserCompanyAccess.objects.create(
            user=self.user,
            company=self.company,
            access_level=self.access_level,
            is_enabled=1,
        )
        self.assertIn(self.company.display_name, str(access))
