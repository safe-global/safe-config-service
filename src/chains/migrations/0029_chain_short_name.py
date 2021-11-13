# Generated by Django 3.2.7 on 2021-09-30 15:16

from django.apps.registry import Apps
from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


def set_chain_short_name(apps: Apps, schema_editor: BaseDatabaseSchemaEditor) -> None:
    Chain = apps.get_model("chains", "Chain")
    for row in Chain.objects.all():
        row.short_name = SHORT_NAME_MAPPING.get(row.id, "")
        row.save(update_fields=["short_name"])


class Migration(migrations.Migration):
    dependencies = [
        ("chains", "0028_chain_vpc_transaction_service_uri"),
    ]

    operations = [
        # Add the field short_name with null=True in order to create a valid column
        migrations.AddField(
            model_name="chain",
            name="short_name",
            field=models.CharField(
                unique=True,
                null=True,
                max_length=255,
                verbose_name="EIP-3770 short name",
            ),
            preserve_default=False,
        ),
        # Fill the column with the values from SHORT_NAME_MAPPING (empty string if value is not found)
        migrations.RunPython(set_chain_short_name, lambda apps, schema_editor: None),
        # set the short_name column as non-nullable
        migrations.AlterField(
            model_name="chain",
            name="short_name",
            field=models.CharField(
                unique=True,
                null=False,
                max_length=255,
                verbose_name="EIP-3770 short name",
            ),
            preserve_default=False,
        ),
    ]


# List retrieved from https://chainid.network/shortNameMapping.json on September 30, 2021
SHORT_NAME_MAPPING = {
    1: "eth",
    2: "exp",
    3: "rop",
    4: "rin",
    5: "gor",
    6: "kot",
    7: "tch",
    8: "ubq",
    9: "tubq",
    10: "oeth",
    11: "meta",
    12: "kal",
    13: "dstg",
    14: "flr",
    15: "diode",
    16: "cflr",
    17: "tfi",
    18: "TST",
    19: "sgb",
    20: "elaeth",
    21: "elaetht",
    22: "eladid",
    23: "eladidt",
    28: "Boba Rinkeby",
    30: "rsk",
    31: "trsk",
    32: "GooDT",
    33: "GooD",
    35: "tbwg",
    38: "val",
    40: "Telos EVM",
    41: "Telos EVM Testnet",
    42: "kov",
    43: "darwinia",
    44: "crab",
    50: "xdc",
    51: "TXDC",
    52: "cet",
    53: "tcet",
    56: "bnb",
    57: "sys",
    58: "Ontology Mainnet",
    59: "EOS Mainnet",
    60: "go",
    61: "etc",
    62: "tetc",
    63: "metc",
    64: "ella",
    65: "tokt",
    66: "okt",
    67: "dbm",
    68: "SO1",
    69: "okov",
    76: "mix",
    77: "poa",
    78: "primuschain",
    80: "GeneChain",
    82: "Meter",
    85: "gttest",
    86: "gt",
    88: "tomo",
    95: "Kylin Testnet",
    97: "bnbt",
    99: "skl",
    100: "xdai",
    101: "eti",
    102: "w3g",
    108: "TT",
    110: "xpr",
    111: "ETL",
    122: "fuse",
    124: "dwu",
    127: "feth",
    128: "heco",
    137: "matic",
    142: "dax",
    162: "tpht",
    163: "pht",
    170: "hoosmartchain",
    172: "resil",
    200: "aox",
    211: "EDI",
    246: "ewt",
    250: "ftm",
    256: "hecot",
    269: "hpb",
    288: "Boba",
    321: "kcs",
    322: "kcst",
    361: "theta-mainnet",
    363: "theta-sapphire",
    364: "theta-amber",
    365: "theta-testnet",
    369: "pls",
    385: "lisinski",
    420: "ogor",
    499: "rupx",
    558: "tao",
    595: "maca",
    686: "kar",
    721: "tfeth",
    777: "cth",
    787: "aca",
    803: "haic",
    820: "clo",
    821: "tclo",
    888: "wan",
    940: "tpls",
    977: "yeti",
    999: "twan",
    1001: "Baobab",
    1007: "tnew",
    1010: "EVC",
    1012: "new",
    1022: "sku",
    1023: "tclv",
    1024: "clv",
    1139: "MATH",
    1140: "tMATH",
    1284: "mbeam",
    1285: "mriver",
    1286: "mrock",
    1287: "mbase",
    1288: "mshadow",
    1618: "cate",
    1620: "ath",
    1856: "tsf",
    1987: "egem",
    2020: "420",
    2021: "edg",
    2022: "edgt",
    2559: "ktoc",
    4002: "tftm",
    4689: "iotex-mainnet",
    4690: "iotex-testnet",
    5197: "es",
    5700: "tsys",
    5851: "Ontology Testnet",
    5869: "rbd",
    8029: "mdgl",
    8080: "GeneChainAdn",
    8217: "Cypress",
    8285: "Kortho",
    8723: "olo",
    8724: "tolo",
    8995: "berg",
    10000: "smartbch",
    10001: "smartbchtest",
    10101: "GEN",
    16000: "mtt",
    16001: "mtttest",
    24484: "web",
    24734: "mintme",
    31102: "esn",
    31337: "got",
    32659: "fsn",
    39797: "nrg",
    42069: "PC",
    42161: "arb1",
    42220: "CELO",
    43110: "avaeth",
    43113: "Fuji",
    43114: "Avalanche",
    44787: "ALFA",
    49797: "tnrg",
    62320: "BKLV",
    71393: "ckb",
    73799: "vt",
    78110: "firenze",
    80001: "maticmum",
    100000: "qkc-r",
    100001: "qkc-s0",
    100002: "qkc-s1",
    100003: "qkc-s2",
    100004: "qkc-s3",
    100005: "qkc-s4",
    100006: "qkc-s5",
    100007: "qkc-s6",
    100008: "qkc-s7",
    110000: "qkc-d-r",
    110001: "qkc-d-s0",
    110002: "qkc-d-s1",
    110003: "qkc-d-s2",
    110004: "qkc-d-s3",
    110005: "qkc-d-s4",
    110006: "qkc-d-s5",
    110007: "qkc-d-s6",
    110008: "qkc-d-s7",
    200625: "aka",
    246529: "ats",
    246785: "atstau",
    333888: "sparta",
    333999: "olympus",
    421611: "arb-rinkeby",
    1313114: "etho",
    1313500: "xero",
    7762959: "music",
    13371337: "tpep",
    18289463: "ilt",
    20181205: "qki",
    28945486: "auxi",
    35855456: "JOYS",
    61717561: "aqua",
    99415706: "TOYS",
    311752642: "oneledger",
    1122334455: "ipos",
    1313161554: "aurora",
    1313161555: "aurora-testnet",
    1313161556: "aurora-betanet",
    1666600000: "hmy-s0",
    1666600001: "hmy-s1",
    1666600002: "hmy-s2",
    1666600003: "hmy-s3",
    1666700000: "hmy-b-s0",
    1666700001: "hmy-b-s1",
    1666700002: "hmy-b-s2",
    1666700003: "hmy-b-s3",
    3125659152: "pirl",
    4216137055: "frankenstein",
    11297108099: "tpalm",
    11297108109: "palm",
}
