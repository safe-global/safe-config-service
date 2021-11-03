from .utils import TestMigrations


class Migration0029TestCase(TestMigrations):
    migrate_from = "0030_wallet"
    migrate_to = "0031_chain_block_explorer_uri_api_template"

    fixtures = ["src/chains/migrations/tests/fixtures/0030_chains.json"]

    def test_block_explorer_uri_api_template_is_set(self) -> None:
        Chain = self.apps_registry.get_model("chains", "Chain")

        mainnet = Chain.objects.get(id=1)
        rinkeby = Chain.objects.get(id=4)
        polygon = Chain.objects.get(id=137)

        self.assertEqual(
            mainnet.block_explorer_uri_api_template,
            "https://api.etherscan.io/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",
        )
        self.assertEqual(
            rinkeby.block_explorer_uri_api_template,
            "https://api-rinkeby.etherscan.io/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",  # noqa E501 # line too long
        )
        self.assertEqual(
            polygon.block_explorer_uri_api_template,
            "https://api.polygonscan.com/api?module={{module}}&action={{action}}&address={{address}}&apiKey={{apiKey}}",  # noqa E501 # line too long
        )
