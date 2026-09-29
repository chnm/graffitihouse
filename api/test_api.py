import datetime
import io

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.urls import Resolver404, resolve, reverse
from rest_framework.throttling import AnonRateThrottle

from graffiti.models import GraffitiPhoto, GraffitiWall, Location, Site
from people.models import Alias, Organization, Person, Service

INTERNAL_FIELDS = {
    "notes",
    "conservation_notes",
    "created_by",
    "history",
    "interpretation",
    "coordinates",
}
ENDPOINTS = ["site", "location", "wall", "photo", "person"]


@pytest.fixture(autouse=True)
def reset_throttle():
    # Throttle counts live in the cache, which outlives each test.
    cache.clear()
    yield
    cache.clear()


def make_location(**kwargs):
    # Coordinates are required here: without them `save` calls the geocoder.
    return Location.objects.create(
        place=kwargs.pop("place", "Graffiti House"),
        city=kwargs.pop("city", "Brandy Station"),
        state=kwargs.pop("state", "Virginia"),
        latitude=38.4956,
        longitude=-77.887,
        **kwargs,
    )


def make_site(name="Site", **kwargs):
    return Site.objects.create(name=name, **kwargs)


def make_wall(site, n=1, **kwargs):
    return GraffitiWall.objects.create(
        name=kwargs.pop("name", f"Wall {n}"),
        image="images/wall.jpg",
        room=kwargs.pop("room", "100"),
        spatial_position="A1",
        wall_grid_position="A1",
        identifier=f"W{n}",
        date_taken=kwargs.pop("date_taken", datetime.date(2020, 1, 1)),
        site_id=site,
        notes="internal note",
        conservation_notes="conservation note",
        interpretation="internal interpretation",
        **kwargs,
    )


def make_photo(wall, n=1, **kwargs):
    return GraffitiPhoto.objects.create(
        graffiti_wall=wall,
        identifier=f"IMG_{wall.pk}_{n}",
        graffiti_type=kwargs.pop("graffiti_type", "name"),
        description="<p>Capt J. Marshall</p>",
        x=10,
        y=20,
        width=30,
        height=40,
        coordinates={"leaflet": {}},
        **kwargs,
    )


def make_person(last_name="Marshall", governance="confederacy", photos=()):
    person = Person.objects.create(first_name="J.", last_name=last_name)
    Alias.objects.create(person=person, name=f"{last_name} alias")
    Organization.objects.create(person=person, name="12th Virginia Cavalry")
    Service.objects.create(
        person=person,
        military_rank="captain",
        military_unit="Co. E",
        military_branch="army",
        military_division="cavalry",
        military_governance=governance,
    )
    person.associated_graffiti_photos.set(photos)
    person.tags.add("officer")
    return person


@pytest.fixture
def data():
    site = make_site(name="Graffiti House", location=make_location())
    site.tags.add("house")
    wall = make_wall(site)
    wall.tags.add("charcoal")
    photo = make_photo(wall)
    photo.tags.add("signature")
    person = make_person(photos=[photo])
    return {
        "site": site,
        "location": site.location,
        "wall": wall,
        "photo": photo,
        "person": person,
    }


def list_url(basename, **query):
    url = reverse(f"api:{basename}-list")
    if query:
        url += "?" + "&".join(f"{key}={value}" for key, value in query.items())
    return url


def detail_url(basename, pk):
    return reverse(f"api:{basename}-detail", args=[pk])


def result_ids(response):
    return [item["id"] for item in response.json()["results"]]


def all_keys(value):
    """Every key anywhere in a JSON value, including nested objects."""
    if isinstance(value, dict):
        return set(value) | {k for v in value.values() for k in all_keys(v)}
    if isinstance(value, list):
        return {k for v in value for k in all_keys(v)}
    return set()


# Reading -----------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.parametrize("basename", ENDPOINTS)
def test_list_and_detail_are_public(client, data, basename):
    instance = data[basename]

    listing = client.get(list_url(basename))
    detail = client.get(detail_url(basename, instance.pk))

    assert listing.status_code == 200
    assert listing["Content-Type"] == "application/json"
    assert set(listing.json()) == {"count", "next", "previous", "results"}
    assert result_ids(listing) == [instance.pk]
    assert detail.status_code == 200
    assert detail.json()["id"] == instance.pk
    assert detail.json()["url"].endswith(detail_url(basename, instance.pk))


