import responses
from django.test import TestCase, override_settings
from faker import Faker

from ..models import Feature, Wallet
from .factories import ChainFactory, FeatureFactory, GasPriceFactory, WalletFactory

fake = Faker()
Faker.seed(0)


class ChainNetworkHookTestCaseSetupCheck(TestCase):
    @responses.activate
    @override_settings(CGW_URL=None, CGW_AUTH_TOKEN="example-token")
    def test_no_cgw_call_with_no_url(self) -> None:
        ChainFactory.create()

        assert len(responses.calls) == 0

    @responses.activate
    @override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN=None)
    def test_no_cgw_call_with_no_token(self) -> None:
        ChainFactory.create()

        assert len(responses.calls) == 0


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class ChainNetworkHookTestCase(TestCase):
    @responses.activate
    def test_on_chain_create(self) -> None:
        chain_id = fake.pyint()
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "CHAIN_UPDATE", "chainId": str(chain_id)}
                ),
            ],
        )

        ChainFactory.create(id=chain_id)

        assert len(responses.calls) == 1
        assert isinstance(responses.calls[0], responses.Call)
        assert responses.calls[
            0
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[0].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_chain_delete(self) -> None:
        # Deleting an object sets the primary key to None so we set it in a separate variable
        chain_id = fake.pyint()
        chain = ChainFactory.create(id=chain_id)
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "CHAIN_UPDATE", "chainId": str(chain.id)}
                ),
            ],
        )

        chain.delete()

        # 2 calls: one for creation and one for deletion
        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[
            1
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain_id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_chain_update(self) -> None:
        chain = ChainFactory.create()

        # Not updating using queryset because hooks are not triggered that way
        chain.currency_name = "Ether"
        chain.save()

        # 2 calls: one for creation and one for updating
        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[
            1
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[0].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class FeatureHookTestCase(TestCase):
    @responses.activate
    def test_on_feature_create_with_no_chain(self) -> None:
        Feature(key="Test Feature").save()

        # Creating a feature with no chains should not trigger any webhook
        assert len(responses.calls) == 0

    @responses.activate
    def test_on_feature_create_with_chain(self) -> None:
        chain = ChainFactory.create()
        FeatureFactory.create(key="Test Feature", chains=(chain,))

        # 1 call for Chain creation, 1 call for feature creation, 1 call for M2M update
        assert len(responses.calls) == 3
        assert isinstance(responses.calls[2], responses.Call)
        assert responses.calls[
            2
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[2].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[2].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_feature_delete_with_no_chain(self) -> None:
        feature = Feature(key="Test Feature")

        feature.save()  # create
        feature.delete()  # delete

        # Deleting a feature with no chains should not trigger any webhook
        assert len(responses.calls) == 0

    @responses.activate
    def test_on_feature_delete_with_chain(self) -> None:
        chain = ChainFactory.create()
        feature = FeatureFactory.create(key="Test Feature", chains=(chain,))

        feature.delete()

        # 1 call for Chain creation, 1 call for feature creation, 1 call for M2M update, 1 call for feature deletion
        assert len(responses.calls) == 4
        assert isinstance(responses.calls[3], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_feature_update_with_no_chain(self) -> None:
        feature = Feature(key="Test Feature")

        feature.save()  # create
        feature.key = "New Test Feature"
        feature.save()  # update

        # Updating a feature with no chains should not trigger any webhook
        assert len(responses.calls) == 0

    @responses.activate
    def test_on_feature_update_with_chain(self) -> None:
        chain = ChainFactory.create()
        feature = FeatureFactory.create(key="Test Feature", chains=(chain,))

        feature.chains.remove(chain)

        # 1 call for Chain creation, 1 call for feature creation,
        # 1 call for M2M update, 1 call for removing m2m relationship
        assert len(responses.calls) == 4
        assert isinstance(responses.calls[3], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_feature_update_with_multiple_chains(self) -> None:
        chain_1 = ChainFactory.create()
        chain_2 = ChainFactory.create()

        FeatureFactory.create(key="Test Feature", chains=(chain_1, chain_2))

        # 1 call for Chain 1 creation, 1 call for Chain 2 creation, 1 call for feature creation,
        # 1 call for Chain 1 M2M update, 1 call for Chain 2 M2M update, 1 call for Feature update
        assert len(responses.calls) == 6
        assert isinstance(responses.calls[3], responses.Call)
        assert isinstance(responses.calls[4], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain_2.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            4
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain_1.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert responses.calls[4].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert (
            responses.calls[4].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class WalletHookTestCase(TestCase):
    @responses.activate
    def test_on_wallet_create_with_no_chain(self) -> None:
        Wallet(key="Test Wallet").save()

        # Creating a wallet with no chains should not trigger any webhook
        assert len(responses.calls) == 0

    @responses.activate
    def test_on_wallet_create_with_chain(self) -> None:
        chain = ChainFactory.create()
        WalletFactory.create(key="Test Wallet", chains=(chain,))

        # 1 call for Chain creation, 1 call for Wallet creation, 1 call for M2M update
        assert len(responses.calls) == 3
        assert isinstance(responses.calls[2], responses.Call)
        assert responses.calls[
            2
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[2].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[2].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_wallet_delete_with_no_chain(self) -> None:
        wallet = Wallet(key="Test Wallet")

        wallet.save()  # create
        wallet.delete()  # delete

        # deleting a wallet with no chains should not trigger any webhook
        assert len(responses.calls) == 0

    @responses.activate
    def test_on_wallet_delete_with_chain(self) -> None:
        chain = ChainFactory.create()
        wallet = WalletFactory.create(key="Test Wallet", chains=(chain,))

        wallet.delete()

        # 1 call for Chain creation, 1 call for Wallet creation, 1 call for M2M update, 1 call for Wallet deletion
        assert len(responses.calls) == 4
        assert isinstance(responses.calls[3], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_wallet_update_with_no_chain(self) -> None:
        wallet = Wallet(key="Test Wallet")

        wallet.save()  # create
        wallet.key = "Test Wallet v2"
        wallet.save()  # update

        # Updating a wallet with no chains should not trigger any webhook
        assert len(responses.calls) == 0

    @responses.activate
    def test_on_wallet_update_with_chain(self) -> None:
        chain = ChainFactory.create()
        wallet = WalletFactory.create(key="Test Wallet", chains=(chain,))

        wallet.chains.remove(chain)

        # 1 call for Chain creation, 1 call for Wallet creation,
        # 1 call for M2M update, 1 call for removing m2m relationship
        assert len(responses.calls) == 4
        assert isinstance(responses.calls[3], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_wallet_update_with_multiple_chains(self) -> None:
        chain_1 = ChainFactory.create()
        chain_2 = ChainFactory.create()

        WalletFactory.create(key="Test Wallet", chains=(chain_1, chain_2))

        # 1 call for Chain 1 creation, 1 call for Chain 2 creation, 1 call for Wallet creation,
        # 1 call for Chain 1 M2M update, 1 call for Chain 2 M2M update, 1 call for Wallet update
        assert len(responses.calls) == 6
        assert isinstance(responses.calls[3], responses.Call)
        assert isinstance(responses.calls[4], responses.Call)
        assert responses.calls[
            3
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain_2.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[
            4
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{chain_1.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[3].request.url == "http://127.0.0.1/v1/hooks/events"
        assert responses.calls[4].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[3].request.headers.get("Authorization")
            == "Basic example-token"
        )
        assert (
            responses.calls[4].request.headers.get("Authorization")
            == "Basic example-token"
        )


@override_settings(CGW_URL="http://127.0.0.1", CGW_AUTH_TOKEN="example-token")
class GasPriceHookTestCase(TestCase):
    def setUp(self) -> None:
        self.chain = (
            ChainFactory.create()
        )  # chain creation: a GasPrice requires a chain

    @responses.activate
    def test_on_gas_price_create(self) -> None:
        responses.add(
            responses.POST,
            "http://127.0.0.1/v1/hooks/events",
            status=200,
            match=[
                responses.matchers.header_matcher(
                    {"Authorization": "Basic example-token"}
                ),
                responses.matchers.json_params_matcher(
                    {"type": "CHAIN_UPDATE", "chainId": str(self.chain.id)}
                ),
            ],
        )

        GasPriceFactory.create(chain=self.chain)

        assert len(responses.calls) == 1
        assert isinstance(responses.calls[0], responses.Call)
        assert responses.calls[
            0
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{self.chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[0].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[0].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_gas_price_delete(self) -> None:
        gas_price = GasPriceFactory.create(chain=self.chain)  # create
        gas_price.delete()  # delete

        # 2 calls: one for creation and one for deletion
        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[
            1
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{self.chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )

    @responses.activate
    def test_on_gas_price_update(self) -> None:
        gas_price = GasPriceFactory.create(
            chain=self.chain, fixed_wei_value=1000
        )  # create

        gas_price.fixed_wei_value = 2000
        gas_price.save()  # update

        # 2 calls: one for creation and one for updating
        assert len(responses.calls) == 2
        assert isinstance(responses.calls[1], responses.Call)
        assert responses.calls[
            1
        ].request.body == f'{{"type": "CHAIN_UPDATE", "chainId": "{self.chain.id}"}}'.encode(
            "utf-8"
        )
        assert responses.calls[1].request.url == "http://127.0.0.1/v1/hooks/events"
        assert (
            responses.calls[1].request.headers.get("Authorization")
            == "Basic example-token"
        )
