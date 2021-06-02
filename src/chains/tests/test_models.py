from django.test import TestCase

from .factories import ChainFactory


class ChainTestCase(TestCase):
    def test_str_method_outputs_name_chain_id(self):
        chain = ChainFactory.create()
        self.assertEqual(
            str(chain),
            f"{chain.name} | chain_id={chain.id}",
        )
