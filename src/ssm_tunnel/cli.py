import logging
import argparse
from ssm_tunnel.commands import TunnelConfig, ExecuteTunnel


def main():
    parser = argparse.ArgumentParser(
        prog="ssm_tunnel",
        description="SSM Tunnel CLI")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available commands")

    # sshx command
    tunnel_parser = subparsers.add_parser(
        "start_session", help="Start Tunneling Session")
    tunnel_parser.add_argument("env", help="Environment")
    tunnel_parser.add_argument("config_file", help="Config file path")

    args = parser.parse_args()

    env = args.env
    config_file = args.config_file

    if args.command == "start_session":
        config = TunnelConfig(config_file, env)
        default_instance = config.get_instance()

        for session in config.test_targets:
            host = session['host']
            dest_port = session['destination_port']
            local_port = session['local_port']
            profile = session.get('use_profile')

            instance = (
                config.get_instance(use_profile=profile)
                if profile else default_instance
            )      

            tunnel = ExecuteTunnel(
                env,
                host,
                local_port,
                dest_port,
                instance,
                profile
            )

            tunnel.add_entry_hosts_file()
            result = tunnel.execute_tunnel()

            if result["status"] == "success":
                logging.info(
                    "Tunnel established successfully for %s:%s on local port %s, with PID %s",
                    host, dest_port, local_port, result['pid']
                )
                print(" ")
            else:
                logging.error(
                    "Failed to establish tunnel: %s",
                    result['error']
                )
                print(" ")

if __name__ == "__main__":
    main()
