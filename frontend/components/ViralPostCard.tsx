'use client';

import { Heart, Repeat2, MessageCircle, Eye, Sparkles } from 'lucide-react';
import type { ViralPost } from '@/lib/types';

interface ViralPostCardProps {
  post: ViralPost;
  onRemix: (post: ViralPost) => void;
}

export default function ViralPostCard({ post, onRemix }: ViralPostCardProps) {
  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="card hover:shadow-lg transition-shadow">
      {/* Author */}
      <div className="flex items-center gap-2 mb-3">
        <div className="w-10 h-10 bg-gradient-to-br from-prism-purple to-prism-pink rounded-full flex items-center justify-center text-white font-bold">
          {post.author_username[0].toUpperCase()}
        </div>
        <div>
          <p className="font-semibold text-gray-900">@{post.author_username}</p>
          <p className="text-xs text-gray-500">
            {new Date(post.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {/* Tweet Text */}
      <p className="text-gray-800 mb-4 leading-relaxed">{post.text}</p>

      {/* Engagement Metrics */}
      <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
        <div className="flex items-center gap-1">
          <Heart className="w-4 h-4" />
          <span>{formatNumber(post.metrics.likes)}</span>
        </div>
        <div className="flex items-center gap-1">
          <Repeat2 className="w-4 h-4" />
          <span>{formatNumber(post.metrics.retweets)}</span>
        </div>
        <div className="flex items-center gap-1">
          <MessageCircle className="w-4 h-4" />
          <span>{formatNumber(post.metrics.replies)}</span>
        </div>
        {post.metrics.views > 0 && (
          <div className="flex items-center gap-1">
            <Eye className="w-4 h-4" />
            <span>{formatNumber(post.metrics.views)}</span>
          </div>
        )}
      </div>

      {/* Remix Button */}
      <button
        onClick={() => onRemix(post)}
        className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-prism-purple to-prism-pink hover:opacity-90 text-white font-semibold py-3 rounded-lg transition-all"
      >
        <Sparkles className="w-5 h-5" />
        Remix with AI
      </button>
    </div>
  );
}
