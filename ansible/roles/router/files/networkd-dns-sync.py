#!/usr/bin/python3

import argparse
import ipaddress
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
INTERFACE_NAME = re.compile(r"^[A-Za-z0-9_.:-]+$")
HOSTS_FILE = Path("/var/lib/networkd-dns/dhcp.hosts")
RELOAD_MARKER = Path("/var/lib/networkd-dns/reload-pending")


def validate_domain(value):
    domain = value.lower().rstrip(".")
    if not domain or any(
        not HOST_LABEL.fullmatch(label) for label in domain.split(".")
    ):
        raise ValueError(f"Invalid DNS domain: {value!r}")
    return domain


def read_dhcp_leases(interface):
    import dbus

    bus = dbus.SystemBus()
    manager_object = bus.get_object(
        "org.freedesktop.network1",
        "/org/freedesktop/network1",
    )
    manager = dbus.Interface(
        manager_object,
        dbus_interface="org.freedesktop.network1.Manager",
    )
    ifindex, _ = manager.GetLinkByName(interface)
    description = json.loads(str(manager.DescribeLink(int(ifindex))))

    dhcp_server = description.get("DHCPServer")
    if not isinstance(dhcp_server, dict) or not isinstance(
        dhcp_server.get("Leases"), list
    ):
        raise TypeError(
            f"systemd-networkd did not report DHCP server leases for {interface}"
        )
    return dhcp_server["Leases"]


def normalize_hostname(value, domain):
    if not isinstance(value, str):
        return None

    hostname = value.strip().rstrip(".").lower()
    hostname = hostname.removesuffix(f".{domain}")

    if "." in hostname or not HOST_LABEL.fullmatch(hostname):
        return None
    return hostname


def parse_lease_address(value):
    if isinstance(value, str):
        return ipaddress.ip_address(value)
    if (
        isinstance(value, list)
        and len(value) == 4
        and all(type(octet) is int and 0 <= octet <= 255 for octet in value)
    ):
        return ipaddress.IPv4Address(bytes(value))
    raise ValueError("DHCP server lease has a missing or invalid IPv4 address")


def render_hosts(leases, subnet, domain, server_address):
    if not isinstance(leases, list):
        raise TypeError("DHCP server leases must be a list")

    domain = validate_domain(domain)
    network = ipaddress.ip_network(subnet, strict=True)
    server_ip = ipaddress.ip_address(server_address)
    if network.version != 4 or server_ip not in network:
        raise ValueError(
            "The DHCP subnet and server address must be matching IPv4 values"
        )

    addresses_by_name = {}
    names_by_address = {}
    for lease in leases:
        if not isinstance(lease, dict):
            raise TypeError("Malformed DHCP server lease entry")

        raw_address = lease.get("Address")
        address = parse_lease_address(raw_address)
        if address.version != 4:
            raise ValueError(
                f"DHCP server lease has a non-IPv4 address: {raw_address!r}"
            )
        if address not in network or address == server_ip:
            print(
                f"Ignoring out-of-subnet DHCP lease address {address}", file=sys.stderr
            )
            continue

        hostname = normalize_hostname(lease.get("Hostname"), domain)
        if hostname is None:
            print(
                f"Ignoring lease for {address} without a valid hostname",
                file=sys.stderr,
            )
            continue

        addresses_by_name.setdefault(hostname, set()).add(address)
        names_by_address.setdefault(address, set()).add(hostname)

    lines = []
    for hostname in sorted(addresses_by_name):
        addresses = addresses_by_name[hostname]
        if len(addresses) != 1:
            print(f"Ignoring ambiguous DHCP hostname {hostname!r}", file=sys.stderr)
            continue

        address = next(iter(addresses))
        if len(names_by_address[address]) != 1:
            print(f"Ignoring ambiguous DHCP lease address {address}", file=sys.stderr)
            continue

        lines.append(f"{address} {hostname}.{domain} {hostname}")

    return "".join(f"{line}\n" for line in lines)


def atomic_write(path, content):
    path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    try:
        if path.read_text(encoding="ascii") == content:
            return False
    except FileNotFoundError:
        pass

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="ascii",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            os.fchmod(temporary_file.fileno(), 0o644)

        os.replace(temporary_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return True


def synchronize(interface, subnet, server_address, domain):
    leases = read_dhcp_leases(interface)
    content = render_hosts(leases, subnet, domain, server_address)
    try:
        previous_content = HOSTS_FILE.read_text(encoding="ascii")
    except FileNotFoundError:
        previous_content = None

    if previous_content != content:
        RELOAD_MARKER.touch(mode=0o600, exist_ok=True)
        atomic_write(HOSTS_FILE, content)
    if RELOAD_MARKER.exists():
        subprocess.run(
            ["systemctl", "reload", "dnsmasq.service"],
            check=True,
            timeout=15,
        )
        RELOAD_MARKER.unlink()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", required=True)
    parser.add_argument("--subnet", required=True)
    parser.add_argument("--server-address", required=True)
    parser.add_argument("--domain", required=True)
    args = parser.parse_args()

    if not INTERFACE_NAME.fullmatch(args.interface):
        parser.error("invalid interface name")
    try:
        synchronize(
            args.interface,
            args.subnet,
            args.server_address,
            validate_domain(args.domain),
        )
    except (OSError, RuntimeError, TypeError, ValueError, subprocess.SubprocessError) as error:
        print(f"networkd-dns-sync: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
