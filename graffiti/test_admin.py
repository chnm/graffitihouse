from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from graffiti.models import GraffitiPhoto, GraffitiWall, Site


class GraffitiAdminTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )
        site = Site.objects.create(name="Test site")
        cls.wall = GraffitiWall.objects.create(
            name="Test wall",
            image="images/test-wall.jpg",
            room="Test room",
            spatial_position="A1",
            wall_grid_position="A1",
            identifier="wall-1",
            date_taken=date(2026, 1, 1),
            site_id=site,
        )
        GraffitiPhoto.objects.create(
            graffiti_wall=cls.wall,
            graffiti_type="drawing",
            identifier="photo-1",
        )

    def setUp(self):
        self.client.force_login(self.admin_user)

    def test_photo_changelist_renders_wall_link(self):
        response = self.client.get(reverse("admin:graffiti_graffitiphoto_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("admin:graffiti_graffitiwall_change", args=[self.wall.pk]),
        )

    def test_admin_sidebar_contains_project_navigation(self):
        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin/index.html")
        self.assertContains(response, 'id="nav-sidebar"')
        self.assertContains(response, "Project dashboard")
        self.assertContains(response, "Wall documentation")
        self.assertContains(response, "Research collections")
        self.assertContains(response, "People and access")
        groups = response.context["sidebar_navigation"]
        self.assertEqual(
            [group.get("title") for group in groups],
            [None, "Wall documentation", "Research collections", "People and access"],
        )
        links = {
            str(item["link"])
            for group in groups
            for item in group["items"]
            if item["has_permission"]
        }
        self.assertIn(
            reverse("admin:graffiti_graffitiwall_changelist"),
            links,
        )
        self.assertIn(reverse("admin:people_person_changelist"), links)
        self.assertIn(reverse("admin:accounts_customuser_changelist"), links)
        self.assertEqual(
            {
                stat["title"]: stat["value"]
                for stat in response.context["dashboard_stats"]
            },
            {"Walls": 1, "Graffiti photos": 1, "People": 0, "Sources": 0},
        )

    def test_wall_change_form_renders_image_widget(self):
        response = self.client.get(
            reverse("admin:graffiti_graffitiwall_change", args=[self.wall.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.wall.image.url)

    def test_derive_view_uses_unfold_admin_context(self):
        response = self.client.get(
            reverse("admin:derive-graffiti", args=[self.wall.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "Derive graffiti photo")
        self.assertContains(response, self.wall.image.url)
