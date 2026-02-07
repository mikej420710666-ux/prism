/**
 * API Client for PRISM Backend
 * Axios wrapper with JWT authentication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { auth } from './auth';
import type {
  User,
  AuthResponse,
  ViralPost,
  RemixRequest,
  RemixResponse,
  ScheduleRequest,
  ScheduledPost,
  DiscoverParams,
  AnalyticsPost,
  Subscription,
  Payment,
  CheckoutSession,
  PortalSession,
} from './types';

// Use empty baseURL for Vercel proxy to work (rewrites /api/* to backend)
// For local dev, set NEXT_PUBLIC_API_URL=http://localhost:8003
const API_URL = process.env.NEXT_PUBLIC_API_URL || '';

/**
 * Axios instance with JWT authentication
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add JWT token to all requests
apiClient.interceptors.request.use(
  (config) => {
    const token = auth.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle 401 errors (unauthorized) by logging out
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      auth.logout();
    }
    return Promise.reject(error);
  }
);

/**
 * API methods
 */
export const api = {
  // ============================================================================
  // AUTHENTICATION
  // ============================================================================

  /**
   * Start X OAuth flow
   */
  async startOAuth(): Promise<{ authorization_url: string; state: string }> {
    const { data } = await apiClient.get('/api/auth/connect');
    return data;
  },

  /**
   * Get current authenticated user
   */
  async getMe(): Promise<User> {
    const { data } = await apiClient.get('/api/auth/me');
    return data;
  },

  // ============================================================================
  // VOICE ANALYSIS
  // ============================================================================

  /**
   * Trigger voice analysis for current user
   */
  async triggerVoiceAnalysis(): Promise<{ task_id: string; status: string; message: string }> {
    const { data } = await apiClient.post('/api/user/voice/analyze');
    return data;
  },

  /**
   * Get user's voice profile
   */
  async getVoiceProfile(): Promise<{
    status: string;
    niche?: string;
    voice_profile?: any;
    analysis_complete?: boolean;
    message?: string;
  }> {
    const { data } = await apiClient.get('/api/user/voice');
    return data;
  },

  // ============================================================================
  // DISCOVERY
  // ============================================================================

  /**
   * Discover viral posts in user's niche
   */
  async discoverPosts(params: DiscoverParams = {}): Promise<{
    niche: string;
    count: number;
    posts: ViralPost[];
  }> {
    const { data } = await apiClient.get('/api/discover', { params });
    return data;
  },

  // ============================================================================
  // REMIX
  // ============================================================================

  /**
   * Remix a viral post using AI
   */
  async remixPost(request: RemixRequest): Promise<RemixResponse> {
    const { data } = await apiClient.post('/api/remix', request);
    return data;
  },

  // ============================================================================
  // SCHEDULING
  // ============================================================================

  /**
   * Schedule a post for future posting
   */
  async schedulePost(request: ScheduleRequest): Promise<{
    scheduled_post_id: number;
    post_id: number;
    content: string;
    scheduled_for: string;
    status: string;
  }> {
    const { data } = await apiClient.post('/api/schedule', request);
    return data;
  },

  /**
   * Get scheduled posts queue
   */
  async getQueue(): Promise<{
    count: number;
    posts: ScheduledPost[];
  }> {
    const { data } = await apiClient.get('/api/schedule/queue');
    return data;
  },

  /**
   * Delete a scheduled post
   */
  async deleteScheduledPost(scheduledPostId: number): Promise<{
    success: boolean;
    message: string;
  }> {
    const { data } = await apiClient.delete(`/api/schedule/${scheduledPostId}`);
    return data;
  },

  // ============================================================================
  // ANALYTICS
  // ============================================================================

  /**
   * Get analytics for published posts
   */
  async getAnalytics(): Promise<{
    count: number;
    posts: AnalyticsPost[];
  }> {
    const { data } = await apiClient.get('/api/analytics/posts');
    return data;
  },

  // ============================================================================
  // BILLING & SUBSCRIPTIONS
  // ============================================================================

  /**
   * Create Stripe checkout session
   */
  async createCheckout(): Promise<CheckoutSession> {
    const { data } = await apiClient.post('/api/billing/create-checkout');
    return data;
  },

  /**
   * Create Stripe customer portal session
   */
  async createPortal(): Promise<PortalSession> {
    const { data } = await apiClient.post('/api/billing/create-portal');
    return data;
  },

  /**
   * Get subscription status
   */
  async getSubscription(): Promise<Subscription> {
    const { data } = await apiClient.get('/api/billing/subscription');
    return data;
  },

  /**
   * Cancel subscription
   */
  async cancelSubscription(): Promise<{ success: boolean; message: string; period_end: string }> {
    const { data } = await apiClient.post('/api/billing/cancel');
    return data;
  },

  /**
   * Reactivate subscription
   */
  async reactivateSubscription(): Promise<{ success: boolean; message: string }> {
    const { data } = await apiClient.post('/api/billing/reactivate');
    return data;
  },

  /**
   * Get payment history
   */
  async getPaymentHistory(): Promise<{ count: number; payments: Payment[] }> {
    const { data } = await apiClient.get('/api/billing/history');
    return data;
  },
};

export default api;
