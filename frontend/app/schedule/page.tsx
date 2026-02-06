'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import QueueList from '@/components/QueueList';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import type { ScheduledPost } from '@/lib/types';

export default function SchedulePage() {
  const [posts, setPosts] = useState<ScheduledPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    setLoading(true);
    try {
      const result = await api.getQueue();
      setPosts(result.posts);
    } catch (error: any) {
      console.error('Queue load error:', error);
      toast.error('Failed to load queue');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this scheduled post?')) {
      return;
    }

    try {
      await api.deleteScheduledPost(id);
      toast.success('Scheduled post deleted');
      // Remove from local state
      setPosts((prev) => prev.filter((p) => p.id !== id));
    } catch (error: any) {
      console.error('Delete error:', error);
      toast.error(error.response?.data?.detail || 'Failed to delete post');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-12 h-12 text-prism-purple animate-spin" />
      </div>
    );
  }

  // Separate posts by status
  const pending = posts.filter((p) => p.status === 'pending');
  const posted = posts.filter((p) => p.status === 'posted');
  const failed = posts.filter((p) => p.status === 'failed');

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Scheduled Posts</h1>
        <p className="text-gray-600 mt-2">
          Manage your queue and track posted tweets.
        </p>
      </div>

      {/* Stats */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Pending</p>
          <p className="text-3xl font-bold text-yellow-600 mt-2">{pending.length}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Posted</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{posted.length}</p>
        </div>
        <div className="card">
          <p className="text-sm font-medium text-gray-500">Failed</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{failed.length}</p>
        </div>
      </div>

      {/* Pending Posts */}
      {pending.length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-4">Pending Posts</h2>
          <QueueList posts={pending} onDelete={handleDelete} />
        </div>
      )}

      {/* Posted */}
      {posted.length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-4">Posted</h2>
          <QueueList posts={posted} onDelete={handleDelete} />
        </div>
      )}

      {/* Failed */}
      {failed.length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-4 text-red-600">Failed</h2>
          <QueueList posts={failed} onDelete={handleDelete} />
        </div>
      )}

      {/* Empty State */}
      {posts.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">No scheduled posts yet.</p>
          <a
            href="/dashboard/discover"
            className="inline-block bg-prism-purple hover:bg-prism-purple/90 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            Discover & Remix Posts
          </a>
        </div>
      )}
    </div>
  );
}