@pytest.mark.django_db
@pytest.mark.parametrize("basename", ENDPOINTS)
def test_internal_fields_are_never_exposed(client, data, basename):
    body = client.get(detail_url(basename, data[basename].pk)).json()

    assert not all_keys(body) & INTERNAL_FIELDS
    assert "internal" not in str(body)
    assert "conservation note" not in str(body)


@pytest.mark.django_db
def test_site_detail_nests_location_and_counts(client, data):
    body = client.get(detail_url("site", data["site"].pk)).json()

    assert body["html_url"] == f"http://testserver/graffiti/site/{data['site'].pk}/"
    assert body["location"]["place"] == "Graffiti House"
    assert body["location"]["latitude"] == 38.4956
    assert body["image"] is None
    assert body["tags"] == ["house"]
    assert (body["wall_count"], body["photo_count"]) == (1, 1)


@pytest.mark.django_db
def test_wall_detail_links_site_and_absolute_images(client, data):
    wall = data["wall"]
    body = client.get(detail_url("wall", wall.pk)).json()

    assert body["site"] == data["site"].pk
    assert body["site_url"] == f"http://testserver/api/v1/sites/{data['site'].pk}/"
    assert body["html_url"] == f"http://testserver/graffiti/wall/{wall.pk}/"
    assert body["image"] == "http://testserver/media/images/wall.jpg"
    assert body["archival_image"] is None
    assert body["tags"] == ["charcoal"]
    assert body["photo_count"] == 1


@pytest.mark.django_db
def test_photo_detail_includes_crop_type_label_and_people(client, data):
    photo, person = data["photo"], data["person"]
    body = client.get(detail_url("photo", photo.pk)).json()

    assert body["wall"] == data["wall"].pk
    assert body["site"] == data["site"].pk
    assert body["graffiti_type"] == "name"
    assert body["graffiti_type_display"] == "name"
    assert body["description"] == "<p>Capt J. Marshall</p>"
    assert body["crop"] == {"x": 10, "y": 20, "width": 30, "height": 40}
    assert body["html_url"].endswith(f"/graffiti/derived-image/{photo.pk}/")
    assert body["people"] == [
        {"id": person.pk, "url": f"http://testserver/api/v1/people/{person.pk}/"}
    ]


@pytest.mark.django_db
def test_photo_without_rectangle_or_type_reports_nulls(client, data):
    photo = GraffitiPhoto.objects.create(
        graffiti_wall=data["wall"], identifier="IMG_bare"
    )
    body = client.get(detail_url("photo", photo.pk)).json()

    assert body["crop"] is None
    assert body["graffiti_type"] is None
    assert body["graffiti_type_display"] is None
    assert body["image"] is None


@pytest.mark.django_db
def test_person_detail_nests_aliases_organizations_service_and_photos(client, data):
    person, photo = data["person"], data["photo"]
    body = client.get(detail_url("person", person.pk)).json()

    assert body["html_url"] == f"http://testserver/people/{person.pk}/"
    assert [alias["name"] for alias in body["aliases"]] == ["Marshall alias"]
    assert [org["name"] for org in body["organizations"]] == ["12th Virginia Cavalry"]
    assert body["photos"] == [
        {"id": photo.pk, "url": f"http://testserver/api/v1/photos/{photo.pk}/"}
    ]
    [service] = body["service"]
    assert service["military_rank"] == "captain"
    assert service["military_rank_display"] == "Captain"
    assert service["army_branch"] == "cavalry"
    assert service["army_branch_display"] == "Cavalry"
    assert service["military_governance_display"] == "Confederacy"
    assert "military_division" not in service
    assert body["tags"] == ["officer"]


@pytest.mark.django_db
def test_blank_choices_are_null(client):
    person = Person.objects.create(last_name="Doe")
    Service.objects.create(person=person)

    [service] = client.get(detail_url("person", person.pk)).json()["service"]

    assert service["military_rank"] is None
    assert service["military_rank_display"] is None
    assert service["army_branch"] is None


