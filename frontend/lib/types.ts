/**
 * TypeScript type definitions for PRISM
 */

export interface User {
  id: number;
  username: string;
  x_username: string;
  x_user_id: string;
  detected_niche: string | null;
  voice_profile: VoiceProfile | null;
  analysis_complete: boolean;
  created_at: string;
  updated_at: string;
}

export interface VoiceProfile {
  niche: string[];
  tone: string;
  topics: string[];
  best_content: string[];
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    x_username: string;
  };
}

export interface ViralPost {
  id: string;
  text: string;
  author_id: string;
  author_username: string;
  created_at: string;
  engagement_score: number;
  metrics: {
    likes: number;
    retweets: number;
    replies: number;
    views: number;
  };
}

export interface Post {
  id: number;
  user_id: number;
  content: string;
  source_tweet_id: string | null;
  ai_model: string | null;
  status: 'draft' | 'scheduled' | 'posted';
  created_at: string;
}

export interface ScheduledPost {
  id: number;
  post_id: number;
  content: string;
  scheduled_for: string;
  status: 'pending' | 'posted' | 'failed';
  posted_at: string | null;
  x_post_id: string | null;
  error_message: string | null;
}

export interface RemixRequest {
  source_tweet_id: string;
  source_text: string;
  model: 'claude' | 'mistral' | 'grok';
}

export interface RemixResponse {
  post_id: number;
  original: string;
  remixed: string;
  model: string;
  status: string;
}

export interface ScheduleRequest {
  post_id: number;
  scheduled_time: string; // ISO 8601 datetime
}

export interface DiscoverParams {
  niche?: string;
  min_likes?: number;
  max_results?: number;
}

export interface AnalyticsPost {
  scheduled_post_id: number;
  content: string;
  posted_at: string;
  x_post_id: string;
  metrics: {
    id: string;
    created_at: string;
    likes: number;
    retweets: number;
    replies: number;
    views: number;
    engagement_score: number;
  };
}

export interface Subscription {
  plan_type: 'free' | 'pro';
  status: string | null;
  is_pro: boolean;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
  canceled_at: string | null;
}

export interface Payment {
  id: number;
  amount: number;
  currency: string;
  status: string;
  description: string;
  paid_at: string | null;
  failure_reason: string | null;
}

export interface CheckoutSession {
  session_id: string;
  url: string;
}

export interface PortalSession {
  url: string;
}
