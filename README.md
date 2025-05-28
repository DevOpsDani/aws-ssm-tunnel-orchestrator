<div align="center">


# AWS Secure Tunnel for Integration Tests

This solution allows you to securely open tunnels from your CI environment to other AWS accounts and environments. 
It is designed to be used in CI/CD pipelines to facilitate integration tests with services hosted on different AWS accounts and networks.

</div>

## ⚡️ Quick start
Install the library
 ```
 python -m pip install ssm_tunnel
 ```
## ⚡️ Usage
Tag the instances with correlation to the environment they are deployed, for examle:
```Key:SSMTunneling, Value:(dev,test,staging,etc...)```

Example usage - this library is configured to use as CLI tool
```
usage: ssm_tunnel start_session [-h] env config_file

positional arguments:
  env          Environment
  config_file  Config file path

options:
  -h, --help   show this help message and exit
```

Your config file should be structured as follows:
```
tunnel_sessions:
  dev:
  - host: "example.com"
    destination_port: 443
    local_port: 30123
  - host: "example.com"
    destination_port: 443
    local_port: 30124

  test:
  - host: "example.com"
    destination_port: 443

  staging:
  - host: "example.com"
    destination_port: 443

  cell:
   - host:
     destination_port: 443
```
To open tunnels as specified in the `config.yaml`, run the following command. This will open two tunnels for the `dev` environment, listening on local ports 30123 and 30124, and forwarding traffic to the configured destination host.
```
ssm_tunnel start_session dev config.yaml
```
## 👆 **Note**:
The solution assumes that your ```.aws/credentials``` are on order per environment for example
```
[dev]
aws_access_key_id = some keys
aws_secret_access_key = some secret
aws_session_token = some session token

[test]
aws_access_key_id = some keys
aws_secret_access_key = some secret
aws_session_token = some session token

[staging]
aws_access_key_id = some keys
aws_secret_access_key = some secret
aws_session_token = some session token
```
