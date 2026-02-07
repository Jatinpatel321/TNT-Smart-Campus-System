# TNT Admin Dashboard

## Overview
Web-based dashboard for administrators to monitor and manage the TNT food ordering system.

## Features
- **System Health Monitoring**: Service status, database connections, Redis status
- **Vendor Management**: Approve/reject vendors, view performance metrics
- **Order Analytics**: Total orders, revenue, peak hours, popular items
- **User Management**: View all users, role management
- **Slot Utilization**: Real-time capacity monitoring across all vendors
- **AI Insights**: Rush hour predictions, ETA accuracy metrics

## Tech Stack
- **Frontend**: React + TypeScript
- **UI Library**: Material-UI (MUI)
- **Charts**: Chart.js or Recharts
- **State Management**: Redux Toolkit
- **API Client**: Axios with JWT auth

## Project Structure
```
admin-dashboard/
├── src/
│   ├── components/       # Reusable UI components
│   ├── pages/           # Main dashboard pages
│   │   ├── Dashboard.tsx
│   │   ├── Vendors.tsx
│   │   ├── Orders.tsx
│   │   ├── Users.tsx
│   │   └── Analytics.tsx
│   ├── services/        # API integration
│   ├── utils/           # Helpers and constants
│   ├── types/           # TypeScript interfaces
│   └── App.tsx
├── public/
└── package.json
```

## Key Components
1. **Dashboard Overview**: System health, key metrics, recent activity
2. **Vendor Management**: List, approve/reject, performance charts
3. **Order Monitoring**: Real-time order status, revenue tracking
4. **User Administration**: Role management, user statistics
5. **Analytics**: Charts for trends, peak hours, popular items

## API Integration
- Connects to all microservices (auth, vendor, order, admin)
- JWT authentication for admin access
- Real-time updates via polling/WebSocket

## Deployment
- Docker containerization
- Nginx reverse proxy
- SSL/TLS encryption
- CI/CD pipeline ready
