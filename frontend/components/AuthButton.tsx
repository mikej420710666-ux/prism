'use client';

import { useState } from 'react';
import { Twitter } from 'lucide-react';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

export default function AuthButton() {
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    try {
      const { authorization_url } = await api.startOAuth();

      // Redirect to X OAuth page
      window.location.href = authorization_url;
    } catch (error: any) {
      console.error('OAuth error:', error);
      toast.error(error.response?.data?.detail || 'Failed to connect X account');
      setLoading(false);
    }
  };

  return (
    <button
      onClick={handleConnect}
      disabled={loading}
      className="flex items-center gap-3 bg-x-blue hover:bg-x-blue/90 disabled:bg-gray-400 text-white font-bold py-4 px-8 rounded-xl transition-all transform hover:scale-105 shadow-lg"
    >
      <Twitter className="w-6 h-6" />
      {loading ? 'Connecting...' : 'Connect X Account'}
    </button>
  );
}
