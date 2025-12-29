# Football Scouting Platform

A professional, full-stack football scouting and recruitment platform built with modern web technologies. This platform enables football clubs to discover players, analyze performance, manage shortlists, and generate comprehensive scouting reports.

## 🎯 Project Overview

This platform provides a complete solution for football recruitment teams, featuring:

- **Player Management** - Comprehensive player database with advanced search and filtering
- **Coach Management** - Track and scout coaching staff
- **Shortlist System** - CRM-style workflow for managing recruitment targets
- **Report Generation** - Automated PDF scouting reports
- **Role-Based Access Control** - Secure access for Admin, Analyst, Coach, and Scout roles
- **Analytics Engine** - GBE calculator and similarity matching algorithms

## 🏗️ Architecture

### Technology Stack

**Frontend:**
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- Shadcn/ui Components
- React Hook Form + Zod
- Clerk Authentication
- Axios

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL 15
- Redis 7
- SQLAlchemy ORM
- Alembic Migrations
- Pydantic v2
- UV Package Manager

**Infrastructure:**
- Docker & Docker Compose
- PostgreSQL with pgAdmin
- Redis with Redis Commander

## 📁 Project Structure

```
football-scouting-platform/
├── frontend/                    # Next.js application
│   ├── app/
│   │   ├── (auth)/             # Authentication pages
│   │   │   ├── sign-in/
│   │   │   └── sign-up/
│   │   ├── (dashboard)/        # Protected dashboard
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   ├── players/
│   │   │   │   ├── coaches/
│   │   │   │   └── shortlists/
│   │   │   └── layout.tsx
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/                 # Shadcn components
│   │   └── layout/
│   ├── lib/
│   │   ├── api-client.ts       # Axios API client
│   │   ├── types/              # TypeScript interfaces
│   │   └── validations/        # Zod schemas
│   ├── middleware.ts           # Auth middleware
│   └── package.json
│
└── backend/                     # FastAPI application
    ├── app/
    │   ├── api/
    │   │   └── v1/
    │   │       ├── endpoints/
    │   │       │   ├── auth.py
    │   │       │   ├── players.py
    │   │       │   ├── coaches.py
    │   │       │   ├── shortlists.py
    │   │       │   └── reports.py
    │   │       └── api.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── database.py
    │   │   ├── clerk_auth.py
    │   │   └── dependencies.py
    │   ├── models/
    │   │   ├── __init__.py
    │   │   ├── user.py
    │   │   ├── player.py
    │   │   ├── coach.py
    │   │   ├── shortlist.py
    │   │   ├── report.py
    │   │   └── activity_log.py
    │   ├── schemas/
    │   │   ├── user.py
    │   │   ├── player.py
    │   │   ├── coach.py
    │   │   ├── shortlist.py
    │   │   ├── report.py
    │   │   └── common.py
    │   └── main.py
    ├── alembic/
    ├── scripts/
    ├── docker-compose.yml
    ├── pyproject.toml
    └── .env
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **Docker** & Docker Compose (for databases)
- **Git**
- **UV** (Python package manager)

### Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/football-scouting-platform.git
cd football-scouting-platform
```

#### 2. Backend Setup

```bash
cd backend

# Install UV package manager
pip install uv

# Install dependencies
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your configuration
```

**Backend Environment Variables (.env):**

```env
# Database
DATABASE_URL=postgresql://football_user:football_pass_2025@localhost:5433/football_scouting
TEST_DATABASE_URL=postgresql://football_user:football_pass_2025@localhost:5433/football_scouting_test

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_your_clerk_secret_key
CLERK_PUBLISHABLE_KEY=pk_test_your_clerk_publishable_key
CLERK_WEBHOOK_SECRET=whsec_your_webhook_secret

# Super Admin (comma-separated emails)
SUPER_ADMIN_EMAILS=admin@example.com

# Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

#### 3. Start Database Services

```bash
# From backend directory
docker-compose up -d

# Check services are running
docker-compose ps

# View logs if needed
docker-compose logs -f
```

#### 4. Run Database Migrations

```bash
# Generate migration
uv run alembic revision --autogenerate -m "Initial database schema"

# Apply migration
uv run alembic upgrade head
```

#### 5. Start Backend Server

```bash
uv run uvicorn app.main:app --reload

# Server runs on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

