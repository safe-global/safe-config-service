from django.test import override_settings
from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

faker = Faker()


def generate_semver(
    min_major=0, max_major=10, min_minor=0, max_minor=10, min_patch=0, max_patch=10
):
    major = faker.random_int(min=min_major, max=max_major)
    minor = faker.random_int(min=min_minor, max=max_minor)
    patch = faker.random_int(min=min_patch, max=max_patch)
    return f"{major}.{minor}.{patch}"


semver = generate_semver()


@override_settings(APPLICATION_VERSION=semver)
class AboutJsonPayloadFormatViewTests(APITestCase):
    def test_json_payload_format(self):
        url = reverse("v1:about:detail")
        expected_json_response = {
            "name": "Safe Config Service",
            "version": semver,
            "apiVersion": "v1",
            "secure": False,
        }

        response = self.client.get(path=url, data=None, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_json_response)


@override_settings(APPLICATION_VERSION=semver)
class AboutSecureRequestViewTests(APITestCase):
    def test_https_request(self):
        url = reverse("v1:about:detail")
        expected_json_response = {
            "name": "Safe Config Service",
            "version": semver,
            "api_version": "v1",
            "secure": True,
        }

        response = self.client.get(path=url, data=None, format="json", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_json_response)

    def test_http_request(self):
        url = reverse("v1:about:detail")
        expected_json_response = {
            "name": "Safe Config Service",
            "version": semver,
            "api_version": "v1",
            "secure": False,
        }

        response = self.client.get(path=url, data=None, format="json", secure=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_json_response)


class SwaggerTests(APITestCase):
    def test_swagger_json_schema(self):
        url = reverse("schema-json", args=(".json",))

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_swagger_ui(self):
        url = reverse("schema-swagger-ui")

        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
