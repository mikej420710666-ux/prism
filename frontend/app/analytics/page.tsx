'use client';

import { useState, useEffect } from 'react';
import { Loader2, Heart, Repeat2, MessageCircle, Eye, ExternalLink } from 'lucide-react';
import { format } from 'date-fns';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import type { AnalyticsPost } from '@/lib/types';

export default function AnalyticsPage() {
  const [posts, setPosts] = useState<AnalyticsPost[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      const result = await api.getAnalytics();
      setPosts(result.posts);
    } catch (error: any) {
      console.error('Analytics load error:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="w-12 h-12 text-prism-purple animate-spin" />
      </div>
    );
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  // Calculate totals
  const totals = posts.reduce(
    (acc, post) => ({
      likes: acc.likes + post.metrics.likes,
      retweets: acc.retweets + post.metrics.retweets,
      replies: acc.replies + post.metrics.replies,
      views: acc.views + post.metrics.views,
      engagement: acc.engagement + post.metrics.engagement_score,
    }),
    { likes: 0, retweets: 0, replies: 0, views: 0, engagement: 0 }
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600 mt-2">
          Track performance of your published posts.
        </p>
      </div>

      {/* Total Stats */}
      {posts.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="card">
            <p className="text-sm font-medium text-gray-500">Total Posts</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{posts.length}</p>
          </div>
          <div className="card">
            <div className="flex items-center gap-2 mb-1">
              <Heart className="w-4 h-4 text-red-500" />
              <p className="text-sm font-medium text-gray-500">Likes</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(totals.likes)}</p>
          </div>
          <div className="card">
            <div className="flex items-center gap-2 mb-1">
              <Repeat2 className="w-4 h-4 text-green-500" />
              <p className="text-sm font-medium text-gray-500">Retweets</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(totals.retweets)}</p>
          </div>
          <div className="card">
            <div className="flex items-center gap-2 mb-1">
              <MessageCircle className="w-4 h-4 text-blue-500" />
              <p className="text-sm font-medium text-gray-500">Replies</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(totals.replies)}</p>
          </div>
          <div className="card">
            <div className="flex items-center gap-2 mb-1">
              <Eye className="w-4 h-4 text-purple-500" />
              <p className="text-sm font-medium text-gray-500">Views</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">{formatNumber(totals.views)}</p>
          </div>
        </div>
      )}

      {/* Posts Table */}
      {posts.length > 0 ? (
        <div className="card overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Content</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Posted</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">
                  <Heart className="w-4 h-4 inline" />
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">
                  <Repeat2 className="w-4 h-4 inline" />
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">
                  <MessageCircle className="w-4 h-4 inline" />
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">
                  <Eye className="w-4 h-4 inline" />
                </th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Link</th>
              </tr>
            </thead>
            <tbody>
              {posts.map((post) => (
                <tr key={post.scheduled_post_id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 max-w-md">
                    <p className="text-gray-800 line-clamp-2">{post.content}</p>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-600 whitespace-nowrap">
                    {format(new Date(post.posted_at), 'MMM d, HH:mm')}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {formatNumber(post.metrics.likes)}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {formatNumber(post.metrics.retweets)}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {formatNumber(post.metrics.replies)}
                  </td>
                  <td className="py-3 px-4 text-center text-gray-700">
                    {formatNumber(post.metrics.views)}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <a
                      href={`https://twitter.com/i/web/status/${post.x_post_id}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-x-blue hover:underline inline-flex items-center gap-1"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">No published posts yet.</p>
          <a
            href="/dashboard/discover"
            className="inline-block bg-prism-purple hover:bg-prism-purple/90 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
          >
            Start Creating Content
          </a>
        </div>
      )}
    </div>
  );
}