#### 6. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with your Clerk keys
```

**Frontend Environment Variables (.env.local):**

```env
# Clerk Keys
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here
CLERK_SECRET_KEY=sk_test_your_key_here

# Clerk URLs
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_VERSION=v1
```

#### 7. Start Frontend Server

```bash
npm run dev

# Frontend runs on http://localhost:3000
```

### Accessing the Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **PostgreSQL Admin:** http://localhost:8080 (admin@footballscout.com / admin123)
- **Redis Commander:** http://localhost:8081

## 🔐 Authentication & Authorization

### User Roles & Permissions

| Role | Players | Coaches | Shortlists | Reports | Analytics | User Mgmt |
|------|---------|---------|------------|---------|-----------|-----------|
| **Admin** | Full | Full | Full | Full | Full | Full |
| **Analyst** | Full | Full | Full | Create/Read/Delete | Read | None |
| **Coach** | Read | Read | Create/Read/Update | Create/Read | None | None |
| **Scout** | Read/Update | Read | Create/Read/Update | Create/Read | None | None |

### Setting Up First Admin

1. **Environment Variable Method (Recommended):**
   - Add your email to `SUPER_ADMIN_EMAILS` in backend `.env`
   - Sign up through Clerk
   - Your account will automatically get admin role

2. **Manual Database Update:**
   ```sql
   UPDATE users SET role = 'admin' WHERE email = 'your-email@example.com';
   ```

## 📊 Database Schema

### Core Tables

- **users** - System users with authentication and roles
- **players** - Football player profiles and statistics
- **coaches** - Coach profiles and tactical information
- **shortlists** - Recruitment shortlists (player/coach)
- **shortlist_items** - Items within shortlists with status tracking
- **reports** - Generated scouting reports
- **activity_logs** - Audit trail of user actions

### Key Features

- Full-text search on players and coaches
- JSON fields for flexible statistics storage
- Soft delete functionality
- Automatic timestamp tracking
- Foreign key constraints for data integrity
- Optimized indexes for query performance

## 🎨 Frontend Features

### Implemented Pages

✅ **Authentication**
- Sign in / Sign up (Clerk hosted)
- Protected routes with middleware
- Role-based navigation

✅ **Dashboard**
- User profile display
- Quick statistics
- Recent activity

✅ **Players**
- List view with search, filters, and pagination
- Add new player form with validation
- Player detail page with tabs
- Edit player functionality
- Delete with confirmation
- Similar players suggestions

✅ **Coaches**
- Same pattern as players (to be implemented)

⏳ **Shortlists** (Planned)
- Create and manage shortlists
- Add players/coaches to lists
- Status workflow tracking
- Export to CSV/PDF

⏳ **Reports** (Planned)
- Generate scouting reports
- Download PDF reports
- Report history

### UI Components

Built with Shadcn/ui:
- Button, Input, Textarea
- Card, Alert, Badge
- Table, Select, Dialog
- Tabs, Skeleton, Form
- Alert Dialog, Separator

## 🔧 API Documentation

### Authentication Endpoints

```
GET  /api/v1/auth/me          - Get current user
POST /api/v1/auth/sync        - Sync user with Clerk
POST /api/v1/auth/webhook/clerk - Clerk webhook handler
```

### Player Endpoints

```
GET    /api/v1/players                - List players (with filters)
POST   /api/v1/players                - Create player
GET    /api/v1/players/{id}           - Get player details
PUT    /api/v1/players/{id}           - Update player
DELETE /api/v1/players/{id}           - Delete player (soft delete)
GET    /api/v1/players/{id}/similar   - Get similar players
GET    /api/v1/players/stats/summary  - Get player statistics
```

### Coach Endpoints

```
GET    /api/v1/coaches                - List coaches (with filters)
POST   /api/v1/coaches                - Create coach
GET    /api/v1/coaches/{id}           - Get coach details
PUT    /api/v1/coaches/{id}           - Update coach
DELETE /api/v1/coaches/{id}           - Delete coach
GET    /api/v1/coaches/{id}/similar   - Get similar coaches
```

### Shortlist Endpoints

```
GET    /api/v1/shortlists                      - List shortlists
POST   /api/v1/shortlists                      - Create shortlist
GET    /api/v1/shortlists/{id}                 - Get shortlist details
PUT    /api/v1/shortlists/{id}                 - Update shortlist
DELETE /api/v1/shortlists/{id}                 - Delete shortlist
POST   /api/v1/shortlists/{id}/items           - Add item to shortlist
PUT    /api/v1/shortlists/{id}/items/{item_id} - Update item
DELETE /api/v1/shortlists/{id}/items/{item_id} - Remove item
```

### Report Endpoints

```
GET    /api/v1/reports             - List reports
POST   /api/v1/reports             - Generate report
GET    /api/v1/reports/{id}        - Get report details
GET    /api/v1/reports/{id}/download - Download report
DELETE /api/v1/reports/{id}        - Delete report
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
uv run pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### API Testing with Swagger

