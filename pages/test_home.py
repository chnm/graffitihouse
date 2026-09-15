from datetime import date

from django.test import TestCase
from django.urls import reverse

from graffiti.models import GraffitiPhoto, GraffitiWall, Site


class HomePageMasonryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        site = Site.objects.create(name="Test site")
        for index in range(2):
            wall = GraffitiWall.objects.create(
                name=f"Wall {index}",
                image=f"images/wall-{index}.jpg",
                room="Test room",
                spatial_position=f"A{index}",
                wall_grid_position=f"A{index}",
                identifier=f"wall-{index}",
                date_taken=date(2026, 1, 1),
                site_id=site,
            )
            GraffitiPhoto.objects.create(
                graffiti_wall=wall,
                graffiti_type="drawing",
                image=f"images/derived/graffiti-{index}.jpg",
                identifier=f"graffiti-{index}",
            )

    def test_homepage_uses_three_random_wall_and_graffiti_images(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["masonry_images"]), 3)
        self.assertContains(response, 'loading="lazy"', count=3)
        self.assertNotContains(response, "Field records")

    def test_homepage_has_an_empty_state_when_no_images_exist(self):
        GraffitiPhoto.objects.all().delete()
        GraffitiWall.objects.all().delete()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["masonry_images"], [])
        self.assertContains(response, "images will appear here")
