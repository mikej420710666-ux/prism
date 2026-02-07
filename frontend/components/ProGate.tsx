'use client';

import { useEffect, useState } from 'react';
import { Lock } from 'lucide-react';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface ProGateProps {
  children: React.ReactNode;
  feature: string;
}

export default function ProGate({ children, feature }: ProGateProps) {
  const router = useRouter();
  const [isPro, setIsPro] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkProStatus();
  }, []);

  const checkProStatus = async () => {
    try {
      const subscription = await api.getSubscription();
      setIsPro(subscription.is_pro);
    } catch (error) {
      console.error('Failed to check pro status:', error);
      setIsPro(false);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-prism-purple"></div>
      </div>
    );
  }

  if (!isPro) {
    return (
      <div className="max-w-2xl mx-auto py-20 px-4 text-center">
        <div className="card">
          <Lock className="w-16 h-16 text-prism-purple mx-auto mb-4" />
          <h2 className="text-2xl font-bold mb-2">Pro Feature</h2>
          <p className="text-gray-600 mb-6">
            {feature} is available on the Pro plan. Upgrade to unlock this feature and more!
          </p>
          <button
            onClick={() => router.push('/pricing')}
            className="px-8 py-3 bg-gradient-to-r from-prism-purple to-prism-pink text-white rounded-lg font-semibold hover:opacity-90 transition-opacity"
          >
            Upgrade to Pro
          </button>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
