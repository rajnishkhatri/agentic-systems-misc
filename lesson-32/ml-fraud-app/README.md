# ML Fraud Detection: First Principles Guide

An interactive React application that explores fraud detection through a first-principles framework. This comprehensive guide includes both ML fraud detection and Address Manipulation fraud, taking you from surface-level knowledge to irreducible axioms using recursive questioning methodology.

## Guides Available

### 1. ML Fraud Detection First Principles
- **6-Phase Learning Journey**: Baseline → Assumptions → Axioms → Mechanisms → Application → Synthesis
- **Interactive Components**: Expandable sections, quiz validation, animated transitions
- **First Principles Framework**: Deep dive into fundamental truths about ML fraud detection

### 2. Address Fraud Detection First Principles ⭐ **Enhanced with Deep Reference Links**
- **Complete Integration**: Interactive React guide + comprehensive documentation
- **Contextual Reference Links**: Each phase links to detailed companion documentation
- **918-line Reference Document**: Complete technical implementation guide
- **Progressive Disclosure**: Links appear contextually as you advance through phases
- **Comprehensive Footer**: Organized navigation to all documentation sections

## Documentation

All reference materials are included in the `docs/` directory:
- `docs/address-fraud-first-principles-companion.md` - Complete 918-line reference guide
- `docs/README.md` - Documentation overview

## Features

- **Interactive Learning**: Click-through phases with animations and state management
- **External Reference Integration**: Seamless links to GitHub-hosted documentation
- **Rich Tooltips**: Contextual previews without leaving the application
- **Responsive Design**: Works across desktop and mobile devices
- **Modern UI**: Built with React 19, Tailwind CSS, and Vite

## Local Development

### Prerequisites

- Node.js 18+ and npm

### Setup

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open your browser to the URL shown (typically `http://localhost:5173`)

### Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Deployment

This project is configured for deployment on Vercel:

1. Push code to GitHub repository: `git@github.com:rajnishkhatri/ml-fraud-react.git`
2. Connect repository to Vercel
3. Vercel will automatically detect Vite and deploy

### Vercel Configuration

The `vercel.json` file is already configured with:
- Build command: `npm run build`
- Output directory: `dist`
- Framework: Vite
- SPA routing rewrites

## Project Structure

```
ml-fraud-app/
├── src/
│   ├── components/
│   │   ├── LandingPage.jsx
│   │   ├── MLFraudFirstPrinciplesGuide.jsx
│   │   ├── AddressFraudFirstPrinciplesGuide.jsx     ⭐ Enhanced with reference links
│   │   └── StolenCardFraudFirstPrinciplesGuide.jsx
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── docs/                                           ⭐ Documentation directory
│   ├── address-fraud-first-principles-companion.md  ⭐ Complete reference guide (918 lines)
│   └── README.md                                   ⭐ Documentation overview
├── index.html
├── vite.config.js
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── vercel.json
└── README.md
```

## Technologies

- **React 19**: UI framework
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **PostCSS**: CSS processing

## License

This project is part of an educational series on ML fraud detection.
