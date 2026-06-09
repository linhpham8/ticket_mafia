import boto3
import os

# Đảm bảo region và credentials (vì bạn đang dùng export trong CMD)
os.environ['AWS_DEFAULT_REGION'] = 'ap-southeast-1'   # thay bằng region thật của bạn

session = boto3.Session()
client = session.client('rds')

# Lấy danh sách tất cả RDS instances
response = client.describe_db_instances()

print("=== Danh sách RDS Instances ===")
for db in response['DBInstances']:
    print(f"DB Identifier : {db['DBInstanceIdentifier']}")
    print(f"Engine        : {db['Engine']} {db.get('EngineVersion', '')}")
    print(f"Status        : {db['DBInstanceStatus']}")
    print(f"Endpoint      : {db.get('Endpoint', {}).get('Address', 'N/A')}")
    print(f"Port          : {db.get('Endpoint', {}).get('Port', 'N/A')}")
    print("-" * 60)