# Writing -----------------------------------------------------------------------

WRITES = [
    ("post", False),
    ("put", True),
    ("patch", True),
    ("delete", True),
]


@pytest.mark.django_db
@pytest.mark.parametrize("basename", ENDPOINTS)
@pytest.mark.parametrize("method,on_detail", WRITES)
def test_writes_are_rejected_for_anonymous(client, data, basename, method, on_detail):
    url = detail_url(basename, data[basename].pk) if on_detail else list_url(basename)

    response = getattr(client, method)(url, {}, content_type="application/json")

    assert response.status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize("basename", ENDPOINTS)
@pytest.mark.parametrize("method,on_detail", WRITES)
def test_writes_are_rejected_for_superusers(
    admin_client, data, basename, method, on_detail
):
    instance = data[basename]
    url = detail_url(basename, instance.pk) if on_detail else list_url(basename)

    response = getattr(admin_client, method)(url, {}, content_type="application/json")

    assert response.status_code in (403, 405)
    assert type(instance).objects.filter(pk=instance.pk).exists()


@pytest.mark.django_db
def test_schema_has_no_write_operations(client):
    schema = client.get(reverse("api:schema"), {"format": "json"}).json()

    methods = {
        method for operations in schema["paths"].values() for method in operations
    }

    assert methods == {"get"}


# Routing -----------------------------------------------------------------------


def test_ancillary_sources_are_not_routed(client):
    root = client.get("/api/v1/").json()

    assert set(root) == {"sites", "locations", "walls", "photos", "people"}
    for path in ("sources", "ancillary-sources", "archives"):
        with pytest.raises(Resolver404):
            resolve(f"/api/v1/{path}/")


@pytest.mark.django_db
def test_schema_and_docs_are_served(client):
    assert client.get(reverse("api:schema")).status_code == 200
    docs = client.get(reverse("api:docs"))
    assert docs.status_code == 200
    # Swagger UI comes from the bundled sidecar, not a CDN.
    assert b"drf_spectacular_sidecar" in docs.content


def test_schema_generates_without_warnings():
    call_command("spectacular", "--validate", "--fail-on-warn", stdout=io.StringIO())


@pytest.mark.django_db
def test_cors_allows_any_origin_for_api_reads_only(client):
    api = client.get("/api/v1/", headers={"Origin": "https://viz.example.org"})
    site = client.get("/graffiti/", headers={"Origin": "https://viz.example.org"})

    assert api["Access-Control-Allow-Origin"] == "*"
    assert "Access-Control-Allow-Credentials" not in api
    assert "Access-Control-Allow-Origin" not in site


def test_anonymous_requests_are_throttled(client, monkeypatch):
    monkeypatch.setitem(AnonRateThrottle.THROTTLE_RATES, "anon", "2/minute")

    statuses = [client.get("/api/v1/").status_code for _ in range(3)]

    assert statuses == [200, 200, 429]


# Pagination --------------------------------------------------------------------


@pytest.mark.django_db
def test_pagination_defaults_to_fifty_and_caps_page_size(client):
    site = make_site()
    GraffitiWall.objects.bulk_create(
        GraffitiWall(
            name=f"Wall {n}",
            image="images/wall.jpg",
            room="1",
            spatial_position="A1",
            wall_grid_position="A1",
            identifier=f"W{n}",
            date_taken=datetime.date(2020, 1, 1),
            site_id=site,
        )
        for n in range(501)
    )

    default = client.get(list_url("wall")).json()
    small = client.get(list_url("wall", page_size=5, page=2)).json()
    capped = client.get(list_url("wall", page_size=10_000)).json()

    assert default["count"] == 501
    assert len(default["results"]) == 50
    assert len(small["results"]) == 5 and small["previous"] and small["next"]
    assert len(capped["results"]) == 500


# Filtering ---------------------------------------------------------------------


