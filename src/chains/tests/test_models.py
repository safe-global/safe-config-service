from decimal import Decimal

import web3
from django.core.exceptions import ValidationError
from django.db import DataError
from django.test import TestCase, TransactionTestCase
from faker import Faker

from .factories import ChainFactory, FeatureFactory, GasPriceFactory, WalletFactory


class ChainTestCase(TestCase):
    def test_str_method_outputs_name_chain_id(self) -> None:
        chain = ChainFactory.create()
        self.assertEqual(
            str(chain),
            f"{chain.name} | chain_id={chain.id}",
        )


class GasPriceTestCase(TestCase):
    def test_str_method_output(self) -> None:
        gas_price = GasPriceFactory.create()

        self.assertEqual(
            str(gas_price),
            f"Chain = {gas_price.chain.id} | uri={gas_price.oracle_uri} | fixed_wei_value={gas_price.fixed_wei_value}",
        )


class ChainGasPriceFixedTestCase(TestCase):
    @staticmethod
    def test_null_oracle_with_non_null_fixed_gas_price() -> None:
        gas_price = GasPriceFactory.create(
            oracle_uri=None,
            fixed_wei_value=10000,
        )

        gas_price.full_clean()

    def test_null_oracle_gas_oracle_with_null_fixed_gas_price(self) -> None:
        gas_price = GasPriceFactory.create(
            oracle_uri=None,
            fixed_wei_value=None,
        )

        with self.assertRaises(ValidationError):
            gas_price.full_clean()

    @staticmethod
    def test_big_number() -> None:
        gas_price = GasPriceFactory.create(
            oracle_uri=None,
            fixed_wei_value="115792089237316195423570985008687907853269984665640564039457584007913129639935",
        )

        gas_price.full_clean()


class ChainGasPriceOracleTestCase(TestCase):
    faker = Faker()

    def test_oracle_gas_parameter_with_null_uri(self) -> None:
        gas_price = GasPriceFactory.create(
            oracle_uri=None,
            oracle_parameter="fake parameter",
            fixed_wei_value=None,
        )

        with self.assertRaises(ValidationError):
            gas_price.full_clean()

    def test_null_oracle_gas_parameter_with_uri(self) -> None:
        gas_price = GasPriceFactory.create(
            oracle_uri=self.faker.url(),
            oracle_parameter=None,
            fixed_wei_value=None,
        )

        with self.assertRaises(ValidationError):
            gas_price.full_clean()

    def test_oracle_gas_parameter_with_uri(self) -> None:
        gas_price = GasPriceFactory.create(
            oracle_uri=self.faker.url(),
            oracle_parameter="fake parameter",
            fixed_wei_value=None,
        )

        # No validation exception should be thrown
        gas_price.full_clean()


class ChainColorValidationTestCase(TransactionTestCase):
    faker = Faker()

    def test_invalid_text_colors(self) -> None:
        param_list = [
            "aaa",
            "bbb",
            "#fffffffff",
            "zzz",
            "010",
            "",
            "a word",
            "#hhh",
            "#fff",
            "#ffffffff",
        ]
        for invalid_color in param_list:
            with self.subTest(msg=f"Invalid color {invalid_color} should throw"):
                with self.assertRaises(tuple([ValidationError, DataError])):
                    chain = ChainFactory.create(theme_text_color=invalid_color)
                    # run validators
                    chain.full_clean()

    def test_valid_text_colors(self) -> None:
        param_list = ["#000000", "#ffffff"] + [
            self.faker.hex_color() for _ in range(20)
        ]
        for valid_color in param_list:
            with self.subTest(msg=f"Valid color {valid_color} should not throw"):
                chain = ChainFactory.create(theme_text_color=valid_color)
                chain.full_clean()


