'use client';

import { useState, useEffect } from 'react';
import { Search, Loader2 } from 'lucide-react';
import ViralPostCard from '@/components/ViralPostCard';
import RemixModal from '@/components/RemixModal';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import type { ViralPost } from '@/lib/types';

export default function DiscoverPage() {
  const [niche, setNiche] = useState('');
  const [minLikes, setMinLikes] = useState(1000);
  const [posts, setPosts] = useState<ViralPost[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPost, setSelectedPost] = useState<ViralPost | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    // Auto-discover on mount (uses user's detected niche)
    handleDiscover();
  }, []);

  const handleDiscover = async () => {
    setLoading(true);
    try {
      const result = await api.discoverPosts({
        niche: niche || undefined,
        min_likes: minLikes,
        max_results: 50,
      });

      setPosts(result.posts);

      if (result.posts.length === 0) {
        toast.error('No viral posts found. Try adjusting your filters.');
      } else {
        toast.success(`Found ${result.count} viral posts!`);
      }
    } catch (error: any) {
      console.error('Discovery error:', error);
      toast.error(error.response?.data?.detail || 'Failed to discover posts');
    } finally {
      setLoading(false);
    }
  };

  const handleRemix = (post: ViralPost) => {
    setSelectedPost(post);
    setIsModalOpen(true);
  };

  const handleScheduled = () => {
    toast.success('Post scheduled! Check your queue.');
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Discover Viral Posts</h1>
        <p className="text-gray-600 mt-2">
          Find high-engagement content in your niche and remix it in your voice.
        </p>
      </div>

      {/* Search Controls */}
      <div className="card">
        <div className="grid md:grid-cols-3 gap-4">
          {/* Niche Input */}
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Niche / Topic (leave empty to use your detected niche)
            </label>
            <input
              type="text"
              value={niche}
              onChange={(e) => setNiche(e.target.value)}
              placeholder="e.g., AI tools, fitness, crypto"
              className="input"
            />
          </div>

          {/* Min Engagement */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Likes
            </label>
            <input
              type="number"
              value={minLikes}
              onChange={(e) => setMinLikes(parseInt(e.target.value))}
              min={100}
              step={100}
              className="input"
            />
          </div>
        </div>

        {/* Search Button */}
        <button
          onClick={handleDiscover}
          disabled={loading}
          className="mt-4 w-full md:w-auto flex items-center justify-center gap-2 btn-primary disabled:bg-gray-400"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Discovering...
            </>
          ) : (
            <>
              <Search className="w-5 h-5" />
              Discover Posts
            </>
          )}
        </button>
      </div>

      {/* Posts Grid */}
      {posts.length > 0 && (
        <div>
          <h2 className="text-xl font-bold mb-4">
            Found {posts.length} viral {posts.length === 1 ? 'post' : 'posts'}
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post) => (
              <ViralPostCard key={post.id} post={post} onRemix={handleRemix} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && posts.length === 0 && (
        <div className="card text-center py-12">
          <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">
            No posts yet. Click "Discover Posts" to find viral content.
          </p>
        </div>
      )}

      {/* Remix Modal */}
      <RemixModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        post={selectedPost}
        onScheduled={handleScheduled}
      />
    </div>
  );
}
