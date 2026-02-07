🧠 TNT – Tap N Take
Smart Campus Scheduling & Queue Management System

🎓 User Roles
👨‍🎓 Student

OTP-based login using phone number

Secure JWT-based session

Role-based access (student-only features)

View available vendors (food court & stationery)

View menus and items

View available time slots

Pre-book a slot (no physical queue)

Place orders for food or stationery

One-click scheduling before arrival

See own orders only

Track order status:

pending

confirmed

cancelled

completed

Prevent double booking for same slot

Fair access to limited-capacity slots

🧑‍🍳 Vendor (Food Court / Stationery)

OTP-based login

Secure JWT with vendor role

Vendor identity derived only from token (no spoofing)

Create and manage own vendor profile

Create and manage menus

Add and manage items under own menus

Create and manage time slots

Define slot capacity

Slot capacity automatically reduced on booking

View only orders related to own slots

No access to other vendors’ data

Real-time order intake (ready for dashboard)

🛠️ Admin (planned, not implemented yet)

System-wide visibility

Vendor approval & management

Slot monitoring

Analytics & reporting

Campus-level configuration

📦 Core System Features
🔐 Authentication & Security

OTP-based authentication

JWT-based stateless auth

Role-based access control:

student

vendor

admin

Protected APIs using dependency injection

Vendor ownership enforcement

Zero trust on client-provided IDs

📅 Slot Scheduling & Queue Reduction

Slot-based booking system

Each slot has limited capacity

Atomic capacity decrement (ACID-safe)

No overbooking allowed

No race conditions

Designed for high concurrency

Ready for Redis-based locking (future)

🧾 Order & Booking System

Slot-based order creation

Atomic booking + capacity validation

Order lifecycle management

Order-item mapping

Vendor isolation (vendor sees only own orders)

Student isolation (student sees only own orders)

Production-grade transaction handling

🧱 Architecture & Engineering Features
🧩 Microservices Architecture

Auth Service

Vendor Service

Order / Booking Service

Admin Service (planned)

AI Service (planned)

Each service:

Independent FastAPI app

Independent database ownership

Clean separation of concerns

🗄️ Data & Performance

PostgreSQL as primary database

Proper relational modeling

Row-level locking for slot safety

Redis planned for:

Slot locking

Load handling

Rush management

Scalable for campus-wide usage

🤖 AI-Powered Features (Planned)

Slot ETA prediction

Rush hour forecasting

Smart slot recommendations

Load-aware scheduling

Reduced waiting time intelligence

📱 Frontend Experience (Planned)
Student App (React Native – Android)

Mobile-first experience

Fast booking

Slot reminders

Order tracking

Vendor / Admin Dashboard (React)

Slot & menu management

Order management

Analytics & insights

🚀 Production-Ready Foundations

Clean code structure

Swagger/OpenAPI docs

Secure JWT handling

Ownership enforcement

Transaction-safe booking

Designed for scale, not demos
