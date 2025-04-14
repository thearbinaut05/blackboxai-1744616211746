import os
import logging
import stripe
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StripeManager:
    """Manages Stripe payment processing and payouts for the Agent Swarm System."""
    
    def __init__(self):
        self.api_key = os.getenv('STRIPE_API_KEY')
        self.connect_client_id = os.getenv('STRIPE_CONNECT_CLIENT_ID')
        stripe.api_key = self.api_key
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
    async def initialize(self):
        """Initialize Stripe configuration."""
        try:
            # Verify Stripe API key
            stripe.Account.retrieve()
            logger.info("Stripe API key verified successfully")
        except stripe.error.AuthenticationError as e:
            logger.error(f"Stripe authentication error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Stripe initialization error: {str(e)}")
            raise

    async def create_payment_intent(self, amount: int, currency: str) -> stripe.PaymentIntent:
        """Create a payment intent for charges."""
        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=amount,
                currency=currency,
                payment_method_types=['card']
            )
            logger.info(f"Created payment intent: {payment_intent.id}")
            return payment_intent
        except stripe.error.StripeError as e:
            logger.error(f"Payment intent creation error: {str(e)}")
            raise

    async def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhooks."""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            
            if event.type == 'payment_intent.succeeded':
                await self._handle_payment_success(event.data.object)
            elif event.type == 'payment_intent.payment_failed':
                await self._handle_payment_failure(event.data.object)
                
            return {'status': 'success', 'event_type': event.type}
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Webhook handling error: {str(e)}")
            raise

    async def _handle_payment_success(self, payment_intent: stripe.PaymentIntent):
        """Handle successful payment."""
        try:
            logger.info(f"Payment succeeded: {payment_intent.id}")
            return {'status': 'success', 'payment_intent_id': payment_intent.id}
        except Exception as e:
            logger.error(f"Payment success handling error: {str(e)}")
            raise

    async def _handle_payment_failure(self, payment_intent: stripe.PaymentIntent):
        """Handle failed payment."""
        try:
            logger.error(f"Payment failed: {payment_intent.id}")
            return {'status': 'failed', 'payment_intent_id': payment_intent.id}
        except Exception as e:
            logger.error(f"Payment failure handling error: {str(e)}")
            raise

    async def create_refund(self, payment_intent_id: str, amount: Optional[int] = None) -> stripe.Refund:
        """Create a refund for a payment."""
        try:
            refund_data = {'payment_intent': payment_intent_id}
            if amount:
                refund_data['amount'] = amount
                
            refund = stripe.Refund.create(**refund_data)
            logger.info(f"Created refund: {refund.id}")
            return refund
            
        except stripe.error.StripeError as e:
            logger.error(f"Refund creation error: {str(e)}")
            raise

    async def create_connect_account(self, email: str, country: str, business_type: str = 'individual') -> stripe.Account:
        """Create a Stripe Connect account for payouts."""
        try:
            account = stripe.Account.create(
                type='custom',
                country=country,
                email=email,
                capabilities={
                    'card_payments': {'requested': True},
                    'transfers': {'requested': True},
                },
                business_type=business_type
            )
            logger.info(f"Created Connect account: {account.id}")
            return account
        except stripe.error.StripeError as e:
            logger.error(f"Connect account creation error: {str(e)}")
            raise

    async def create_account_link(self, account_id: str, refresh_url: str, return_url: str) -> str:
        """Create an account link for Connect onboarding."""
        try:
            account_link = stripe.AccountLink.create(
                account=account_id,
                refresh_url=refresh_url,
                return_url=return_url,
                type='account_onboarding'
            )
            return account_link.url
        except stripe.error.StripeError as e:
            logger.error(f"Account link creation error: {str(e)}")
            raise

    async def create_payout(self, account_id: str, amount: int, currency: str) -> stripe.Payout:
        """Create a payout to a connected account."""
        try:
            payout = stripe.Payout.create(
                amount=amount,
                currency=currency,
                stripe_account=account_id
            )
            logger.info(f"Created payout: {payout.id} to account: {account_id}")
            return payout
        except stripe.error.StripeError as e:
            logger.error(f"Payout creation error: {str(e)}")
            raise

    async def verify_account_status(self, account_id: str) -> Dict[str, Any]:
        """Verify a Connect account's verification status."""
        try:
            account = stripe.Account.retrieve(account_id)
            return {
                'charges_enabled': account.charges_enabled,
                'payouts_enabled': account.payouts_enabled,
                'requirements': account.requirements,
                'verification_status': account.verification
            }
        except stripe.error.StripeError as e:
            logger.error(f"Account verification check error: {str(e)}")
            raise

    async def create_instant_payout(self, account_id: str, amount: int, currency: str, 
                                  destination: str) -> stripe.Payout:
        """Create an instant payout to a connected account's debit card."""
        try:
            payout = stripe.Payout.create(
                amount=amount,
                currency=currency,
                stripe_account=account_id,
                method='instant',
                destination=destination
            )
            logger.info(f"Created instant payout: {payout.id} to account: {account_id}")
            return payout
        except stripe.error.StripeError as e:
            logger.error(f"Instant payout creation error: {str(e)}")
            raise

    async def handle_payout_failure(self, payout_id: str, account_id: str) -> Dict[str, Any]:
        """Handle a failed payout and attempt retry."""
        try:
            payout = stripe.Payout.retrieve(payout_id, stripe_account=account_id)
            if payout.failure_code:
                logger.error(f"Payout failed: {payout_id}, reason: {payout.failure_message}")
                
                # Attempt to retry the payout with same parameters
                retried_payout = stripe.Payout.create(
                    amount=payout.amount,
                    currency=payout.currency,
                    stripe_account=account_id,
                    method=payout.method,
                    destination=payout.destination
                )
                
                return {
                    'original_payout': payout,
                    'retry_payout': retried_payout,
                    'status': 'retried'
                }
            
            return {
                'original_payout': payout,
                'status': 'no_failure'
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Payout failure handling error: {str(e)}")
            raise
