#!/usr/bin/python

from charmhelpers.core import unitdata
from charms.reactive import Endpoint
from charms.reactive import when_any, when_not
from charms.reactive import set_state, remove_state

db = unitdata.kv()


class CNIPluginClient(Endpoint):
    def manage_flags(self):
        config = self.get_config()

        # Announce changes to kubeconfig-hash
        kubeconfig_hash = config.get("kubeconfig-hash")
        kubeconfig_hash_key = self.expand_name("{endpoint_name}.kubeconfig-hash")
        if kubeconfig_hash:
            set_state(self.expand_name("{endpoint_name}.kubeconfig.available"))
        if kubeconfig_hash != db.get(kubeconfig_hash_key):
            set_state(self.expand_name("{endpoint_name}.kubeconfig.changed"))
            db.set(kubeconfig_hash_key, kubeconfig_hash)

        # Announce changes to service-cidr
        service_cidr = config.get("service-cidr")
        service_cidr_key = self.expand_name("{endpoint_name}.service-cidr")
        if service_cidr:
            set_state(self.expand_name("{endpoint_name}.service_cidr.available"))
        if service_cidr != db.get(service_cidr_key):
            set_state(self.expand_name("{endpoint_name}.service_cidr.changed"))
            db.set(service_cidr_key, service_cidr)

    @when_any("endpoint.{endpoint_name}.joined", "endpoint.{endpoint_name}.changed")
    def changed(self):
        """Indicate the relation is connected, and if the relation data is
        set it is also available."""
        set_state(self.expand_name("{endpoint_name}.connected"))
        remove_state(self.expand_name("endpoint.{endpoint_name}.changed"))

    @when_not("endpoint.{endpoint_name}.joined")
    def broken(self):
        """Indicate the relation is no longer available and not connected."""
        remove_state(self.expand_name("{endpoint_name}.connected"))

    def get_config(self):
        """Get the kubernetes configuration information."""
        return self.all_joined_units.received_raw

    def set_config(self, cidr, cni_conf_file):
        """Sets the CNI configuration information."""
        for relation in self.relations:
            relation.to_publish_raw.update(
                {"cidr": cidr, "cni-conf-file": cni_conf_file}
            )
