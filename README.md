# linux-setup-scripts

Ansible-based workstation setup for Debian systems.

## What it sets up

| Role | What it does |
|---|---|
| `common` | installs base packages (curl, wget, git, …) |
| `shell_config` | fish shell, starship prompt, direnv, fzf, lsd, pyenv, Hack Nerd Font, Konsole profile |
| `podman` | rootless podman, podman-compose, user socket + linger, containers.conf |

## Requirements

- Debian / Ubuntu based system
- `sudo` access for package installation

## First-time setup

```bash
# 1. Install Python and pipx dependencies
./install-requirements

# 2. Install ansible-core and Ansible collections
./install-ansible

# 3. Run the playbook
./run-ansible
```

## Day-to-day usage

```bash
./run-ansible
```

To run only a specific role use tags:

```bash
cd ansible
ansible-playbook -i inventories/production/hosts.yml playbooks/workstation.yml \
  --ask-become-pass --tags shell
```

Available tags: `common`, `shell`, `podman`

## Repository layout

```
ansible/
  ansible.cfg
  requirements.yml
  inventories/production/
    hosts.yml
    group_vars/all.yml
  playbooks/
    workstation.yml
  roles/
    common/
    shell_config/
    podman/
install-requirements   # installs python3, pip, venv
install-ansible        # installs ansible-core + collections
run-ansible            # runs the workstation playbook
requirements.txt       # pip packages (pipx, podman-compose)
requirements.yml       # Ansible collections
```

## NVIDIA (manual scripts)

The `nvidia/` folder contains standalone shell scripts for setting up the NVIDIA driver stack on Debian 12. These are **not** part of the Ansible playbook and must be run manually.

| Script | Purpose |
|---|---|
| `install_nvidia_keyring` | downloads and installs the CUDA apt keyring from NVIDIA |
| `install_nvidia_packages` | installs the full NVIDIA driver stack at a pinned version |
| `list_installed_nvidia_packages` | lists currently installed NVIDIA packages and their versions |
| `installed_nvidia_packages_version_580` | reference list of all packages installed for driver version 580 |

### Usage

```bash
# Step 1 — add the NVIDIA apt repository keyring
sudo ./nvidia/install_nvidia_keyring

# Step 2 — install the driver stack (edit VERSION in the script first if needed)
sudo ./nvidia/install_nvidia_packages
```