class ChainEnsRegistryAddressValidationTestCase(TransactionTestCase):
    def test_invalid_addresses(self) -> None:
        param_list = [
            "0x",
            "0x0",
            "0xgz",
            "0x0",
            "0x000000000000000000000000000000000000000",
            "0x00000000000000000000000000000000000000000",
        ]

        for invalid_address in param_list:
            with self.subTest(msg=f"Invalid address {invalid_address} should throw"):
                with self.assertRaises(
                    (
                        # normalize_address from gnosis-py throws a generic Exception if the address is not valid
                        Exception,
                    )
                ):
                    chain = ChainFactory.create(ens_registry_address=invalid_address)
                    # run validators
                    chain.full_clean()

    def test_valid_addresses(self) -> None:
        param_list = [
            "0x0000000000000000000000000000000000000000",
            "0xFFfFfFffFFfffFFfFFfFFFFFffFFFffffFfFFFfF",
        ] + [web3.Account.create().address for _ in range(20)]

        for valid_address in param_list:
            with self.subTest(msg=f"Valid address {valid_address} should not throw"):
                chain = ChainFactory.create(ens_registry_address=valid_address)
                chain.full_clean()


class ChainGweiFactorTestCase(TestCase):
    @staticmethod
    def test_ether_to_gwei_conversion_rate_valid() -> None:
        eth_gwei = Decimal("0.000000001")  # 0.000000001 ETH == 1 GWei
        gas_price = GasPriceFactory.create(gwei_factor=eth_gwei)

        gas_price.full_clean()

    @staticmethod
    def test_wei_to_gwei_conversion_rate_valid() -> None:
        eth_gwei = Decimal("1000000000")  # 1000000000 Wei == 1 GWei
        gas_price = GasPriceFactory.create(gwei_factor=eth_gwei)

        gas_price.full_clean()

    def test_1e_minus10_conversion_rate_invalid(self) -> None:
        factor = Decimal("0.00000000001")
        gas_price = GasPriceFactory.create(gwei_factor=factor)

        with self.assertRaises(ValidationError):
            gas_price.full_clean()

    def test_1e10_conversion_rate_invalid(self) -> None:
        factor = Decimal("10000000000")

        with self.assertRaises(DataError):
            gas_price = GasPriceFactory.create(gwei_factor=factor)
            gas_price.full_clean()


class ChainMinMasterCopyVersionValidationTestCase(TransactionTestCase):
    def test_invalid_versions(self) -> None:
        param_list = [
            "1",
            "1.2",
            "1.2.3-0123",
            "1.1.01",
            "1.01.1",
            "01.1.1",
        ]

        for invalid_version in param_list:
            with self.subTest(msg=f"Invalid version {invalid_version} should throw"):
                with self.assertRaises(ValidationError):
                    chain = ChainFactory.create(
                        recommended_master_copy_version=invalid_version
                    )
                    # run validators
                    chain.full_clean()

    def test_valid_versions(self) -> None:
        param_list = [
            "0.0.4",
            "10.20.30",
            "1.2.3",
            "1.1.2-prerelease+meta",
            "1.0.0-alpha.1",
            "99999999999999999999999.999999999999999999.99999999999999999",
        ]

        for valid_version in param_list:
            with self.subTest(msg=f"Valid version {valid_version} should not throw"):
                chain = ChainFactory.create(
                    recommended_master_copy_version=valid_version
                )
                # run validators
                chain.full_clean()


class ChainCurrencyLogoTestCase(TestCase):
    def test_currency_logo_upload_path(self) -> None:
        chain = ChainFactory.create(id=12)

        self.assertEqual(
            chain.currency_logo_uri.url, "/media/chains/12/currency_logo.jpg"
        )


class WalletTestCase(TestCase):
    def test_str_method_outputs_name(self) -> None:
        wallet = WalletFactory.create()

        self.assertEqual(str(wallet), f"Wallet: {wallet.key}")


class FeatureTestCase(TestCase):
    def test_str_method_outputs_name(self) -> None:
        feature = FeatureFactory.create()

        self.assertEqual(str(feature), f"Chain Feature: {feature.key}")
