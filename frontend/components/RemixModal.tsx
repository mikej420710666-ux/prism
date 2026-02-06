'use client';

import { useState } from 'react';
import * as Dialog from '@radix-ui/react-dialog';
import { X, Sparkles, Clock, Send, Loader2 } from 'lucide-react';
import { api } from '@/lib/api';
import type { ViralPost } from '@/lib/types';
import toast from 'react-hot-toast';
import ScheduleControls from './ScheduleControls';

interface RemixModalProps {
  isOpen: boolean;
  onClose: () => void;
  post: ViralPost | null;
  onScheduled?: () => void;
}

export default function RemixModal({ isOpen, onClose, post, onScheduled }: RemixModalProps) {
  const [model, setModel] = useState<'claude' | 'mistral' | 'grok'>('claude');
  const [remixing, setRemixing] = useState(false);
  const [remixedContent, setRemixedContent] = useState('');
  const [postId, setPostId] = useState<number | null>(null);
  const [showSchedule, setShowSchedule] = useState(false);
  const [scheduling, setScheduling] = useState(false);

  if (!post) return null;

  const handleRemix = async () => {
    setRemixing(true);
    try {
      const response = await api.remixPost({
        source_tweet_id: post.id,
        source_text: post.text,
        model,
      });

      setRemixedContent(response.remixed);
      setPostId(response.post_id);
      toast.success('Remixed successfully!');
    } catch (error: any) {
      console.error('Remix error:', error);
      toast.error(error.response?.data?.detail || 'Failed to remix post');
    } finally {
      setRemixing(false);
    }
  };

  const handleSchedule = async (scheduledTime: Date) => {
    if (!postId) return;

    setScheduling(true);
    try {
      await api.schedulePost({
        post_id: postId,
        scheduled_time: scheduledTime.toISOString(),
      });

      toast.success('Post scheduled successfully!');
      onScheduled?.();
      onClose();
      resetModal();
    } catch (error: any) {
      console.error('Schedule error:', error);
      toast.error(error.response?.data?.detail || 'Failed to schedule post');
    } finally {
      setScheduling(false);
    }
  };

  const resetModal = () => {
    setRemixedContent('');
    setPostId(null);
    setShowSchedule(false);
    setModel('claude');
  };

  const handleClose = () => {
    onClose();
    setTimeout(resetModal, 300);
  };

  return (
    <Dialog.Root open={isOpen} onOpenChange={handleClose}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40" />
        <Dialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-2xl w-[90vw] max-w-3xl max-h-[85vh] overflow-y-auto z-50 p-8">
          <Dialog.Title className="text-2xl font-bold mb-4 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-prism-purple" />
            AI Remix
          </Dialog.Title>

          <Dialog.Close asChild>
            <button className="absolute top-4 right-4 text-gray-500 hover:text-gray-700">
              <X className="w-6 h-6" />
            </button>
          </Dialog.Close>

          <div className="space-y-6">
            {/* Original Post */}
            <div>
              <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Original Post
              </h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="text-gray-800">{post.text}</p>
                <p className="text-xs text-gray-500 mt-2">@{post.author_username}</p>
              </div>
            </div>

            {/* AI Model Selection */}
            {!remixedContent && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                  AI Model
                </h3>
                <div className="flex gap-2">
                  {(['claude', 'mistral', 'grok'] as const).map((m) => (
                    <button
                      key={m}
                      onClick={() => setModel(m)}
                      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                        model === m
                          ? 'bg-prism-purple text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {m.charAt(0).toUpperCase() + m.slice(1)}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Remixed Content */}
            {remixedContent && (
              <div>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                  Remixed Version
                </h3>
                <textarea
                  value={remixedContent}
                  onChange={(e) => setRemixedContent(e.target.value)}
                  className="w-full h-32 px-4 py-3 border border-prism-purple rounded-lg focus:ring-2 focus:ring-prism-purple focus:border-transparent outline-none resize-none"
                  maxLength={280}
                />
                <p className="text-sm text-gray-500 mt-1">
                  {remixedContent.length}/280 characters
                </p>
              </div>
            )}

            {/* Schedule Controls */}
            {showSchedule && remixedContent && (
              <ScheduleControls onSchedule={handleSchedule} scheduling={scheduling} />
            )}

            {/* Actions */}
            <div className="flex gap-3">
              {!remixedContent ? (
                <button
                  onClick={handleRemix}
                  disabled={remixing}
                  className="flex-1 flex items-center justify-center gap-2 bg-prism-purple hover:bg-prism-purple/90 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition-colors"
                >
                  {remixing ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Remixing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5" />
                      Remix with {model}
                    </>
                  )}
                </button>
              ) : (
                <>
                  {!showSchedule ? (
                    <>
                      <button
                        onClick={() => setShowSchedule(true)}
                        className="flex-1 flex items-center justify-center gap-2 bg-prism-blue hover:bg-prism-blue/90 text-white font-semibold py-3 rounded-lg transition-colors"
                      >
                        <Clock className="w-5 h-5" />
                        Schedule
                      </button>
                      <button
                        onClick={() => handleSchedule(new Date())}
                        disabled={scheduling}
                        className="flex-1 flex items-center justify-center gap-2 bg-prism-pink hover:bg-prism-pink/90 disabled:bg-gray-400 text-white font-semibold py-3 rounded-lg transition-colors"
                      >
                        {scheduling ? (
                          <Loader2 className="w-5 h-5 animate-spin" />
                        ) : (
                          <>
                            <Send className="w-5 h-5" />
                            Post Now
                          </>
                        )}
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => setShowSchedule(false)}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-3 rounded-lg transition-colors"
                    >
                      Cancel
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
