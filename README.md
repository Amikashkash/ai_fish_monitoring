# 🐠 Fish Monitoring System

AI-powered system for tracking ornamental fish acclimation and treatment during the critical first two weeks after receiving shipments.

## Features

- 📊 **Track Shipments** - Record fish arrivals with species, source, quantity, and tank conditions
- 💊 **Treatment Protocols** - Manage medication schedules and dosages
- 📝 **Daily Observations** - Quick mobile-friendly health checks
- 🤖 **AI Recommendations** - Learn from historical data to suggest optimal treatments
- 📈 **Supplier Scoring** - Rank suppliers by success rates to guide purchasing
- 📱 **Mobile PWA** - Works on any device, installable like a native app
- 🔄 **Automated Reminders** - WhatsApp notifications via n8n workflows

## Technology Stack

- **Backend**: Python + FastAPI
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Vue.js PWA
- **AI**: Claude API (Anthropic)
- **Automation**: n8n
- **Notifications**: WhatsApp

## Project Structure

```
fish-monitoring/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── config/         # Settings and database
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Business logic
│   │   ├── crud/           # Database operations
│   │   ├── ai/             # AI integration
│   │   ├── api/            # API routes
│   │   └── utils/          # Helper functions
│   ├── requirements.txt
│   └── .env
├── frontend/               # Vue.js PWA
│   ├── src/
│   │   ├── views/         # Page components
│   │   └── components/    # Reusable components
│   └── package.json
├── supabase/              # Database migrations
└── docs/                  # Documentation
```

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Supabase account (free tier)
- Anthropic API key

### 1. Database Setup

1. Create a free Supabase project at [supabase.com](https://supabase.com)
2. Go to SQL Editor in Supabase dashboard
3. Copy content from `supabase/migrations/001_initial_schema.sql`
4. Execute the migration
5. Verify tables created in Table Editor

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.template .env

# Edit .env and add your credentials:
# - ANTHROPIC_API_KEY
# - SUPABASE_URL
# - SUPABASE_KEY
```

### 3. Run Backend

```bash
# From backend directory
uvicorn app.main:app --reload

# API will be available at:
# http://localhost:8000
# API docs at:
# http://localhost:8000/docs
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment template
copy .env.template .env

# Edit .env and add:
# - VITE_API_URL=http://localhost:8000
# - VITE_SUPABASE_URL
# - VITE_SUPABASE_ANON_KEY
```

### 5. Run Frontend

```bash
# From frontend directory
npm run dev

# PWA will be available at:
# http://localhost:5173
```

### 6. n8n Setup (Optional)

```bash
# Install n8n globally
npm install n8n -g

# Start n8n
n8n start

# Access at http://localhost:5678
# Import workflows from n8n_workflows/
```

## Usage

### Recording a New Shipment

1. Open PWA on your mobile device
2. Click "Add New Shipment"
3. Fill in:
   - Fish scientific name
   - Common name
   - Source country
   - Quantity
   - Aquarium volume
4. Click "Get AI Recommendation"
5. Review suggested protocol
6. Click "Save & Start Treatment"

### Daily Routine

1. Receive WhatsApp reminder at 8 AM
2. Perform treatments listed
3. Submit observation via:
   - WhatsApp form, OR
   - PWA daily checklist
4. Rate overall condition (1-5)
5. Check symptom boxes if needed

### 5-Day Follow-up

1. Receive reminder 5 days after treatment ends
2. Count surviving fish
3. Check if symptoms returned
4. Submit follow-up assessment
5. AI updates knowledge base automatically

## Architecture

### Server Roles

```
User's Phone
     │
     ↓
[Vercel PWA] ──────→ [Supabase DB]
     │                     ↑
     ↓                     │
[Railway API] ←────────────┘
     │         (AI logic, complex queries)
     ↓
[Claude AI API]

[n8n] ──→ [Railway API] ──→ [WhatsApp]
```

**Why each component:**

- **Supabase**: Cloud PostgreSQL database + auto REST API
- **Railway/Render**: Custom Python backend for AI logic (Supabase can't run Python or call Claude API)
- **Vercel**: Fast CDN hosting for PWA
- **n8n**: Automated scheduling and WhatsApp integration

## Code Organization

This project follows strict modularity:

- **Small files** (< 200 lines each)
- **Single responsibility** per file
- **Comprehensive docstrings** on every function
- **Type hints** throughout
- **Reusable utilities** extracted to services

Example:
```python
# app/services/density_calculator.py
def calculate_density(quantity: int, volume: int) -> float:
    """
    Calculate fish density (fish per liter) for health assessment.

    Args:
        quantity: Number of fish
        volume: Aquarium volume in liters

    Returns:
        Fish density, rounded to 2 decimal places
    """
```

## Database Schema

7 tables:

1. **shipments** - Fish arrival records
2. **drug_protocols** - Standard medication info
3. **treatments** - Treatment sessions
4. **treatment_drugs** - Drugs used in treatments (many-to-many)
5. **daily_observations** - Daily health checks
6. **followup_assessments** - 5-day post-treatment evaluations
7. **ai_knowledge** - Learned patterns from history

## AI Behavior

**Critical Constraint**: AI uses ONLY your historical data. No internet research.

Example:
```
First shipment of Betta splendens from Thailand:
→ "No historical data. Standard quarantine protocol recommended."

After 5 successful shipments with 92% avg success:
→ "High confidence recommendation: Methylene Blue 2mg/L + Salt 1g/L for 7 days"
```

## Deployment

### Free Tier Deployment

**Total Cost: $0-25/month**

- **Supabase**: Free (500MB database)
- **Railway**: Free $5 credit/month
- **Vercel**: Free (PWA hosting)
- **n8n**: $20/month OR free if self-hosted

See `docs/DEPLOYMENT.md` for detailed deployment guide.

## Development

### Running Tests

```bash
cd backend
pytest
```

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Keep functions small and focused

### Adding a New Feature

1. Create model in `app/models/`
2. Create schema in `app/schemas/`
3. Create CRUD in `app/crud/`
4. Add business logic to `app/services/`
5. Create API route in `app/api/`
6. Update frontend views

## Documentation

- [API Documentation](docs/API_DOCUMENTATION.md) - Full API reference
- [Setup Guide](docs/SETUP_GUIDE.md) - Detailed setup instructions
- [n8n Setup](docs/N8N_SETUP.md) - n8n workflow configuration
- [Supabase Setup](docs/SUPABASE_SETUP.md) - Database configuration

## Troubleshooting

### Backend won't start

```bash
# Check Python version
python --version  # Should be 3.10+

# Verify virtual environment activated
where python  # Should point to venv

# Check dependencies
pip list
```

### Database connection fails

1. Verify Supabase credentials in `.env`
2. Check if Supabase project is active
3. Confirm database migration ran successfully

### AI recommendations not working

1. Verify `ANTHROPIC_API_KEY` in `.env`
2. Check API key is valid on Anthropic console
3. Ensure you have API credits

## Contributing

This is a personal project for fish monitoring. Feel free to fork and adapt for your own use.

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or questions, open an issue on GitHub.

---

Built with ❤️ for the ornamental fish community
