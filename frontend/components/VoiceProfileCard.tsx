'use client';

import { Sparkles, Loader2 } from 'lucide-react';
import type { VoiceProfile } from '@/lib/types';

interface VoiceProfileCardProps {
  status: 'pending' | 'complete';
  voiceProfile?: VoiceProfile | null;
  niche?: string | null;
}

export default function VoiceProfileCard({ status, voiceProfile, niche }: VoiceProfileCardProps) {
  if (status === 'pending') {
    return (
      <div className="card">
        <div className="flex items-center gap-3 mb-4">
          <Loader2 className="w-6 h-6 text-prism-purple animate-spin" />
          <h2 className="text-xl font-bold">Analyzing Your Voice...</h2>
        </div>
        <p className="text-gray-600">
          We're analyzing your recent tweets to understand your writing style, tone, and niche.
          This usually takes 30-60 seconds.
        </p>
      </div>
    );
  }

  if (!voiceProfile) {
    return null;
  }

  return (
    <div className="card">
      <div className="flex items-center gap-3 mb-4">
        <Sparkles className="w-6 h-6 text-prism-purple" />
        <h2 className="text-xl font-bold">Your Voice Profile</h2>
      </div>

      <div className="space-y-4">
        {/* Niche */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Niche
          </h3>
          <div className="flex flex-wrap gap-2">
            {voiceProfile.niche.map((n, i) => (
              <span
                key={i}
                className="bg-prism-purple/10 text-prism-purple px-3 py-1 rounded-full text-sm font-medium"
              >
                {n}
              </span>
            ))}
          </div>
        </div>

        {/* Tone */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Tone
          </h3>
          <p className="text-gray-800 font-medium">{voiceProfile.tone}</p>
        </div>

        {/* Topics */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Common Topics
          </h3>
          <div className="flex flex-wrap gap-2">
            {voiceProfile.topics.map((topic, i) => (
              <span
                key={i}
                className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm"
              >
                {topic}
              </span>
            ))}
          </div>
        </div>

        {/* Best Content */}
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Best Content Types
          </h3>
          <div className="flex flex-wrap gap-2">
            {voiceProfile.best_content.map((content, i) => (
              <span
                key={i}
                className="bg-prism-pink/10 text-prism-pink px-3 py-1 rounded-full text-sm font-medium"
              >
                {content}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
