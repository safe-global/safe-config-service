# SPDX-License-Identifier: FSL-1.1-MIT
"""Export current Feature rows for a service as a remote-config declaration.

Run this against a populated database (e.g. production) to seed the initial
checked-in declaration file so the first reconcile diff is clean::

    python src/manage.py export_remote_config --service WALLET_WEB > remote-config.json
"""
import json
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from chains.models import Feature, Service


class Command(BaseCommand):
    help = "Export a service's Feature rows as a remote-config declaration (JSON)."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--service",
            required=True,
            help="The Service.key to export (e.g. WALLET_WEB, MOBILE, CGW).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        service_key = options["service"]
        try:
            service = Service.objects.get(key=service_key)
        except Service.DoesNotExist as error:
            raise CommandError(f"No Service with key '{service_key}'") from error

        features = (
            Feature.objects.filter(services=service)
            .prefetch_related("chains")
            .order_by("key")
        )

        entries = []
        for feature in features:
            if feature.scope == Feature.Scope.PER_CHAIN:
                default_chains = sorted(
                    (str(chain.id) for chain in feature.chains.all()), key=int
                )
            else:
                default_chains = []
            entries.append(
                {
                    "key": feature.key,
                    "description": feature.description,
                    "scope": feature.scope,
                    "defaultChains": default_chains,
                }
            )

        document = {
            "$schema": "./remote-config.schema.json",
            "service": service_key,
            "features": entries,
        }
        self.stdout.write(json.dumps(document, indent=2))
