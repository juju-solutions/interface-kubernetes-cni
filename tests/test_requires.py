import pytest

from charms.reactive import clear_flag, is_flag_set
from charmhelpers.core import unitdata

import requires


def test_get_config():
    client = requires.CNIPluginClient("cni", [1])
    config = {"kubeconfig-hash": "hash"}
    client.all_joined_units.received_raw = config
    assert client.get_config() == config


def test_set_config():
    client = requires.CNIPluginClient("cni", [1])
    client.set_config("192.168.0.0/24", "10-test.conflist")
    assert client.relations[0].to_publish_raw == {
        "cidr": "192.168.0.0/24",
        "cni-conf-file": "10-test.conflist",
    }


@pytest.fixture()
def reset_flags_and_kv():
    unitdata.kv().clear()
    for flag in [
        "cni.kubeconfig.available",
        "cni.kubeconfig.changed",
        "cni.service_cidr.available",
        "cni.service_cidr.changed",
        "cni.image_registry.available",
        "cni.image_registry.changed",
    ]:
        clear_flag(flag)


@pytest.mark.usefixtures("reset_flags_and_kv")
def test_manage_kubeconfig_flags():
    client = requires.CNIPluginClient("cni", [1])
    client.all_joined_units.received_raw["kubeconfig-hash"] = "hash"
    client.manage_flags()
    assert is_flag_set("cni.kubeconfig.available")
    assert is_flag_set("cni.kubeconfig.changed")
    assert not is_flag_set("cni.service_cidr.available")
    assert not is_flag_set("cni.service_cidr.changed")
    assert not is_flag_set("cni.image_registry.available")
    assert not is_flag_set("cni.image_registry.changed")

    clear_flag("cni.kubeconfig.changed")
    client.manage_flags()
    assert is_flag_set("cni.kubeconfig.available")
    assert not is_flag_set("cni.kubeconfig.changed")


@pytest.mark.usefixtures("reset_flags_and_kv")
def test_manage_service_cidr_flags():
    client = requires.CNIPluginClient("cni", [1])
    client.all_joined_units.received_raw["service-cidr"] = "hash"
    client.manage_flags()
    assert not is_flag_set("cni.kubeconfig.available")
    assert not is_flag_set("cni.kubeconfig.changed")
    assert not is_flag_set("cni.image_registry.available")
    assert not is_flag_set("cni.image_registry.changed")
    assert is_flag_set("cni.service_cidr.available")
    assert is_flag_set("cni.service_cidr.changed")

    clear_flag("cni.service_cidr.changed")
    client.manage_flags()
    assert is_flag_set("cni.service_cidr.available")
    assert not is_flag_set("cni.service_cidr.changed")


@pytest.mark.usefixtures("reset_flags_and_kv")
def test_manage_image_registry_flags():
    client = requires.CNIPluginClient("cni", [1])
    client.all_joined_units.received_raw[
        "image-registry"
    ] = "rocks.canonical.com:443/cdk"
    client.manage_flags()
    assert not is_flag_set("cni.kubeconfig.available")
    assert not is_flag_set("cni.kubeconfig.changed")
    assert not is_flag_set("cni.service_cidr.available")
    assert not is_flag_set("cni.service_cidr.changed")
    assert is_flag_set("cni.image_registry.available")
    assert is_flag_set("cni.image_registry.changed")

    clear_flag("cni.image_registry.changed")
    client.manage_flags()
    assert is_flag_set("cni.image_registry.available")
    assert not is_flag_set("cni.image_registry.changed")
