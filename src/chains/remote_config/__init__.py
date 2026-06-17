# SPDX-License-Identifier: FSL-1.1-MIT
"""Declarative remote-config flag reconciliation.

This package reads checked-in ``remote-config`` declaration files (one per
service) from a Git ref, diffs them against the ``Feature``/``Service``/``Chain``
database, and lets an operator selectively apply the differences from the Django
admin. See ``docs/remote-config.md`` for the runbook.

The :mod:`declaration` and :mod:`diff` modules are intentionally pure (no Django
imports) so the comparison logic can be unit-tested in isolation.
"""
