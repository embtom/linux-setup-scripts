# ------------------------------------------------------------------------------------
# INTERACTIVE GUARD
# ------------------------------------------------------------------------------------
if not status is-interactive
    exec bash
end

# ------------------------------------------------------------------------------------
# PATH
# ------------------------------------------------------------------------------------
fish_add_path ~/.local/bin

# ------------------------------------------------------------------------------------
# Starship Prompt
# ------------------------------------------------------------------------------------
starship init fish | source

# ------------------------------------------------------------------------------------
# direnv
# ------------------------------------------------------------------------------------
if type -q direnv
    direnv hook fish | source
end

# ------------------------------------------------------------------------------------
# Fish UI behaviour
# ------------------------------------------------------------------------------------
set -g fish_greeting ""
set -g fish_color_autosuggestion brblack

set -U fish_autosuggestion_enabled 1
set -U fish_complete_fuzzy_match 1
set -U fish_case_sensitive 0

set -U fish_pager_show_description 0
set -U fish_pager_show_prefix 1
set -U fish_pager_prefix_position left
set -U fish_pager_color_completion normal

# ------------------------------------------------------------------------------------
# Fish completions
# ------------------------------------------------------------------------------------
podman completion fish | source

# ------------------------------------------------------------------------------------
# pyenv
# ------------------------------------------------------------------------------------
if type -q pyenv
    set -Ux PYENV_ROOT $HOME/.pyenv
    set -U fish_user_paths $PYENV_ROOT/bin $fish_user_paths

    pyenv init - fish | source
    pyenv virtualenv-init - | source
end

# ------------------------------------------------------------------------------------
# Aliases
# ------------------------------------------------------------------------------------
alias pse='ps -Leo pid,tid,class,priority,rtprio,ni,pcpu,stat,cmd'
alias lsb='lsblk -o NAME,PARTLABEL,MAJ:MIN,FSTYPE,SIZE,MOUNTPOINT,RO'
alias ls='lsd'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -F'

# ------------------------------------------------------------------------------------
# fzf keybindings
# ------------------------------------------------------------------------------------
if type -q fzf_key_bindings
    fzf_key_bindings
end

