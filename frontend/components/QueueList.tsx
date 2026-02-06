'use client';

import { Trash2, Clock, CheckCircle, XCircle, ExternalLink } from 'lucide-react';
import { format } from 'date-fns';
import type { ScheduledPost } from '@/lib/types';

interface QueueListProps {
  posts: ScheduledPost[];
  onDelete: (id: number) => void;
}

export default function QueueList({ posts, onDelete }: QueueListProps) {
  if (posts.length === 0) {
    return (
      <div className="card text-center py-12">
        <Clock className="w-12 h-12 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">No scheduled posts yet</p>
      </div>
    );
  }

  const getStatusBadge = (status: ScheduledPost['status']) => {
    switch (status) {
      case 'pending':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-medium">
            <Clock className="w-4 h-4" />
            Pending
          </span>
        );
      case 'posted':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium">
            <CheckCircle className="w-4 h-4" />
            Posted
          </span>
        );
      case 'failed':
        return (
          <span className="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-medium">
            <XCircle className="w-4 h-4" />
            Failed
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <div key={post.id} className="card hover:shadow-lg transition-shadow">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              {/* Content */}
              <p className="text-gray-800 mb-3 leading-relaxed">{post.content}</p>

              {/* Metadata */}
              <div className="flex flex-wrap items-center gap-3 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>
                    {post.status === 'posted' && post.posted_at
                      ? `Posted ${format(new Date(post.posted_at), 'PPp')}`
                      : `Scheduled for ${format(new Date(post.scheduled_for), 'PPp')}`}
                  </span>
                </div>

                {getStatusBadge(post.status)}

                {post.x_post_id && (
                  <a
                    href={`https://twitter.com/i/web/status/${post.x_post_id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-x-blue hover:underline"
                  >
                    View on X
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>

              {/* Error Message */}
              {post.error_message && (
                <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                  {post.error_message}
                </div>
              )}
            </div>

            {/* Delete Button */}
            {post.status !== 'posted' && (
              <button
                onClick={() => onDelete(post.id)}
                className="text-gray-400 hover:text-red-600 transition-colors p-2"
                title="Delete scheduled post"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
