"""
Stripe Service
Handles Stripe API operations for subscriptions and payments
"""

import stripe
from app.database import settings
from app.models import User, Subscription
from typing import Dict

stripe.api_key = settings.stripe_secret_key


class StripeService:
    """Service for Stripe API interactions"""

    @staticmethod
    def create_customer(user: User) -> str:
        """
        Create Stripe customer for user

        Args:
            user: User model instance

        Returns:
            Stripe customer ID
        """
        customer = stripe.Customer.create(
            email=user.email if user.email else None,
            metadata={
                "user_id": user.id,
                "username": user.username,
                "x_username": user.x_username
            }
        )
        return customer.id

    @staticmethod
    def create_checkout_session(
        user: User,
        subscription: Subscription,
        success_url: str,
        cancel_url: str
    ) -> Dict:
        """
        Create Stripe Checkout session for subscription

        Args:
            user: User model instance
            subscription: Subscription model instance
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect if user cancels

        Returns:
            Dictionary with session_id and checkout URL
        """
        session = stripe.checkout.Session.create(
            customer=subscription.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': settings.stripe_pro_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "subscription_id": subscription.id
            },
            allow_promotion_codes=True,
            billing_address_collection='auto',
        )
        return {
            "session_id": session.id,
            "url": session.url
        }

    @staticmethod
    def create_portal_session(customer_id: str, return_url: str) -> Dict:
        """
        Create Stripe Customer Portal session

        Args:
            customer_id: Stripe customer ID
            return_url: URL to return to after portal interaction

        Returns:
            Dictionary with portal URL
        """
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return {"url": session.url}

    @staticmethod
    def cancel_subscription(stripe_subscription_id: str) -> stripe.Subscription:
        """
        Cancel subscription at period end

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Updated Stripe Subscription object
        """
        return stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )

    @staticmethod
    def reactivate_subscription(stripe_subscription_id: str) -> stripe.Subscription:
        """
        Reactivate a subscription set to cancel

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Updated Stripe Subscription object
        """
        return stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=False
        )

    @staticmethod
    def get_subscription(stripe_subscription_id: str) -> stripe.Subscription:
        """
        Retrieve subscription from Stripe

        Args:
            stripe_subscription_id: Stripe subscription ID

        Returns:
            Stripe Subscription object
        """
        return stripe.Subscription.retrieve(stripe_subscription_id)

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str):
        """
        Verify and construct webhook event

        Args:
            payload: Raw request body
            sig_header: Stripe signature header

        Returns:
            Verified Stripe Event object

        Raises:
            ValueError: Invalid payload
            stripe.error.SignatureVerificationError: Invalid signature
        """
        return stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
