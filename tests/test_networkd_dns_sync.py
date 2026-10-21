import importlib.util
import ipaddress
from pathlib import Path
import tempfile
import unittest


SCRIPT = (
    Path(__file__).parents[1]
    / "ansible"
    / "roles"
    / "router"
    / "files"
    / "networkd-dns-sync.py"
)
SPEC = importlib.util.spec_from_file_location("networkd_dns_sync", SCRIPT)
networkd_dns_sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(networkd_dns_sync)


class RenderHostsTests(unittest.TestCase):
    def test_renders_valid_fqdn_and_short_alias(self):
        result = networkd_dns_sync.render_hosts(
            [{"Address": "192.168.100.101", "Hostname": "Venus"}],
            ipaddress.ip_network("192.168.100.0/24"),
            "home.arpa",
            "192.168.100.1",
        )
        self.assertEqual(result, "192.168.100.101 venus.home.arpa venus\n")

    def test_accepts_hostname_already_qualified_with_configured_domain(self):
        result = networkd_dns_sync.render_hosts(
            [{"Address": "192.168.100.101", "Hostname": "Venus.home.arpa"}],
            ipaddress.ip_network("192.168.100.0/24"),
            "home.arpa",
            "192.168.100.1",
        )
        self.assertEqual(result, "192.168.100.101 venus.home.arpa venus\n")

    def test_renders_systemd_json_byte_array_address(self):
        result = networkd_dns_sync.render_hosts(
            [{"Address": [192, 168, 100, 101], "Hostname": "venus"}],
            ipaddress.ip_network("192.168.100.0/24"),
            "home.arpa",
            "192.168.100.1",
        )
        self.assertEqual(result, "192.168.100.101 venus.home.arpa venus\n")

    def test_omits_missing_or_invalid_names(self):
        result = networkd_dns_sync.render_hosts(
            [
                {"Address": "192.168.100.101"},
                {"Address": "192.168.100.102", "Hostname": "bad name"},
            ],
            ipaddress.ip_network("192.168.100.0/24"),
            "home.arpa",
            "192.168.100.1",
        )
        self.assertEqual(result, "")

    def test_omits_ambiguous_names(self):
        result = networkd_dns_sync.render_hosts(
            [
                {"Address": "192.168.100.101", "Hostname": "venus"},
                {"Address": "192.168.100.102", "Hostname": "venus"},
            ],
            ipaddress.ip_network("192.168.100.0/24"),
            "home.arpa",
            "192.168.100.1",
        )
        self.assertEqual(result, "")

    def test_rejects_malformed_lease_data(self):
        with self.assertRaises(ValueError):
            networkd_dns_sync.render_hosts(
                [{"Hostname": "venus"}],
                ipaddress.ip_network("192.168.100.0/24"),
                "home.arpa",
                "192.168.100.1",
            )

    def test_atomic_write_updates_and_removes_stale_records(self):
        with tempfile.TemporaryDirectory() as directory:
            hosts_file = Path(directory) / "dhcp.hosts"
            self.assertTrue(
                networkd_dns_sync.atomic_write(
                    hosts_file,
                    "192.168.100.101 venus.home.arpa\n",
                )
            )
            self.assertTrue(networkd_dns_sync.atomic_write(hosts_file, ""))
            self.assertEqual(hosts_file.read_text(encoding="ascii"), "")
            self.assertFalse(networkd_dns_sync.atomic_write(hosts_file, ""))


if __name__ == "__main__":
    unittest.main()
