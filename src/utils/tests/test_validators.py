from django.core.exceptions import ValidationError
from django.db import transaction
from django.test import TestCase

from .models import HostnameExample


class HostnameValidatorTestCase(TestCase):
    def setup(self):
        self.valid_hostname = "domain.net"
        self.invalid_hostname = "domain.net/some_stuff"
        self.objects = HostnameExample.objects

    def test_insert_valid_domain(self):
        obj = HostnameExample(domain=self.valid_domain)
        obj.save()
        self.assertEquals(obj.domain, self.valid_domain)
        self.assertEquals(obj, self.objects.get(domain=self.valid_domain))
        self.assertEquals(self.objects.count(), 1)

    def test_insert_invalid_domain(self):
        with transaction.atomic():
            obj = HostnameExample()
            with self.assertRaises(ValidationError):
                obj.domain = self.invalid_domain
                obj.save()
        self.assertEquals(self.objects.count(), 0)
