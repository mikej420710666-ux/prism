import { Suspense } from 'react';
import PricingContent from './PricingContent';

export const dynamic = 'force-dynamic';

export default function PricingPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-prism-purple/5 via-prism-pink/5 to-prism-blue/5 py-20 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-prism-purple mx-auto mb-4" />
          <p className="text-gray-600">Loading pricing...</p>
        </div>
      </div>
    }>
      <PricingContent />
    </Suspense>
  );
}
