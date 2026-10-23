# Linux Setup Scripts

An Ansible-based workstation configuration for Debian and Ubuntu systems. It
installs a consistent developer environment locally or on a remote machine over
SSH.

## Included Configuration

| Tag | Role | Configuration |
| --- | --- | --- |
| `common` | `common` | Base development packages and Node.js 24 LTS |
| `systemd` | `systemd` | `systemd-resolved`, mDNS, NSS, and NetworkManager DNS integration |
| `ssh` | `ssh_hardening` | OpenSSH server installation and ssh-audit-based cryptographic hardening |
| `podman` | `podman` | Rootless Podman and Podman Compose configuration |
| `nftables` | `nftables` | Default input firewall with SSH, ICMP, and mDNS access |
| `router` | `router` | Optional IPv4 router with DHCP, forwarding, and NAT |
| `shell` | `shell_config` | Fish, Starship, direnv, fzf, pyenv, fonts, and Konsole profile |
| `scripts` | `system_scripts` | Helper scripts in `/usr/local/bin` |
| `vscode` | `vscode` | VS Code repository, application, settings, and extensions |
| `git` | `git_config` | Global Git configuration |
| `yakuake` | `yakuake` | Yakuake configuration and user systemd service |

The `ssh` role defaults to public-key-only authentication, disables root login
and forwarding, and applies connection limits. These SSHD policies can be
overridden with `ssh_hardening_*` variables. Ensure key-based access works
before deploying the role remotely; it does not configure a firewall or
Fail2Ban.

## Testing DNS and mDNS

After deployment, verify that `systemd-resolved` is active and Avahi is not
running:

```bash
systemctl is-active systemd-resolved.service
systemctl is-active avahi-daemon.service
```

The first command must return `active`. The second must return `inactive` or
report that the unit does not exist.

Check the active network link, replacing `wlp2s0` with the appropriate
interface name:

```bash
resolvectl status wlp2s0
```

The output should list the DHCP-provided DNS server (for example,
`192.168.1.1`), the `fritz.box` search domain, and `+mDNS` under `Protocols`.

From another device on the same Layer-2 network segment, resolve the
workstation hostname:

```bash
resolvectl query workstation.local
```

Replace `workstation` with the target's hostname. The command should return
the target's IPv4 and/or IPv6 address. To confirm that the input filter loaded
the mDNS rules, run on the target:

```bash
sudo nft list chain inet filter input
```

The output must include UDP port `5353` rules for `224.0.0.251` (IPv4) and
`ff02::fb` (IPv6).

To inspect the mDNS traffic directly, run the following command on the target
while resolving its `.local` hostname from another device:

```bash
sudo tcpdump -ni wlp2s0 'udp port 5353'
```

Replace `wlp2s0` with the active network interface. The capture should show
UDP packets to `224.0.0.251.5353` (IPv4) and/or `ff02::fb.5353` (IPv6).
mDNS is link-local and does not cross routers; use unicast DNS for names in a
different IP subnet.

## Router Configuration

The `router` role is disabled by default to avoid changing a normal workstation
into a gateway. Enable it for the intended host in inventory variables and
configure the LAN interface that serves DHCP, the WAN interface used for NAT,
and the addresses announced to DHCP clients:

```yaml
router_enabled: true
router_lan_interface: usbnet
router_lan_mac_address: "3c:18:a0:0f:72:63"
router_wan_interface: wlp1s0
router_lan_address: 192.168.100.1/24
router_lan_subnet: 192.168.100.0/24
router_dhcp_gateway: 192.168.100.1
router_dhcp_dns_servers:
  - 192.168.100.1
```

The `nftables` role is enabled by default. It configures a default-drop input
filter with access for established connections, loopback, ICMP/ICMPv6, SSH, and
mDNS. It writes `/etc/nftables.conf` with `flush ruleset` and includes
`/etc/nftables.d/*.nft`, creates `/etc/nftables.d/10-filter.nft`, and manages
the `nftables` service. To prevent conflicting input hooks, it disables
`firewalld` when that service is installed.

The optional `router` role assigns the USB LAN adapter a stable interface name
using its MAC address in `/etc/systemd/network/10-router-lan.link`, configures
IPv4 forwarding, writes `/etc/systemd/network/10-router-lan.network`, and manages
`systemd-networkd`. It creates `/etc/nftables.d/20-router.nft`, which permits
LAN access to the router and adds forwarding plus source NAT. The DHCP pool and
lease durations are configurable through the `router_dhcp_*` variables in the
role defaults. A new `.link` file takes effect when the adapter is next
initialized; reboot the host or reconnect the adapter after deployment.

## Requirements

- Debian or Ubuntu system
- `sudo` access on the target host
- Python 3 on the control machine and remote target
- For remote deployments: SSH access with a configured key or SSH agent

## First-Time Setup

Install the Python tools, Ansible, linting tools, and required collections:

```bash
./scripts/install-requirements
./scripts/install-ansible
```

The installation scripts put Ansible in the user-local `pipx` environment. Open
a new shell after installation if its executable directory was not already on
your `PATH`.

## Deploy Locally

Apply all roles to the local workstation:

```bash
./scripts/deploy
```

The command prompts for the local `sudo` password when privileged tasks need
it. `localhost`, `127.0.0.1`, and `::1` passed with `--host` also use the local
Ansible connection.

## Deploy Remotely

Pass an SSH host name, address, or alias to deploy to a remote workstation:

```bash
./scripts/deploy --host mars
./scripts/deploy --host 192.168.1.50
```

The inventory contains a `remote` placeholder with `ansible_connection: ssh`.
At runtime, `--host` supplies its `ansible_host`, so remote machines do not need
to be committed to the inventory. The remote SSH user defaults to the current
control user's name; configure it in `ansible/inventories/production/group_vars/all.yml`
when the target uses a different account. Ansible displays the resolved
deployment target before it applies roles.

## Run Selected Roles

Use `--tag` (or its short form `-t`) to apply only one role:

```bash
./scripts/deploy --tag shell
./scripts/deploy -H mars -t vscode
```

For compatibility, a bare tag is also accepted:

```bash
./scripts/deploy podman
```

Run `./scripts/deploy --help` for all command-line options.

## VS Code Tasks

The workspace provides tasks for installing dependencies, linting, local
deployment, and remote deployment. Run them from **Tasks: Run Task**:

- `ansible: install`
- `ansible: lint`
- `ansible: run all roles`
- `ansible: run by tag`
- `ansible: run all roles remote`
- `ansible: run by tag remote`

The remote tasks prompt for an SSH host; their default is `localhost`.

## Linting

Run YAML and Ansible linting with:

```bash
./scripts/ansible-lint
```

## Repository Layout

```text
ansible/
  inventories/production/hosts.yml  Local and remote deployment entries
  playbooks/workstation.yml         Workstation playbook
  roles/                            Individual workstation roles
scripts/
  deploy                            Local and remote deployment launcher
  install-requirements              Installs Python package requirements
  install-ansible                   Installs Ansible and collections
  ansible-lint                      Runs yamllint and ansible-lint
nvidia/                             Standalone NVIDIA driver helper scripts
```

## NVIDIA Driver Scripts

The scripts in `nvidia/` are standalone helpers for the NVIDIA driver stack on
Debian 12. They are intentionally not managed by the Ansible workstation
playbook.

```bash
sudo ./nvidia/install_nvidia_keyring
sudo ./nvidia/install_nvidia_packages
```
