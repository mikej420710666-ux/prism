'use client';

import SubscriptionCard from '@/components/SubscriptionCard';

export default function SettingsPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold mb-8">Account Settings</h1>
      <SubscriptionCard />
    </div>
  );
}
