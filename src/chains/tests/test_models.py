import web3
from django.core.exceptions import ValidationError
from django.db import DataError
from django.test import TestCase, TransactionTestCase
from faker import Faker

from .factories import ChainFactory


class ChainTestCase(TestCase):
    def test_str_method_outputs_name_chain_id(self):
        chain = ChainFactory.create()
        self.assertEqual(
            str(chain),
            f"{chain.name} | chain_id={chain.id}",
        )


class ChainGasPriceOracleTestCase(TestCase):
    faker = Faker()

    def test_oracle_gas_parameter_with_null_url(self):
        chain = ChainFactory.create(
            gas_price_oracle_url=None, gas_price_oracle_parameter="fake parameter"
        )

        with self.assertRaises(ValidationError):
            chain.full_clean()

    def test_null_oracle_gas_parameter_with_url(self):
        chain = ChainFactory.create(
            gas_price_oracle_url=self.faker.url(), gas_price_oracle_parameter=None
        )

        # No validation exception should be thrown
        chain.full_clean()

    def test_oracle_gas_parameter_with_url(self):
        chain = ChainFactory.create(
            gas_price_oracle_url=self.faker.url(),
            gas_price_oracle_parameter="fake parameter",
        )

        # No validation exception should be thrown
        chain.full_clean()

    @staticmethod
    def test_null_oracle_gas_parameter_with_null_url():
        chain = ChainFactory.create(
            gas_price_oracle_url=None, gas_price_oracle_parameter=None
        )

        # No validation exception should be thrown
        chain.full_clean()


class ChainColorValidationTestCase(TransactionTestCase):
    faker = Faker()

    def test_invalid_text_colors(self):
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
                with self.assertRaises(
                    (
                        ValidationError,
                        DataError,
                    )
                ):
                    chain = ChainFactory.create(theme_text_color=invalid_color)
                    # run validators
                    chain.full_clean()

    def test_valid_text_colors(self):
        param_list = ["#000000", "#ffffff"] + [
            self.faker.hex_color() for _ in range(20)
        ]
        for valid_color in param_list:
            with self.subTest(msg=f"Valid color {valid_color} should not throw"):
                chain = ChainFactory.create(theme_text_color=valid_color)
                chain.full_clean()


class ChainEnsRegistryAddressValidationTestCase(TransactionTestCase):
    def test_invalid_addresses(self):
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

    def test_valid_addresses(self):
        param_list = [
            "0x0000000000000000000000000000000000000000",
            "0xFFfFfFffFFfffFFfFFfFFFFFffFFFffffFfFFFfF",
        ] + [web3.Account.create().address for _ in range(20)]

        for valid_address in param_list:
            with self.subTest(msg=f"Valid address {valid_address} should not throw"):
                chain = ChainFactory.create(ens_registry_address=valid_address)
                chain.full_clean()
