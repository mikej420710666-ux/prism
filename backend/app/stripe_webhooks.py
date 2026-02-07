"""
Stripe Webhook Handlers
Process Stripe webhook events
"""

from app.models import Subscription, PaymentHistory
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebhookHandler:
    """Handlers for Stripe webhook events"""

    @staticmethod
    def handle_checkout_completed(event_data: dict, db: Session):
        """
        Handle checkout.session.completed event
        Activates subscription after successful checkout

        Args:
            event_data: Stripe event data
            db: Database session
        """
        session = event_data['object']
        subscription_id = session['metadata'].get('subscription_id')

        if subscription_id:
            subscription = db.query(Subscription).filter(
                Subscription.id == int(subscription_id)
            ).first()

            if subscription:
                subscription.stripe_subscription_id = session['subscription']
                subscription.status = 'active'
                db.commit()
                logger.info(f"Activated subscription {subscription.id} for user {subscription.user_id}")

    @staticmethod
    def handle_subscription_updated(event_data: dict, db: Session):
        """
        Handle customer.subscription.updated event
        Syncs subscription status changes from Stripe

        Args:
            event_data: Stripe event data
            db: Database session
        """
        stripe_sub = event_data['object']

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub['id']
        ).first()

        if subscription:
            subscription.status = stripe_sub['status']
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_sub['current_period_start']
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_sub['current_period_end']
            )
            subscription.cancel_at_period_end = stripe_sub['cancel_at_period_end']

            # Update plan type based on status
            if stripe_sub['status'] == 'active':
                subscription.plan_type = 'pro'
            elif stripe_sub['status'] in ['canceled', 'unpaid']:
                subscription.plan_type = 'free'

            db.commit()
            logger.info(f"Updated subscription {subscription.id} status to {stripe_sub['status']}")

    @staticmethod
    def handle_subscription_deleted(event_data: dict, db: Session):
        """
        Handle customer.subscription.deleted event
        Marks subscription as canceled

        Args:
            event_data: Stripe event data
            db: Database session
        """
        stripe_sub = event_data['object']

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub['id']
        ).first()

        if subscription:
            subscription.status = 'canceled'
            subscription.plan_type = 'free'
            subscription.canceled_at = datetime.utcnow()
            db.commit()
            logger.info(f"Canceled subscription {subscription.id}")

    @staticmethod
    def handle_invoice_paid(event_data: dict, db: Session):
        """
        Handle invoice.paid event
        Records successful payment in history

        Args:
            event_data: Stripe event data
            db: Database session
        """
        invoice = event_data['object']

        if not invoice.get('subscription'):
            return

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == invoice['subscription']
        ).first()

        if subscription:
            payment = PaymentHistory(
                subscription_id=subscription.id,
                stripe_payment_intent_id=invoice['payment_intent'],
                stripe_invoice_id=invoice['id'],
                amount=invoice['amount_paid'],
                currency=invoice['currency'],
                status='succeeded',
                description=f"Payment for {invoice['lines']['data'][0]['description']}" if invoice.get('lines') else "Subscription payment",
                paid_at=datetime.fromtimestamp(invoice['status_transitions']['paid_at']) if invoice.get('status_transitions') else datetime.utcnow()
            )
            db.add(payment)
            db.commit()
            logger.info(f"Recorded payment for subscription {subscription.id}")

    @staticmethod
    def handle_invoice_payment_failed(event_data: dict, db: Session):
        """
        Handle invoice.payment_failed event
        Records failed payment and updates subscription status

        Args:
            event_data: Stripe event data
            db: Database session
        """
        invoice = event_data['object']

        if not invoice.get('subscription'):
            return

        subscription = db.query(Subscription).filter(
            Subscription.stripe_subscription_id == invoice['subscription']
        ).first()

        if subscription:
            # Update subscription status
            subscription.status = 'past_due'

            # Record failed payment
            payment = PaymentHistory(
                subscription_id=subscription.id,
                stripe_invoice_id=invoice['id'],
                amount=invoice['amount_due'],
                currency=invoice['currency'],
                status='failed',
                failure_reason=invoice.get('last_finalization_error', {}).get('message', 'Payment failed'),
                description=f"Failed payment for {invoice['lines']['data'][0]['description']}" if invoice.get('lines') else "Subscription payment"
            )
            db.add(payment)
            db.commit()
            logger.warning(f"Payment failed for subscription {subscription.id}")
