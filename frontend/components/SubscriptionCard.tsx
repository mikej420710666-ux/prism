'use client';

import { useState, useEffect } from 'react';
import { CreditCard, Calendar, AlertCircle, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api';
import type { Subscription, Payment } from '@/lib/types';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export default function SubscriptionCard() {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    loadSubscriptionData();
  }, []);

  const loadSubscriptionData = async () => {
    try {
      const [subData, paymentData] = await Promise.all([
        api.getSubscription(),
        api.getPaymentHistory(),
      ]);

      setSubscription(subData);
      setPayments(paymentData.payments);
    } catch (error) {
      console.error('Failed to load subscription:', error);
      toast.error('Failed to load subscription data');
    } finally {
      setLoading(false);
    }
  };

  const handleManageBilling = async () => {
    setActionLoading(true);
    try {
      const { url } = await api.createPortal();
      window.location.href = url;
    } catch (error: any) {
      console.error('Portal error:', error);
      toast.error(error.response?.data?.detail || 'Failed to open billing portal');
      setActionLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will retain access until the end of your billing period.')) {
      return;
    }

    setActionLoading(true);
    try {
      const result = await api.cancelSubscription();
      toast.success(result.message);
      await loadSubscriptionData();
    } catch (error: any) {
      console.error('Cancel error:', error);
      toast.error(error.response?.data?.detail || 'Failed to cancel subscription');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReactivate = async () => {
    setActionLoading(true);
    try {
      const result = await api.reactivateSubscription();
      toast.success(result.message);
      await loadSubscriptionData();
    } catch (error: any) {
      console.error('Reactivate error:', error);
      toast.error(error.response?.data?.detail || 'Failed to reactivate subscription');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Subscription Status */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold mb-2">Subscription</h2>
            <div className="flex items-center gap-2">
              {subscription?.is_pro ? (
                <>
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-lg font-semibold text-prism-purple">Pro Plan</span>
                </>
              ) : (
                <>
                  <span className="text-lg font-semibold text-gray-600">Free Plan</span>
                </>
              )}
            </div>
          </div>

          {subscription?.is_pro && (
            <button
              onClick={handleManageBilling}
              disabled={actionLoading}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center gap-2"
            >
              <CreditCard className="w-4 h-4" />
              Manage Billing
            </button>
          )}
        </div>

        {subscription?.is_pro && subscription.current_period_end && (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-gray-600">
              <Calendar className="w-4 h-4" />
              <span>
                {subscription.cancel_at_period_end ? 'Active until' : 'Renews on'}{' '}
                {format(new Date(subscription.current_period_end), 'MMMM d, yyyy')}
              </span>
            </div>

            {subscription.cancel_at_period_end && (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-yellow-800 font-medium">
                      Subscription set to cancel
                    </p>
                    <p className="text-yellow-700 text-sm mt-1">
                      You'll have access to Pro features until {format(new Date(subscription.current_period_end), 'MMMM d, yyyy')}
                    </p>
                    <button
                      onClick={handleReactivate}
                      disabled={actionLoading}
                      className="mt-3 text-sm font-medium text-yellow-800 hover:text-yellow-900 underline"
                    >
                      Reactivate subscription
                    </button>
                  </div>
                </div>
              </div>
            )}

            {!subscription.cancel_at_period_end && (
              <button
                onClick={handleCancelSubscription}
                disabled={actionLoading}
                className="text-sm text-red-600 hover:text-red-700 font-medium"
              >
                Cancel subscription
              </button>
            )}
          </div>
        )}

        {!subscription?.is_pro && (
          <a
            href="/pricing"
            className="inline-block mt-4 px-6 py-3 bg-gradient-to-r from-prism-purple to-prism-pink text-white rounded-lg font-semibold hover:opacity-90 transition-opacity"
          >
            Upgrade to Pro
          </a>
        )}
      </div>

      {/* Payment History */}
      {payments.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold mb-4">Payment History</h3>
          <div className="space-y-3">
            {payments.slice(0, 5).map((payment) => (
              <div key={payment.id} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div>
                  <p className="font-medium">{payment.description}</p>
                  {payment.paid_at && (
                    <p className="text-sm text-gray-500">
                      {format(new Date(payment.paid_at), 'MMMM d, yyyy')}
                    </p>
                  )}
                  {payment.failure_reason && (
                    <p className="text-sm text-red-600">{payment.failure_reason}</p>
                  )}
                </div>
                <div className="text-right">
                  <p className="font-semibold">
                    ${payment.amount.toFixed(2)} {payment.currency}
                  </p>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      payment.status === 'succeeded'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'
                    }`}
                  >
                    {payment.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