@pytest.mark.django_db
def test_location_filters(client):
    virginia = make_location(state="Virginia")
    make_location(place="Elsewhere", city="Frederick", state="Maryland")

    assert result_ids(client.get(list_url("location", state="virginia"))) == [
        virginia.pk
    ]


@pytest.mark.django_db
def test_site_filters_and_search(client):
    house = make_site(name="Graffiti House", location=make_location())
    blenheim = make_site(name="Historic Blenheim")
    blenheim.tags.add("house museum")

    assert result_ids(client.get(list_url("site", state="Virginia"))) == [house.pk]
    assert result_ids(client.get(list_url("site", search="blenheim"))) == [blenheim.pk]
    assert result_ids(client.get(list_url("site", tag="House%20Museum"))) == [
        blenheim.pk
    ]


@pytest.mark.django_db
def test_wall_filters_search_and_ordering(client):
    first, second = make_site(name="First"), make_site(name="Second")
    old = make_wall(first, 1, date_taken=datetime.date(2019, 5, 1))
    new = make_wall(first, 2, room="200", date_taken=datetime.date(2024, 5, 1))
    other = make_wall(second, 3, name="Parlor")

    assert result_ids(client.get(list_url("wall", site=first.pk))) == [old.pk, new.pk]
    assert result_ids(client.get(list_url("wall", room="200"))) == [new.pk]
    assert result_ids(client.get(list_url("wall", date_taken_after="2023-01-01"))) == [
        new.pk
    ]
    assert result_ids(client.get(list_url("wall", search="parlor"))) == [other.pk]
    assert result_ids(
        client.get(list_url("wall", site=first.pk, ordering="-date_taken"))
    ) == [new.pk, old.pk]


@pytest.mark.django_db
def test_photo_filters(client):
    first, second = make_site(name="First"), make_site(name="Second")
    wall_a, wall_b = make_wall(first, 1), make_wall(second, 2)
    name = make_photo(wall_a, 1, graffiti_type="name")
    poem = make_photo(wall_a, 2, graffiti_type="poetry")
    elsewhere = make_photo(wall_b, 3)
    person = make_person(photos=[poem, elsewhere])

    assert result_ids(client.get(list_url("photo", wall=wall_a.pk))) == [
        name.pk,
        poem.pk,
    ]
    assert result_ids(client.get(list_url("photo", site=second.pk))) == [elsewhere.pk]
    assert result_ids(client.get(list_url("photo", graffiti_type="poetry"))) == [
        poem.pk
    ]
    assert result_ids(client.get(list_url("photo", person=person.pk))) == [
        poem.pk,
        elsewhere.pk,
    ]
    assert client.get(list_url("photo", graffiti_type="bogus")).status_code == 400


@pytest.mark.django_db
def test_person_filters_and_search(client):
    union = make_person(last_name="Adams", governance="union")
    Service.objects.create(person=union, military_governance="union")
    confederate = make_person(last_name="Baker", governance="confederacy")

    assert result_ids(client.get(list_url("person", governance="union"))) == [union.pk]
    assert result_ids(client.get(list_url("person", rank="captain"))) == [
        union.pk,
        confederate.pk,
    ]
    assert result_ids(client.get(list_url("person", search="baker%20alias"))) == [
        confederate.pk
    ]


# Performance -------------------------------------------------------------------


@pytest.fixture
def many_rows():
    for s in range(3):
        site = make_site(name=f"Site {s}", location=make_location(place=f"P{s}"))
        site.tags.add("a", "b")
        for w in range(3):
            wall = make_wall(site, s * 10 + w)
            wall.tags.add("c")
            photos = [make_photo(wall, p) for p in range(2)]
            for photo in photos:
                photo.tags.add("d")
            make_person(last_name=f"P{s}{w}", photos=photos)


@pytest.mark.django_db
@pytest.mark.parametrize("basename", ENDPOINTS)
def test_list_query_count_does_not_grow_with_rows(
    client, many_rows, basename, django_assert_max_num_queries
):
    # count + page + one per prefetched relation (people have five).
    with django_assert_max_num_queries(7):
        response = client.get(list_url(basename))

    assert response.status_code == 200
    assert len(response.json()["results"]) >= 3
