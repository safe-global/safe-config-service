# SPDX-License-Identifier: FSL-1.1-MIT
"""Project Django ``Feature``/``Chain`` rows into pure diff value objects."""
from ..models import Chain, Feature
from .diff import FeatureState


def load_feature_states() -> dict[str, FeatureState]:
    """Return every DB feature keyed by ``key`` as :class:`FeatureState`.

    Includes features for all services (the diff needs this to tell ADD apart
    from ATTACH) with their chain ids and service keys pre-fetched.
    """
    states: dict[str, FeatureState] = {}
    for feature in Feature.objects.prefetch_related("chains", "services"):
        states[feature.key] = FeatureState(
            feature_id=feature.pk,
            key=feature.key,
            description=feature.description,
            scope=feature.scope,
            chains=frozenset(str(chain.id) for chain in feature.chains.all()),
            services=frozenset(service.key for service in feature.services.all()),
        )
    return states


def known_chain_ids() -> set[str]:
    """Return all chain ids known to the database, as strings."""
    return {str(chain_id) for chain_id in Chain.objects.values_list("id", flat=True)}
