# SPDX-License-Identifier: FSL-1.1-MIT
"""Export current Feature rows for a service as a remote-config declaration.

Run this against a populated database (e.g. production) to seed the initial
checked-in declaration file so the first reconcile diff is clean::

    python src/manage.py export_remote_config --service WALLET_WEB > remote-config.json

The same export is available in the Django admin (Features → "Export declaration").
"""
import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from chains.remote_config.export import ServiceNotFound, build_declaration_document


class Command(BaseCommand):
    help = "Export a service's Feature rows as a remote-config declaration (JSON)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--service",
            required=True,
            help="The Service.key to export (e.g. WALLET_WEB, MOBILE, CGW).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        try:
            document = build_declaration_document(options["service"])
        except ServiceNotFound as error:
            raise CommandError(f"No Service with key '{error}'") from error
        self.stdout.write(json.dumps(document, indent=2))
