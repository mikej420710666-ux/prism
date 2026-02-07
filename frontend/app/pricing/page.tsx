'use client';

import { useState } from 'react';
import { Check, Sparkles, Zap, TrendingUp, Clock } from 'lucide-react';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { useRouter, useSearchParams } from 'next/navigation';
import { auth } from '@/lib/auth';

export const dynamic = 'force-dynamic';

export default function PricingPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const isAuthenticated = auth.isAuthenticated();

  // Show upgrade canceled message
  const upgradeCanceled = searchParams.get('upgrade') === 'canceled';

  const handleUpgrade = async () => {
    if (!isAuthenticated) {
      router.push('/');
      toast.error('Please sign in to upgrade');
      return;
    }

    setLoading(true);
    try {
      const { url } = await api.createCheckout();
      window.location.href = url;
    } catch (error: any) {
      console.error('Checkout error:', error);
      toast.error(error.response?.data?.detail || 'Failed to start checkout');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-prism-purple/5 via-prism-pink/5 to-prism-blue/5 py-20 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-4 bg-gradient-to-r from-prism-purple via-prism-pink to-prism-blue bg-clip-text text-transparent">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600">
            Start growing your X presence with AI-powered automation
          </p>
        </div>

        {upgradeCanceled && (
          <div className="mb-8 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-center">
            <p className="text-yellow-800">
              Upgrade canceled. You can upgrade anytime!
            </p>
          </div>
        )}

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Free Plan */}
          <div className="card border-2 border-gray-200">
            <div className="p-8">
              <h3 className="text-2xl font-bold mb-2">Free</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold">$0</span>
                <span className="text-gray-600">/month</span>
              </div>

              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Voice analysis & niche detection</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Discover viral posts</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>Basic AI remixing (Claude only)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span>5 scheduled posts per month</span>
                </li>
              </ul>

              <button
                disabled
                className="w-full py-3 px-6 bg-gray-200 text-gray-500 rounded-lg font-semibold cursor-not-allowed"
              >
                Current Plan
              </button>
            </div>
          </div>

          {/* Pro Plan */}
          <div className="card border-2 border-prism-purple relative overflow-hidden">
            {/* Popular Badge */}
            <div className="absolute top-4 right-4 bg-gradient-to-r from-prism-purple to-prism-pink text-white text-xs font-bold px-3 py-1 rounded-full">
              POPULAR
            </div>

            <div className="p-8">
              <h3 className="text-2xl font-bold mb-2">Pro</h3>
              <div className="mb-6">
                <span className="text-5xl font-bold">$24.99</span>
                <span className="text-gray-600">/month</span>
              </div>

              <ul className="space-y-4 mb-8">
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span className="font-semibold">Everything in Free, plus:</span>
                </li>
                <li className="flex items-start gap-3">
                  <Sparkles className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span>Unlimited AI remixing</span>
                </li>
                <li className="flex items-start gap-3">
                  <Zap className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span>Access to all AI models (Claude, Mistral, Grok)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Clock className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span>Unlimited scheduled posts</span>
                </li>
                <li className="flex items-start gap-3">
                  <TrendingUp className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span>Advanced analytics & insights</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span>Auto-pilot mode (coming soon)</span>
                </li>
                <li className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-prism-purple flex-shrink-0 mt-0.5" />
                  <span>Priority support</span>
                </li>
              </ul>

              <button
                onClick={handleUpgrade}
                disabled={loading}
                className="w-full py-3 px-6 bg-gradient-to-r from-prism-purple to-prism-pink hover:opacity-90 disabled:opacity-50 text-white rounded-lg font-semibold transition-opacity flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-5 h-5" />
                    Upgrade to Pro
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-16 text-center text-gray-600">
          <p className="mb-2">All plans include a 7-day money-back guarantee</p>
          <p>Cancel anytime, no questions asked</p>
        </div>
      </div>
    </div>
  );
}
