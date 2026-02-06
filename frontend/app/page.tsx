'use client';

export const dynamic = 'force-dynamic';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Sparkles, Twitter, TrendingUp, Clock, BarChart3 } from 'lucide-react';
import AuthButton from '@/components/AuthButton';
import { auth } from '@/lib/auth';
import toast from 'react-hot-toast';

export default function LandingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Handle OAuth callback from URL
    const params = new URLSearchParams(window.location.search);
    const token = params.get('access_token');
    
    if (token) {
      auth.setToken(token);
      toast.success('Connected successfully!');
      router.push('/dashboard');
      return;
    }

    // Redirect if already authenticated
    if (auth.isAuthenticated()) {
      router.push('/dashboard');
      return;
    }

    setLoading(false);
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-prism-purple"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Hero Section */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-prism-purple to-prism-pink rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-lg">
              P
            </div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-prism-purple to-prism-pink bg-clip-text text-transparent">
              PRISM
            </h1>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Automate Your X Growth
          </h2>
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto">
            Discover viral posts, remix them in your voice using AI, and schedule them automatically.
            Grow your X presence effortlessly.
          </p>

          <AuthButton />
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-prism-purple/10 rounded-xl flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-prism-purple" />
            </div>
            <h3 className="text-xl font-bold mb-3">Discover Viral Posts</h3>
            <p className="text-gray-600">
              Find high-engagement posts in your niche automatically. Never run out of content ideas.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-prism-pink/10 rounded-xl flex items-center justify-center mb-4">
              <Sparkles className="w-6 h-6 text-prism-pink" />
            </div>
            <h3 className="text-xl font-bold mb-3">AI Remixing</h3>
            <p className="text-gray-600">
              Use Claude, Mistral, or Grok to remix posts in your unique voice. Authentic content, every time.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow">
            <div className="w-12 h-12 bg-prism-blue/10 rounded-xl flex items-center justify-center mb-4">
              <Clock className="w-6 h-6 text-prism-blue" />
            </div>
            <h3 className="text-xl font-bold mb-3">Smart Scheduling</h3>
            <p className="text-gray-600">
              Schedule posts at optimal times. Set it and forget it with our auto-pilot mode.
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="mt-24 text-center">
          <h3 className="text-3xl font-bold mb-12">How It Works</h3>
          <div className="grid md:grid-cols-4 gap-6">
            {[
              { step: 1, title: 'Connect X', desc: 'Link your X account with OAuth 2.0' },
              { step: 2, title: 'Voice Analysis', desc: 'AI analyzes your writing style' },
              { step: 3, title: 'Discover & Remix', desc: 'Find viral posts and remix them' },
              { step: 4, title: 'Schedule & Grow', desc: 'Auto-post and track performance' },
            ].map((item) => (
              <div key={item.step} className="relative">
                <div className="bg-white rounded-xl p-6 shadow-md">
                  <div className="w-10 h-10 bg-gradient-to-br from-prism-purple to-prism-pink rounded-full flex items-center justify-center text-white font-bold mb-4 mx-auto">
                    {item.step}
                  </div>
                  <h4 className="font-bold mb-2">{item.title}</h4>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-24 text-center">
          <h3 className="text-3xl font-bold mb-6">Ready to grow your X presence?</h3>
          <AuthButton />
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-20 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center text-gray-600">
          <p>Built with Claude, Mistral, and Grok AI</p>
        </div>
      </footer>
    </div>
  );
}
