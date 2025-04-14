import os
import logging
import aioboto3
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class AWSManager:
    """Manages AWS service interactions for the Agent Swarm System."""
    
    def __init__(self):
        self.session = aioboto3.Session()
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
    async def initialize(self):
        """Initialize AWS services."""
        try:
            # Verify AWS credentials
            async with self.session.client('sts') as sts:
                await sts.get_caller_identity()
            logger.info("AWS credentials verified successfully")
        except Exception as e:
            logger.error(f"AWS initialization error: {str(e)}")
            raise

    async def create_lambda_function(self, name: str, code: Dict[str, Any], 
                                   handler: str, role: str) -> Dict[str, Any]:
        """Create a Lambda function for agent execution."""
        try:
            async with self.session.client('lambda') as lambda_client:
                response = await lambda_client.create_function(
                    FunctionName=name,
                    Runtime='python3.9',
                    Role=role,
                    Handler=handler,
                    Code=code,
                    Environment={
                        'Variables': {
                            'SWARM_ENV': os.getenv('SWARM_ENV', 'production')
                        }
                    },
                    MemorySize=256,
                    Timeout=30
                )
                return response
        except ClientError as e:
            logger.error(f"Lambda creation error: {str(e)}")
            raise

    async def invoke_lambda(self, function_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a Lambda function."""
        try:
            async with self.session.client('lambda') as lambda_client:
                response = await lambda_client.invoke(
                    FunctionName=function_name,
                    InvocationType='RequestResponse',
                    Payload=payload
                )
                return response
        except ClientError as e:
            logger.error(f"Lambda invocation error: {str(e)}")
            raise

    async def store_pattern(self, pattern_id: str, pattern_data: Dict[str, Any]) -> bool:
        """Store pattern data in DynamoDB."""
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(os.getenv('PATTERNS_TABLE', 'swarm_patterns'))
                await table.put_item(Item={
                    'pattern_id': pattern_id,
                    'data': pattern_data,
                    'status': 'active'
                })
                return True
        except ClientError as e:
            logger.error(f"DynamoDB storage error: {str(e)}")
            raise

    async def get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve pattern data from DynamoDB."""
        try:
            async with self.session.resource('dynamodb') as dynamodb:
                table = await dynamodb.Table(os.getenv('PATTERNS_TABLE', 'swarm_patterns'))
                response = await table.get_item(Key={'pattern_id': pattern_id})
                return response.get('Item')
        except ClientError as e:
            logger.error(f"DynamoDB retrieval error: {str(e)}")
            raise

    async def create_sqs_queue(self, queue_name: str) -> str:
        """Create an SQS queue for agent communication."""
        try:
            async with self.session.client('sqs') as sqs:
                response = await sqs.create_queue(
                    QueueName=queue_name,
                    Attributes={
                        'VisibilityTimeout': '300',
                        'MessageRetentionPeriod': '86400'
                    }
                )
                return response['QueueUrl']
        except ClientError as e:
            logger.error(f"SQS queue creation error: {str(e)}")
            raise

    async def send_message(self, queue_url: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to an SQS queue."""
        try:
            async with self.session.client('sqs') as sqs:
                response = await sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=str(message)
                )
                return response
        except ClientError as e:
            logger.error(f"SQS message sending error: {str(e)}")
            raise

    async def receive_messages(self, queue_url: str, max_messages: int = 10) -> list:
        """Receive messages from an SQS queue."""
        try:
            async with self.session.client('sqs') as sqs:
                response = await sqs.receive_message(
                    QueueUrl=queue_url,
                    MaxNumberOfMessages=max_messages,
                    WaitTimeSeconds=20
                )
                return response.get('Messages', [])
        except ClientError as e:
            logger.error(f"SQS message receiving error: {str(e)}")
            raise

    async def store_metrics(self, metrics: Dict[str, Any]) -> bool:
        """Store metrics in CloudWatch."""
        try:
            async with self.session.client('cloudwatch') as cloudwatch:
                await cloudwatch.put_metric_data(
                    Namespace='SwarmMetrics',
                    MetricData=[
                        {
                            'MetricName': name,
                            'Value': value,
                            'Unit': 'Count'
                        }
                        for name, value in metrics.items()
                    ]
                )
                return True
        except ClientError as e:
            logger.error(f"CloudWatch metrics storage error: {str(e)}")
            raise

    async def create_s3_bucket(self, bucket_name: str) -> bool:
        """Create an S3 bucket for pattern storage."""
        try:
            async with self.session.client('s3') as s3:
                await s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={
                        'LocationConstraint': self.region
                    }
                )
                return True
        except ClientError as e:
            logger.error(f"S3 bucket creation error: {str(e)}")
            raise

    async def store_file_s3(self, bucket: str, key: str, data: bytes) -> bool:
        """Store a file in S3."""
        try:
            async with self.session.client('s3') as s3:
                await s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=data
                )
                return True
        except ClientError as e:
            logger.error(f"S3 file storage error: {str(e)}")
            raise

    async def get_file_s3(self, bucket: str, key: str) -> bytes:
        """Retrieve a file from S3."""
        try:
            async with self.session.client('s3') as s3:
                response = await s3.get_object(
                    Bucket=bucket,
                    Key=key
                )
                return await response['Body'].read()
        except ClientError as e:
            logger.error(f"S3 file retrieval error: {str(e)}")
            raise

    async def setup_monitoring(self) -> bool:
        """Set up CloudWatch monitoring and alarms."""
        try:
            async with self.session.client('cloudwatch') as cloudwatch:
                # Create CPU utilization alarm
                await cloudwatch.put_metric_alarm(
                    AlarmName='SwarmCPUUtilization',
                    MetricName='CPUUtilization',
                    Namespace='AWS/Lambda',
                    Statistic='Average',
                    Period=300,
                    EvaluationPeriods=2,
                    Threshold=80,
                    ComparisonOperator='GreaterThanThreshold',
                    AlarmActions=[os.getenv('ALARM_SNS_TOPIC')]
                )
                
                # Create error rate alarm
                await cloudwatch.put_metric_alarm(
                    AlarmName='SwarmErrorRate',
                    MetricName='Errors',
                    Namespace='SwarmMetrics',
                    Statistic='Sum',
                    Period=300,
                    EvaluationPeriods=1,
                    Threshold=5,
                    ComparisonOperator='GreaterThanThreshold',
                    AlarmActions=[os.getenv('ALARM_SNS_TOPIC')]
                )
                return True
        except ClientError as e:
            logger.error(f"CloudWatch alarm setup error: {str(e)}")
            raise

    async def cleanup_resources(self):
        """Clean up AWS resources."""
        # Implementation for cleaning up resources when needed
        pass
