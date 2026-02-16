# Fish Monitoring System - Frontend PWA

Vue.js Progressive Web App for tracking fish acclimation and treatments.

## Features

- 📱 Mobile-first design (installable as PWA)
- 🎯 Simple, touch-friendly interface
- 🔄 Real-time data from backend API
- 💾 Offline support via service workers
- 🤖 AI-powered recommendations

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Edit `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_key_here
```

### 3. Start Development Server

```bash
npm run dev
```

Access at: http://localhost:5173

### 4. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/
│   ├── manifest.json          # PWA manifest
│   └── icons/                 # App icons (192x192, 512x512)
├── src/
│   ├── api/
│   │   └── client.js          # API client for backend
│   ├── views/
│   │   ├── Dashboard.vue      # Home screen
│   │   ├── ShipmentForm.vue   # Add new shipment
│   │   ├── TreatmentView.vue  # View treatments
│   │   ├── DailyChecklist.vue # Daily observations
│   │   └── SupplierScores.vue # Supplier rankings
│   ├── App.vue                # Root component
│   ├── main.js                # App entry point
│   └── router.js              # Vue Router config
├── index.html                 # HTML entry
├── vite.config.js             # Vite configuration
└── package.json               # Dependencies
```

## Views

### Dashboard
- Overview of active treatments
- Quick stats
- Navigation to other screens

### Shipment Form
- Add new fish shipments
- Get AI pre-shipment advice
- Auto-calculate density

### Treatment View
- List active treatments
- Quick access to daily checklists

### Daily Checklist
- Record observations
- Track symptoms
- Mark treatments completed

### Supplier Scores
- View supplier performance
- Success rates
- Best performing species

## Mobile Installation

### iOS
1. Open in Safari
2. Tap Share button
3. Select "Add to Home Screen"

### Android
1. Open in Chrome
2. Tap menu (⋮)
3. Select "Install app" or "Add to Home Screen"

## API Integration

All API calls go through `src/api/client.js`:

```javascript
import { shipmentsAPI } from '@/api/client';

// Create shipment
await shipmentsAPI.create(shipmentData);

// Get recommendations
await recommendationsAPI.preShipment(species, source);
```

## Development Tips

- Use Chrome DevTools > Application > Service Workers for PWA debugging
- Test offline mode by enabling "Offline" in Network tab
- Mobile testing: use device emulator or ngrok for real device testing

## Technologies

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Fast build tool
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Vite PWA Plugin** - PWA capabilities