1. Start the backend server
2. Visit http://localhost:8000/docs
3. Get authentication token from frontend
4. Click "Authorize" and paste token
5. Test any endpoint

## 🐳 Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart a service
docker-compose restart db

# Remove all data (⚠️ destructive)
docker-compose down -v
```

## 📝 Development Workflow

### Adding a New Feature

1. **Backend:**
   - Create model in `app/models/`
   - Create schema in `app/schemas/`
   - Create endpoint in `app/api/v1/endpoints/`
   - Generate migration: `alembic revision --autogenerate`
   - Apply migration: `alembic upgrade head`

2. **Frontend:**
   - Create types in `lib/types/`
   - Add API methods to `lib/api-client.ts`
   - Create validation schema in `lib/validations/`
   - Build UI pages in `app/(dashboard)/`

### Code Style

**Backend:**
- Follow PEP 8
- Use type hints
- Maximum line length: 100
- Run: `uv run black app/` and `uv run isort app/`

**Frontend:**
- Follow Airbnb style guide
- Use TypeScript strictly
- Run: `npm run lint`

## 🚢 Deployment

### Backend Deployment (Railway/Render)

1. Connect your GitHub repository
2. Set environment variables
3. Deploy command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend Deployment (Vercel)

1. Connect your GitHub repository
2. Framework preset: Next.js
3. Root directory: `frontend`
4. Set environment variables
5. Deploy

### Database (PostgreSQL)

- Use managed PostgreSQL (Railway/Render/Heroku)
- Run migrations after deployment
- Set up automated backups

## 🔒 Security Considerations

- All routes protected by Clerk authentication
- Role-based access control on API endpoints
- SQL injection protection via SQLAlchemy
- CORS configured for specific origins
- Secrets managed via environment variables
- HTTPS required in production
- Rate limiting on API endpoints
- Input validation with Pydantic/Zod
- Audit logging for all actions

## 📈 Performance Optimization

- Database indexes on frequently queried fields
- Redis caching for frequently accessed data
- Pagination on all list endpoints
- Lazy loading on frontend
- Image optimization with Next.js
- API response compression
- Connection pooling for database

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- FastAPI for the excellent Python framework
- Next.js team for the React framework
- Clerk for authentication services
- Shadcn for beautiful UI components
- The open-source community

## 📞 Support

For support, email gelberoo46@gmail.com or join our Slack channel.

## 🗺️ Roadmap

### Phase 1 - Core Features ✅
- [x] Authentication with Clerk
- [x] Player CRUD operations
- [x] Database setup and migrations
- [x] Basic UI with Tailwind

### Phase 2 - Enhanced Features 🚧
- [x] Player detail pages
- [ ] Coach management (in progress)
- [ ] Shortlist CRM system
- [ ] Advanced search and filters

### Phase 3 - Analytics 📋
- [ ] GBE (Gross Base Earnings) calculator
- [ ] Player similarity algorithm
- [ ] Performance analytics dashboard
- [ ] Market value predictions

### Phase 4 - Reports 📊
- [ ] PDF report generation
- [ ] Customizable report templates
- [ ] Automated email delivery
- [ ] Excel export functionality

### Phase 5 - Advanced 🚀
- [ ] Real-time notifications
- [ ] File uploads for documents
- [ ] Video analysis integration
- [ ] Mobile app (React Native)
- [ ] Multi-language support

## 📊 Project Statistics

- **Lines of Code:** ~15,000+
- **API Endpoints:** 30+
- **Database Tables:** 8
- **Frontend Pages:** 10+
- **Development Time:** 20 weeks (as per roadmap)

---

Built with ❤️ for football recruitment professionals