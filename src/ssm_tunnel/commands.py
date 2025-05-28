import subprocess
import socket
import random
import logging
import os
import boto3
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)


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
            logging.error("Error loading tunnel sessions: %s", e)
            return {}

    # Find the jump server dynamically
    def get_instance(self, use_profile: str = None):
        """
        Return relevant instance per environment
        """
        if use_profile:
            profile=use_profile
        else:
            profile=self._env

        try:
            session = boto3.Session(profile_name=profile)
            region = session.region_name
            ec2_client = session.client('ec2', region_name=region)
            query_instance = ec2_client.describe_instances(
                Filters=[{"Name": "tag:SSMTunneling", "Values": [f"{profile}"]}]
            )

            if not query_instance["Reservations"]:
                logging.warning("No EC2 instances found for SSM tunneling.")

            # Extracting instance ID(s)
            instance_ids = [
                instance["InstanceId"]
                for reservation in query_instance["Reservations"]
                for instance in reservation["Instances"]
            ]

            if instance_ids:
                random_instance = random.choice(instance_ids)
                return random_instance

        except Exception as e:
            logging.error("Error retrieving EC2 instance: %s", e)


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
    def __init__(
            self,
            env: str,
            host: str,
            local_port: int,
            dest_port: int,
            instance: str,
            use_profile: str = None
            ):
        self._env = env
        self._host = host
        self._local_port = local_port
        self._dest_port = dest_port
        self._instance = instance
        self._use_profile = use_profile

    def add_entry_hosts_file(self):
        """
        Add entry to /etc/hosts to be able to resolve the destionation host
        """
        entry = f"127.0.0.1 {self._host}\n"
        hosts_file = "/etc/hosts"

        try:
            with open(hosts_file, "a") as file:
                file.write(entry)
        except FileNotFoundError as exception:
            logging.error(
                "Error modifying %s: %s",
                hosts_file, exception
            )

    def execute_tunnel(self):
        """
        Execute the SSM tunnel command to establish port forwarding.
        Returns the output of the command or an error message.
        Using sub process as "Session Manager plugin for the AWS CLI" is required
        """
        if self._use_profile:
            profile=self._use_profile
        else:
            profile=self._env

        session = boto3.Session(profile_name=profile)
        region = session.region_name

        command = [
            "aws", "ssm", "start-session",
            "--target", self._instance,
            "--region", region,
            "--profile", profile,
            "--document-name", "AWS-StartPortForwardingSessionToRemoteHost",
            "--cli-connect-timeout", "1800",
            "--parameters", f'{{"host":["{self._host}"],"portNumber":["{self._dest_port}"], "localPortNumber":["{self._local_port}"]}}'
        ]

        try:
            logging.info(
                "Starting SSM session: Instance=%s, Region=%s",
                self._instance, region
                )
            process = subprocess.Popen(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid)
            return {"status": "success", "pid": process.pid}

        except Exception as e:
            return {"status": "error", "error": str(e)}
