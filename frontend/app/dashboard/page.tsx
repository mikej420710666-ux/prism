'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, Clock, CheckCircle } from 'lucide-react';
import VoiceProfileCard from '@/components/VoiceProfileCard';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import type { User, ScheduledPost } from '@/lib/types';

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null);
  const [voiceStatus, setVoiceStatus] = useState<'pending' | 'complete'>('pending');
  const [queueCount, setQueueCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      // Load user data
      const userData = await api.getMe();
      setUser(userData);

      // Load voice profile
      const voiceData = await api.getVoiceProfile();
      setVoiceStatus(voiceData.status as 'pending' | 'complete');

      // Load queue count
      const queueData = await api.getQueue();
      const pendingCount = queueData.posts.filter((p) => p.status === 'pending').length;
      setQueueCount(pendingCount);
    } catch (error: any) {
      console.error('Dashboard load error:', error);
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-prism-purple"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Welcome Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, @{user?.x_username}! 👋
        </h1>
        <p className="text-gray-600 mt-2">
          Here's what's happening with your X growth automation.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Voice Analysis</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {voiceStatus === 'complete' ? 'Complete' : 'Analyzing...'}
              </p>
            </div>
            {voiceStatus === 'complete' ? (
              <CheckCircle className="w-10 h-10 text-green-500" />
            ) : (
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-prism-purple"></div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Scheduled Posts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{queueCount}</p>
            </div>
            <Clock className="w-10 h-10 text-prism-blue" />
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Niche</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {user?.detected_niche || 'Analyzing...'}
              </p>
            </div>
            <TrendingUp className="w-10 h-10 text-prism-pink" />
          </div>
        </div>
      </div>

      {/* Voice Profile Card */}
      <VoiceProfileCard
        status={voiceStatus}
        voiceProfile={user?.voice_profile}
        niche={user?.detected_niche}
      />

      {/* Quick Actions */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <a
            href="/dashboard/discover"
            className="block p-6 bg-gradient-to-r from-prism-purple to-prism-pink text-white rounded-xl hover:opacity-90 transition-opacity"
          >
            <h3 className="font-bold text-lg mb-2">Discover Viral Posts</h3>
            <p className="text-white/90 text-sm">
              Find high-engagement content in your niche
            </p>
          </a>

          <a
            href="/schedule"
            className="block p-6 bg-gradient-to-r from-prism-blue to-prism-purple text-white rounded-xl hover:opacity-90 transition-opacity"
          >
            <h3 className="font-bold text-lg mb-2">View Schedule</h3>
            <p className="text-white/90 text-sm">
              Manage your scheduled posts queue
            </p>
          </a>
        </div>
      </div>
    </div>
  );
}
