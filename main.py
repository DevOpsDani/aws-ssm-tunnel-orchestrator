import logging
import sys
from tunnel import TunnelConfig, PortFinder, ExecuteTunnel

logging.basicConfig(level=logging.INFO)

if len(sys.argv) < 3:
    print("Usage: python main.py <env> <config_file_path>")
    sys.exit(1)

def main():
    """
    Main function to open multipile tunneling sessions
    Use the following way: python main.py env tunnel_sessions.yml 
    """
    env=sys.argv[1]
    config_file = sys.argv[2]
    config = TunnelConfig(config_file, env)
    instance = config.get_instance()
    port = PortFinder()

    for session in config.test_targets:
        host = session['host']
        dest_port = session['destination_port']
        region = session['region']
        local_port = port.find_unused_port()

        
        tunnel = ExecuteTunnel(
            env, 
            host, 
            local_port, 
            dest_port, 
            instance, 
            region
        )
        
        result = tunnel.execute_tunnel()
        
        if result["status"] == "success":
            logging.info(f"Tunnel established successfully for {host}:{dest_port} on local port {local_port}, with PID {result['pid']}")
        else:
            logging.error(f"Failed to establish tunnel: {result['error']}")
    
if __name__ == "__main__":
    main()
