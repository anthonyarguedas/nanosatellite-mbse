"""Reviewed historical revision aliases for the source migration.

Each alias pairs exact original source/metadata with exact migrated model source.
These identities are fixed configuration and are never learned at runtime.
"""

LEGACY_REVISIONS = {
    "eps_battery_step": {
        "legacy_revision": "60c694ca6591c7eb1e7f8f695751a69d138ecbe52567a84127926f626c4f7124",
        "native_revision": "1a58ec335a074aabefdf2ad774c7563a32e924f4e095db5bbcecd09d73c1434a",
    },
    "eps_converter_step": {
        "legacy_revision": "131d924d4e0682d7f946a6e34c591e06258a7ec4088ff75661805485aa286151",
        "native_revision": "52abbaafd392156ad03d12297793f7a149eef03bcb5d0f337375e51769f00318",
    },
    "eps_energy_segment": {
        "legacy_revision": "531e283efe9bfa77d2e3f75946be2fa46ca4e0479b4d5d7572af374d225040ed",
        "native_revision": "8f6da905febbc0d6cf270ac1eba3fbb6b2742d369bb531d6a7b94f89dd00b5e5",
    },
    "eps_fit": {
        "legacy_revision": "c22f4b5e6f672caeabfb0f46c67953ff3a03d1ef08e6504efa045db64379e396",
        "native_revision": "f10d241c3ae17def93e3a3f872a2000bfc38813eb63eb77cfdab28b6805b398d",
    },
    "eps_geometry": {
        "legacy_revision": "a3ee93a19e3f4a16f99f23ade4be692ae0eae1c3c9a6f3a7755df7fb0ed01713",
        "native_revision": "1956e6b0eaa62d8de2492e96df121bb0c286b6b88e0c9541efed6ea164d9cc9a",
    },
    "eps_guidance": {
        "legacy_revision": "63e3a6a57b26ff45b42899f5264f7ed265e2fe191dab8cfd8a4342a806fcbbc4",
        "native_revision": "2370c10fc5fdfc642801a846bc8bd91e4c6402d78c5f9b8dd59ce1d1910e6e88",
    },
    "eps_power_path": {
        "legacy_revision": "47f02a8ce9ab63e9e2461777f856bdcd678214def20f3cb1cb3d19dfc542a1e3",
        "native_revision": "25f4d056e832020d43013cf9c5f9ac3c57b56cb5710d5539e0da7c674de4868c",
    },
    "eps_protection": {
        "legacy_revision": "06e943f514c2bac43756e3a6656c6162deef148640fdd8d5b348868fd3a5e3e3",
        "native_revision": "55742fd3beabcba7d3d14ec2ace5ceb1e9da99737a6ea59b694adf46dfe1bcc6",
    },
    "eps_ram": {
        "legacy_revision": "63ef1421d0a1285150099e162950a30022d1faeb1b8505dac06ceb99ee9f53ef",
        "native_revision": "51d8e40accd00d5a36189007de67ef21fb86b78c6e77bb00536ebd5284cd21a6",
    },
    "eps_sizing": {
        "legacy_revision": "fe5e8b365156893adf3f2389100bdf106b636600af5cf8aa5eb7f1a86f81e9cf",
        "native_revision": "9a857241815bf36bf4f1d12f44f19df543f7b02c46843065b03cb89cee128ce7",
    },
    "eps_thermal": {
        "legacy_revision": "c9237b5d5cc92f8a01bf623b92decf5954464622035abd7f4cf32dfc89bec414",
        "native_revision": "ecd60be1e716d0e4bde815011d85b0f341cc43a91603bf44ef17a9f5f1faac23",
    },
    "mppt_po": {
        "legacy_revision": "011103331f21e13ce3ef5b4b5512168ac36a43fbea3dd6c68f2990812203911a",
        "native_revision": "b7fba04df2f415f330db10d1285c09dcb2246670a5a8f6080e3569f4e6ad019c",
    },
    "normal_interval": {
        "legacy_revision": "132bbbda3c2b73a941ed1c6d46b6f52ce2d2d72df02b221f5683e352c4533151",
        "native_revision": "9da213067e412ac9885d059a49da85b014d9ed912042805df39eaf3d41259d06",
    },
    "scenario_illumination": {
        "legacy_revision": "389d79b166e6b2cb7b4f781e5443474e7597f484bf7ea98dc20ea28aea5630ee",
        "native_revision": "286c91bb3cc2fc74db771e24f8a0f2b416da7e11e6f0d88be8d733b149884df2",
    },
}
