import re
from urllib.parse import urlsplit, urlunsplit

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.encoding import punycode
from django.utils.ipv6 import is_valid_ipv6_address
from django.utils.regex_helper import _lazy_re_compile
from django.utils.translation import gettext_lazy as _


def validate_ipv6_address(value):
    if not is_valid_ipv6_address(value):
        raise ValidationError(
            _("Enter a valid IPv6 address."), code="invalid", params={"value": value}
        )


@deconstructible
class HostnameValidator(RegexValidator):
    """
    This is Django's URLValidator with removed resource path check
    to serve as a validator for hostnames.
    https://github.com/django/django/blob/e8b4feddc34ffe5759ec21da8fa027e86e653f1c/django/core/validators.py#L63
    """

    ul = "\u00a1-\uffff"  # Unicode letters range (must not be a raw string).

    # IP patterns
    ipv4_re = r"(?:0|25[0-5]|2[0-4]\d|1\d?\d?|[1-9]\d?)(?:\.(?:0|25[0-5]|2[0-4]\d|1\d?\d?|[1-9]\d?)){3}"
    ipv6_re = r"\[[0-9a-f:.]+\]"  # (simple regex, validated later)

    # Host patterns
    hostname_re = (
        r"[a-z" + ul + r"0-9](?:[a-z" + ul + r"0-9-]{0,61}[a-z" + ul + r"0-9])?"
    )
    # Max length for domain name labels is 63 characters per RFC 1034 sec. 3.1
    domain_re = r"(?:\.(?!-)[a-z" + ul + r"0-9-]{1,63}(?<!-))*"
    tld_re = (
        r"\."  # dot
        r"(?!-)"  # can't start with a dash
        r"(?:[a-z" + ul + "-]{2,63}"  # domain label
        r"|xn--[a-z0-9]{1,59})"  # or punycode label
        r"(?<!-)"  # can't end with a dash
        r"\.?"  # may have a trailing dot
    )
    host_re = "(" + hostname_re + domain_re + tld_re + "|localhost)"

    regex = _lazy_re_compile(
        r"^(?:[a-z0-9.+-]*)://"  # scheme is validated separately
        r"(?:[^\s:@/]+(?::[^\s:@/]*)?@)?"  # user:pass authentication
        r"(?:" + ipv4_re + "|" + ipv6_re + "|" + host_re + ")"
        r"(?::\d{1,5})?"  # port
        r"\Z",
        re.IGNORECASE,
    )
    message = _("Enter a valid URL.")
    schemes = ["http", "https", "ftp", "ftps"]
    unsafe_chars = frozenset("\t\r\n")

    def __init__(self, schemes=None, **kwargs):
        super().__init__(**kwargs)
        if schemes is not None:
            self.schemes = schemes

    def __call__(self, value):
        if not isinstance(value, str):
            raise ValidationError(self.message, code=self.code, params={"value": value})
        if self.unsafe_chars.intersection(value):
            raise ValidationError(self.message, code=self.code, params={"value": value})
        # Check if the scheme is valid.
        scheme = value.split("://")[0].lower()
        if scheme not in self.schemes:
            raise ValidationError(self.message, code=self.code, params={"value": value})

        # Then check full URL
        try:
            splitted_url = urlsplit(value)
        except ValueError:
            raise ValidationError(self.message, code=self.code, params={"value": value})
        try:
            super().__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain
            if value:
                scheme, netloc, path, query, fragment = splitted_url
                try:
                    netloc = punycode(netloc)  # IDN -> ACE
                except UnicodeError:  # invalid domain part
                    raise e
                url = urlunsplit((scheme, netloc, path, query, fragment))
                super().__call__(url)
            else:
                raise
        else:
            # Now verify IPv6 in the netloc part
            host_match = re.search(r"^\[(.+)\](?::\d{1,5})?$", splitted_url.netloc)
            if host_match:
                potential_ip = host_match[1]
                try:
                    validate_ipv6_address(potential_ip)
                except ValidationError:
                    raise ValidationError(
                        self.message, code=self.code, params={"value": value}
                    )

        # The maximum length of a full host name is 253 characters per RFC 1034
        # section 3.1. It's defined to be 255 bytes or less, but this includes
        # one byte for the length of the name and one byte for the trailing dot
        # that's used to indicate absolute names in DNS.
        if splitted_url.hostname is None or len(splitted_url.hostname) > 253:
            raise ValidationError(self.message, code=self.code, params={"value": value})
