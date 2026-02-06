# PRISM Frontend

Next.js 14 frontend for PRISM - X Growth Automation Platform.

## Features

- **OAuth 2.0 Authentication** - Secure X account connection
- **Voice Analysis Dashboard** - View AI-analyzed writing profile
- **Viral Post Discovery** - Find high-engagement content in your niche
- **AI Remixing** - Transform posts using Claude, Mistral, or Grok
- **Smart Scheduling** - Queue posts for optimal posting times
- **Analytics** - Track performance of published tweets

## Tech Stack

- **Next.js 14** - App Router with React Server Components
- **TypeScript** - Strict type safety
- **Tailwind CSS** - Utility-first styling
- **Radix UI** - Accessible component primitives
- **Axios** - HTTP client with JWT interceptors
- **React Hot Toast** - Toast notifications
- **Date-fns** - Date manipulation
- **Lucide React** - Icon library

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on port 8003 (see `/prism-backend/SETUP.md`)

### Installation

```bash
cd frontend
npm install
```

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8003
```

For production:

```bash
NEXT_PUBLIC_API_URL=https://api.prism.yourdomain.com
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                      # Next.js App Router
│   ├── layout.tsx           # Root layout with Toaster
│   ├── page.tsx             # Landing page (OAuth flow)
│   ├── dashboard/
│   │   ├── layout.tsx       # Dashboard layout with Navbar
│   │   ├── page.tsx         # Main dashboard
│   │   └── discover/
│   │       └── page.tsx     # Viral post discovery
│   ├── schedule/
│   │   └── page.tsx         # Scheduled posts queue
│   └── analytics/
│       └── page.tsx         # Post analytics
├── components/
│   ├── AuthButton.tsx       # X OAuth connect button
│   ├── VoiceProfileCard.tsx # Voice analysis display
│   ├── ViralPostCard.tsx    # Viral post with metrics
│   ├── RemixModal.tsx       # AI remix modal (Radix Dialog)
│   ├── ScheduleControls.tsx # Date/time picker
│   ├── QueueList.tsx        # Scheduled posts list
│   └── Navbar.tsx           # Dashboard navigation
├── lib/
│   ├── api.ts               # Axios API client
│   ├── auth.ts              # JWT auth helpers
│   └── types.ts             # TypeScript interfaces
└── styles/
    └── globals.css          # Tailwind + custom styles
```

## Authentication Flow

1. **Landing Page** (`/`)
   - User clicks "Connect X Account"
   - Calls `GET /api/auth/connect`
   - Redirects to X OAuth authorization

2. **OAuth Callback** (`/api/auth/callback`)
   - X redirects back with `code` and `state`
   - Backend exchanges code for tokens
   - Returns JWT token

3. **Token Storage**
   - Frontend stores JWT in `localStorage`
   - All API calls include `Authorization: Bearer <token>` header
   - Auto-logout on 401 responses

4. **Dashboard** (`/dashboard`)
   - Protected route (redirects to `/` if not authenticated)
   - Loads user data and voice profile

## Key Components

### AuthButton

OAuth connection button. Calls `/api/auth/connect` and redirects to X.

### VoiceProfileCard

Displays AI-analyzed voice profile with niche, tone, topics, and best content types.

### ViralPostCard

Shows viral post with engagement metrics. "Remix with AI" button opens RemixModal.

### RemixModal

- AI model selector (Claude/Mistral/Grok)
- Original vs remixed content comparison
- Edit remixed content
- Schedule or post immediately

### ScheduleControls

Date/time picker with quick options (1 hour, 3 hours, 6 hours, tomorrow).

### QueueList

Displays scheduled posts with status badges (pending, posted, failed). Delete button for pending posts.

### Navbar

Sticky navigation with links to Dashboard, Discover, Schedule, and Analytics. Logout button.

## API Integration

All API calls go through `lib/api.ts` with automatic JWT authentication:

```typescript
import { api } from '@/lib/api';

// Get current user
const user = await api.getMe();

// Discover viral posts
const result = await api.discoverPosts({ niche: 'AI', min_likes: 1000 });

// Remix a post
const remixed = await api.remixPost({
  source_tweet_id: '123',
  source_text: 'Original tweet',
  model: 'claude'
});

// Schedule post
await api.schedulePost({
  post_id: 1,
  scheduled_time: new Date().toISOString()
});

// Get queue
const queue = await api.getQueue();

// Delete scheduled post
await api.deleteScheduledPost(1);

// Get analytics
const analytics = await api.getAnalytics();
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Connect repo to Vercel
3. Set environment variable:
   - `NEXT_PUBLIC_API_URL=https://api.prism.yourdomain.com`
4. Deploy

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build

ENV NODE_ENV=production
EXPOSE 3000

CMD ["npm", "start"]
```

```bash
docker build -t prism-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8003 prism-frontend
```

## CORS Configuration

Backend must allow frontend origin:

```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local dev
        "https://prism-*.vercel.app",      # Vercel preview
        "https://prism.yourdomain.com"     # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### API Connection Failed

- Check backend is running on port 8003
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`
- Check CORS configuration in backend

### OAuth Redirect Not Working

- Verify callback URL in X Developer Portal matches backend `.env`
- Check `X_OAUTH_CALLBACK_URL` in backend

### JWT Token Expired

- Token expires after 30 days (configurable in backend)
- User will be auto-logged out and redirected to landing page

### Build Errors

```bash
# Clear cache
rm -rf .next
npm run build
```

## Development Tips

### Hot Reload

Next.js automatically reloads on file changes. No need to restart dev server.

### Type Safety

All API responses are typed. Use `types.ts` for consistency:

```typescript
import type { User, ViralPost, ScheduledPost } from '@/lib/types';
```

### Styling

Use Tailwind utility classes. Custom styles in `globals.css`:

```tsx
<button className="btn-primary">Click Me</button>
<div className="card">Content</div>
```

### Toast Notifications

```typescript
import toast from 'react-hot-toast';

toast.success('Success message');
toast.error('Error message');
toast.loading('Loading...');
```

---

Built with ❤️ for X growth automation
