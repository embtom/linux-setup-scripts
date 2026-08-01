# Linux Setup Scripts

An Ansible-based workstation configuration for Debian and Ubuntu systems. It
installs a consistent developer environment locally or on a remote machine over
SSH.

## Included Configuration

| Tag | Role | Configuration |
| --- | --- | --- |
| `common` | `common` | Base development packages and Node.js 20 |
| `systemd` | `systemd` | `systemd-resolved` and NetworkManager DNS integration |
| `podman` | `podman` | Rootless Podman and Podman Compose configuration |
| `shell` | `shell_config` | Fish, Starship, direnv, fzf, pyenv, fonts, and Konsole profile |
| `scripts` | `system_scripts` | Helper scripts in `/usr/local/bin` |
| `vscode` | `vscode` | VS Code repository, application, settings, and extensions |
| `git` | `git_config` | Global Git configuration |
| `yakuake` | `yakuake` | Yakuake configuration and user systemd service |

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
