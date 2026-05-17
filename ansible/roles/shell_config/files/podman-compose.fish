# Fish completions for podman-compose
complete -c podman-compose -f

# Subcommands
complete -c podman-compose -n __fish_use_subcommand -a help      -d 'show help'
complete -c podman-compose -n __fish_use_subcommand -a version   -d 'show version'
complete -c podman-compose -n __fish_use_subcommand -a wait      -d 'wait for running containers to stop'
complete -c podman-compose -n __fish_use_subcommand -a systemd   -d 'create systemd unit file'
complete -c podman-compose -n __fish_use_subcommand -a pull      -d 'pull stack images'
complete -c podman-compose -n __fish_use_subcommand -a push      -d 'push stack images'
complete -c podman-compose -n __fish_use_subcommand -a build     -d 'build stack images'
complete -c podman-compose -n __fish_use_subcommand -a up        -d 'create and start the entire stack'
complete -c podman-compose -n __fish_use_subcommand -a down      -d 'tear down entire stack'
complete -c podman-compose -n __fish_use_subcommand -a ps        -d 'show status of containers'
complete -c podman-compose -n __fish_use_subcommand -a run       -d 'run a one-off command'
complete -c podman-compose -n __fish_use_subcommand -a exec      -d 'execute a command in a running container'
complete -c podman-compose -n __fish_use_subcommand -a start     -d 'start specific services'
complete -c podman-compose -n __fish_use_subcommand -a stop      -d 'stop specific services'
complete -c podman-compose -n __fish_use_subcommand -a restart   -d 'restart specific services'
complete -c podman-compose -n __fish_use_subcommand -a logs      -d 'show logs from services'
complete -c podman-compose -n __fish_use_subcommand -a config    -d 'display the compose file'
complete -c podman-compose -n __fish_use_subcommand -a port      -d 'print public port for a port binding'
complete -c podman-compose -n __fish_use_subcommand -a pause     -d 'pause all running containers'
complete -c podman-compose -n __fish_use_subcommand -a unpause   -d 'unpause all running containers'
complete -c podman-compose -n __fish_use_subcommand -a kill      -d 'kill one or more running containers'
complete -c podman-compose -n __fish_use_subcommand -a stats     -d 'display stats for services'
complete -c podman-compose -n __fish_use_subcommand -a images    -d 'list images used by containers'

# Global options
complete -c podman-compose -s h -l help         -d 'show help'
complete -c podman-compose -s v -l version      -d 'show version'
complete -c podman-compose -s f -l file         -d 'specify compose file' -r
complete -c podman-compose -s p -l project-name -d 'alternate project name' -r
complete -c podman-compose        -l env-file   -d 'alternate environment file' -r
complete -c podman-compose        -l profile    -d 'profile to enable' -r
complete -c podman-compose        -l no-ansi    -d 'do not print ANSI control characters'
complete -c podman-compose        -l no-cleanup -d 'do not remove existing pod & containers'
complete -c podman-compose        -l dry-run    -d 'simulate commands without executing'
complete -c podman-compose        -l verbose    -d 'print debugging output'
complete -c podman-compose        -l parallel   -d 'parallel limit' -r
