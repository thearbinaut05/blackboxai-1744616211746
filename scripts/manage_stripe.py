#!/usr/bin/env python3
import os
import sys
import stripe
import argparse
from typing import Dict, Any
from pathlib import Path

def setup_stripe() -> Dict[str, Any]:
    """Setup Stripe configuration from environment variables."""
    try:
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        account = stripe.Account.retrieve()
        return {
            'account_id': account.id,
            'charges_enabled': account.charges_enabled,
            'payouts_enabled': account.payouts_enabled,
            'details_submitted': account.details_submitted
        }
    except stripe.error.AuthenticationError:
        print("Authentication failed. Check your API keys.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

def verify_webhook() -> bool:
    """Verify webhook configuration."""
    try:
        webhooks = stripe.WebhookEndpoint.list(limit=1)
        return len(webhooks.data) > 0
    except Exception:
        return False

def check_balance() -> Dict[str, Any]:
    """Check account balance."""
    try:
        balance = stripe.Balance.retrieve()
        return {
            'available': balance.available,
            'pending': balance.pending,
            'instant_available': balance.instant_available
        }
    except Exception as e:
        print(f"Error checking balance: {str(e)}")
        return None

def verify_capabilities() -> Dict[str, bool]:
    """Verify account capabilities."""
    try:
        account = stripe.Account.retrieve()
        capabilities = account.capabilities
        return {
            'card_payments': capabilities.get('card_payments') == 'active',
            'transfers': capabilities.get('transfers') == 'active',
            'sepa_debit': capabilities.get('sepa_debit') == 'active',
            'instant_payouts': capabilities.get('instant_payouts') == 'active'
        }
    except Exception as e:
        print(f"Error checking capabilities: {str(e)}")
        return None

def setup_payout_schedule(interval: str = 'daily') -> bool:
    """Setup automatic payout schedule."""
    try:
        account = stripe.Account.modify(
            settings={
                'payouts': {
                    'schedule': {
                        'interval': interval
                    }
                }
            }
        )
        return True
    except Exception as e:
        print(f"Error setting payout schedule: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Manage Stripe Integration')
    parser.add_argument('--check', action='store_true', help='Check Stripe setup')
    parser.add_argument('--balance', action='store_true', help='Check account balance')
    parser.add_argument('--verify-webhook', action='store_true', help='Verify webhook setup')
    parser.add_argument('--verify-capabilities', action='store_true', help='Verify account capabilities')
    parser.add_argument('--setup-payouts', choices=['daily', 'weekly', 'monthly'], 
                       help='Setup automatic payout schedule')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
        
    if args.check:
        status = setup_stripe()
        print("\nStripe Account Status:")
        print("---------------------")
        print(f"Account ID: {status['account_id']}")
        print(f"Charges Enabled: {status['charges_enabled']}")
        print(f"Payouts Enabled: {status['payouts_enabled']}")
        print(f"Details Submitted: {status['details_submitted']}")
        
    if args.balance:
        balance = check_balance()
        if balance:
            print("\nAccount Balance:")
            print("---------------")
            for currency in balance['available']:
                print(f"Available ({currency.currency}): {currency.amount/100:.2f}")
            for currency in balance['pending']:
                print(f"Pending ({currency.currency}): {currency.amount/100:.2f}")
                
    if args.verify_webhook:
        has_webhook = verify_webhook()
        print("\nWebhook Status:")
        print("--------------")
        print("Configured" if has_webhook else "Not Configured")

    if args.verify_capabilities:
        caps = verify_capabilities()
        if caps:
            print("\nAccount Capabilities:")
            print("-------------------")
            for cap, status in caps.items():
                print(f"{cap.replace('_', ' ').title()}: {'Enabled' if status else 'Disabled'}")

    if args.setup_payouts:
        success = setup_payout_schedule(args.setup_payouts)
        print("\nPayout Schedule:")
        print("---------------")
        print(f"{'Successfully set' if success else 'Failed to set'} {args.setup_payouts} payouts")

if __name__ == "__main__":
    main()
