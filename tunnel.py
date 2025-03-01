import yaml
import subprocess
import socket
import random
import logging
import os


class TunnelConfig:
    def __init__(self, config_file: str, env: str):
        self._env = env
        self._config_file = config_file    
        self._sessions = self.load_sessions()
        
    @property
    def test_targets(self):
        """
        Retrieves the relevant hosts & ports for the requested environment
        """
        return self._sessions.get(self._env)
        
    def load_sessions(self):
        """
        Load tunnel session mappings from env file
        """
        try:
            with open(self._config_file, "r") as config:
                data = yaml.safe_load(config)
                return data.get("tunnel_sessions", {})
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error loading tunnel sessions: {e}")
            return {}
        
    
    def get_instance(self):
        """    
        Return relevant instance per environment 
        """
        try: 
            config_file = "./instance_mapping.yml"
            with open(config_file, "r") as config:
                data = yaml.safe_load(config)
                return data.get("instance_mapping", {}).get(self._env, "Unknown environment")
        except (FileNotFoundError, yaml.YAMLError) as e:
            print(f"Error loading tunnel sessions: {e}")
            return {}
    
class PortFinder:
    def __init__(self, port_range=(32768, 61000), max_attempts=20):
        self.port_range = port_range
        self.max_attempts = max_attempts

    def is_port_in_use(self, port):
        """Check if a port is already in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", port)) == 0

    def find_unused_port(self):
        """
        Find an available port within the specified range.
        Stops after max_attempts to avoid infinite loops.
        """
        for _ in range(self.max_attempts):
            port = random.randint(*self.port_range)
            if not self.is_port_in_use(port):
                return port

        logging.error("Failed to find an unused port after multiple attempts.")
        return None


class ExecuteTunnel:
    def __init__(self, env: str, host: str, local_port: int, dest_port: int, instance: str, region: str, profile: str = "default"):
        self._env = env
        self._host = host
        self._local_port = local_port
        self._dest_port = dest_port
        self._instance = instance
        self._region = region
        self._profile = profile

    def execute_tunnel(self):
        """
        Execute the SSM tunnel command to establish port forwarding.
        Returns the output of the command or an error message.
        """
        command = [
            "aws", "ssm", "start-session",
            "--target", self._instance,
            "--region", self._region,
            "--profile", self._profile,
            "--document-name", "AWS-StartPortForwardingSessionToRemoteHost",
            "--parameters", f'{{"host":["{self._host}"],"portNumber":["{self._dest_port}"], "localPortNumber":["{self._local_port}"]}}'
        ]
        
        try:
            process = subprocess.Popen(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid
            )
            return {"status": "success", "pid": process.pid}
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
