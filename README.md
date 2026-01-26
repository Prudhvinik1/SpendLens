# SpendLens Frontend

A premium, dark-themed financial dashboard for analyzing spending patterns from bank statements.

## Features

- 🎨 **Dark Premium Design** - Modern dashboard-style UI with orange accent colors
- 📊 **Interactive Charts** - Category breakdown with donut charts
- 💡 **AI-Powered Insights** - Actionable spending insights and recommendations
- 📱 **Responsive Design** - Works seamlessly on desktop, tablet, and mobile
- ⚡ **Fast Processing** - Real-time analysis status updates

## Tech Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality component library
- **Recharts** - Beautiful charting library
- **Framer Motion** - Smooth animations

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
SpendLens/
├── app/
│   ├── page.tsx                 # Landing page
│   ├── analyze/
│   │   ├── processing/           # Processing status page
│   │   └── results/             # Results dashboard
│   ├── layout.tsx               # Root layout
│   └── globals.css              # Global styles and CSS variables
├── components/
│   ├── ui/                      # shadcn/ui components
│   ├── layout/                  # Layout components (header, footer)
│   ├── landing/                 # Landing page components
│   ├── processing/              # Processing page components
│   └── dashboard/               # Dashboard components
├── lib/
│   └── utils.ts                 # Utility functions
└── styles/
    └── animations.css           # Custom animations
```

## Design System

### Color Palette

- **Backgrounds**: Dark shades (#0a0a0a, #111111, #1a1a1a)
- **Accent**: Orange (#f97316) for CTAs and highlights
- **Success**: Teal (#14b8a6) for positive indicators
- **Warning**: Orange for alerts
- **Error**: Red (#ef4444) for negative indicators

### Typography

- **Headings**: Inter (sans-serif)
- **Numbers**: Tabular nums for alignment
- **Code/Dates**: JetBrains Mono (monospace)

## Pages

1. **Landing Page** (`/`) - File upload interface
2. **Processing** (`/analyze/processing`) - Analysis status
3. **Results** (`/analyze/results`) - Dashboard with insights

## Development

### Adding New Components

Components follow the shadcn/ui pattern. Use the `cn()` utility for class merging.

### Styling

- Use CSS variables from `globals.css` for colors
- Follow the design system color palette
- Use Tailwind utilities for spacing and layout

## Deployment

### Deploy to Vercel

The easiest way to deploy SpendLens is using [Vercel](https://vercel.com):

#### Option 1: Deploy via Vercel CLI

```bash
# Install Vercel CLI globally
npm i -g vercel

# Deploy
vercel
```

#### Option 2: Deploy via GitHub Integration

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and sign in
3. Click "Add New Project"
4. Import your GitHub repository
5. Vercel will auto-detect Next.js and configure everything
6. Click "Deploy"

#### Option 3: Deploy via Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your Git repository
3. Vercel will automatically detect Next.js
4. Configure environment variables if needed
5. Click "Deploy"

### Environment Variables

If you need to configure environment variables (e.g., API endpoints), add them in the Vercel dashboard:

1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add your variables
4. Redeploy

### Build Settings

Vercel will automatically:
- Detect Next.js framework
- Run `npm install` and `npm run build`
- Deploy your application

The `vercel.json` file is optional but included for any custom configurations.

## License

MIT

