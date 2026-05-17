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
