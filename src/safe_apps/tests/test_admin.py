from django.contrib.admin import site
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from ..admin import SafeAppAdmin
from ..models import SafeApp
from ..tests.factories import SafeAppFactory


class ChainIdFilterTest(TestCase):
    request_factory = RequestFactory()

    alfred: User

    @classmethod
    def setUpTestData(cls) -> None:
        # Create superuser (alfred)
        cls.alfred = User.objects.create_superuser(
            "alfred", "alfred@example.com", "password"
        )

    def test_look_up(self) -> None:
        # Add safe apps and configure request
        SafeAppFactory.create(chain_ids=[3])
        SafeAppFactory.create(chain_ids=[1])
        SafeAppFactory.create(chain_ids=[100])
        safe_app_admin = SafeAppAdmin(SafeApp, site)
        request = self.request_factory.get("/")
        request.user = self.alfred

        changelist = safe_app_admin.get_changelist_instance(request)

        filterspec = changelist.get_filters(request)[0][0]
        # The lookup should return a tuple of (chain_id, chain_id)
        expected = [(1, 1), (3, 3), (100, 100)]
        self.assertEqual(filterspec.lookup_choices, expected)  # type: ignore[attr-defined]

    def test_unfiltered_lookup(self) -> None:
        safe_app_1 = SafeAppFactory.create(chain_ids=[3])
        safe_app_2 = SafeAppFactory.create(chain_ids=[1])
        safe_app_3 = SafeAppFactory.create(chain_ids=[100])
        safe_app_admin = SafeAppAdmin(SafeApp, site)
        request = self.request_factory.get("/")
        request.user = self.alfred

        changelist = safe_app_admin.get_changelist_instance(request)

        # The queryset should contain all apps (no filter)
        queryset = changelist.get_queryset(request)
        self.assertEqual(set(queryset), {safe_app_2, safe_app_1, safe_app_3})

    def test_filtered_lookup(self) -> None:
        safe_app_2 = SafeAppFactory.create(chain_ids=[1])
        SafeAppFactory.create(chain_ids=[3])
        SafeAppFactory.create(chain_ids=[100])
        safe_app_admin = SafeAppAdmin(SafeApp, site)
        request = self.request_factory.get("/", {"chain_ids": "1"})
        request.user = self.alfred

        changelist = safe_app_admin.get_changelist_instance(request)

        # The queryset should contain apps with chainId 1
        queryset = changelist.get_queryset(request)
        self.assertEqual(set(queryset), {safe_app_2})
