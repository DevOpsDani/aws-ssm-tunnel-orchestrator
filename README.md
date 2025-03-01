<div align="center">


# AWS Secure Tunnel for Integration Tests

This solution allows you to securely open tunnels from your CI environment to other AWS accounts and environments. 
It is designed to be used in CI/CD pipelines to facilitate integration tests with services hosted on different AWS accounts and networks.

</div>


## ⚡️ Quick start
Before you begin, ensure you have the following:

- Python 3.x
- AWS CLI configured with sufficient IAM permissions for AWS Systems Manager and EC2 instances.
- Access to the target AWS environments and the necessary EC2 instances with SSM agent installed and running.
- The `tunnel_sessions.yml` configuration file that defines the host, destination port, region, and instance information for each environment.

## ⚡️ Setup
1. **Clone the repository**:
   ```
   git clone https://github.com/yourusername/aws-secure-tunnel.git
   cd aws-secure-tunnel
   ```
2. **Configure your AWS CLI profile**:
   ```aws configure --profile <your-profile>```
3. **Create a tunnel sessions.yml**:
   This file should contain mappings for your environments (e.g., dev, test, staging) with details of the instances and ports to forward. Example file in the repo.
4. **Set up the instance mappings file**:
   Create a ```instance_mapping.yml``` file that maps each environment to its corresponding EC2 instance, Example file in the repo.

## ⚡️ Usage
```python main.py dev tunnel_sessions.yml```

##👆 **Note**:
The program is using the default profile, if you would like to modify it you can call the script that way 
```AWS_PROFILE=myprofile python main.py dev tunnel_sessions.yml```
Or you can add your profile under main.py 

```
tunnel = ExecuteTunnel(
    env, 
    host, 
    local_port, 
    dest_port, 
    instance, 
    region,
    profile="myprofile"
)
```
