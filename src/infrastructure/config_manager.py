import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for the Agent Swarm System."""
    
    def __init__(self):
        self.config = {
            'stripe': {
                'api_key': os.getenv('STRIPE_API_KEY'),
                'connect_client_id': os.getenv('STRIPE_CONNECT_CLIENT_ID'),
                'webhook_secret': os.getenv('STRIPE_WEBHOOK_SECRET'),
                'payout_settings': {
                    'default_currency': 'usd',
                    'min_payout_amount': 100,  # $1.00
                    'max_payout_amount': 999999,  # $9,999.99
                    'instant_payout_enabled': True,
                    'instant_payout_fee_percent': 1.5,
                    'retry_failed_payouts': True,
                    'max_retry_attempts': 3,
                    'retry_delay_seconds': 3600  # 1 hour
                }
            },
            'aws': {
                'region': os.getenv('AWS_REGION', 'us-east-1'),
                'dynamodb_table': os.getenv('DYNAMODB_TABLE'),
                's3_bucket': os.getenv('S3_BUCKET')
            },
            'system': {
                'environment': os.getenv('ENVIRONMENT', 'development'),
                'log_level': os.getenv('LOG_LEVEL', 'INFO'),
                'enable_monitoring': True
            }
        }
        
    def get_stripe_config(self) -> Dict[str, Any]:
        """Get Stripe-related configuration."""
        return self.config['stripe']
        
    def get_payout_settings(self) -> Dict[str, Any]:
        """Get payout-specific settings."""
        return self.config['stripe']['payout_settings']
        
    def update_payout_settings(self, settings: Dict[str, Any]) -> None:
        """Update payout settings."""
        try:
            self.config['stripe']['payout_settings'].update(settings)
            logger.info("Payout settings updated successfully")
        except Exception as e:
            logger.error(f"Failed to update payout settings: {str(e)}")
            raise
            
    def validate_payout_amount(self, amount: int) -> bool:
        """Validate if a payout amount is within allowed limits."""
        settings = self.get_payout_settings()
        return settings['min_payout_amount'] <= amount <= settings['max_payout_amount']
        
    def calculate_instant_payout_fee(self, amount: int) -> int:
        """Calculate fee for instant payouts."""
        settings = self.get_payout_settings()
        if not settings['instant_payout_enabled']:
            raise ValueError("Instant payouts are not enabled")
            
        fee_percent = settings['instant_payout_fee_percent']
        return int(amount * (fee_percent / 100))
        
    def should_retry_failed_payout(self, attempt_count: int) -> bool:
        """Determine if a failed payout should be retried."""
        settings = self.get_payout_settings()
        return (settings['retry_failed_payouts'] and 
                attempt_count < settings['max_retry_attempts'])
                
    def get_retry_delay(self) -> int:
        """Get delay in seconds before retrying a failed payout."""
        return self.get_payout_settings()['retry_delay_seconds']
        
    def export_config(self, filepath: Optional[str] = None) -> str:
        """Export current configuration to JSON."""
        try:
            config_json = json.dumps(self.config, indent=2)
            if filepath:
                with open(filepath, 'w') as f:
                    f.write(config_json)
            return config_json
        except Exception as e:
            logger.error(f"Failed to export configuration: {str(e)}")
            raise
            
    def import_config(self, filepath: str) -> None:
        """Import configuration from JSON file."""
        try:
            with open(filepath, 'r') as f:
                new_config = json.load(f)
            self.config.update(new_config)
            logger.info("Configuration imported successfully")
        except Exception as e:
            logger.error(f"Failed to import configuration: {str(e)}")
            raise
