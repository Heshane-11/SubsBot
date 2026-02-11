# 🤖 SubsBot – Automated Subscription Management System

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Stripe](https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com/)
[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://telegram.org/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

SubsBot is a **production-ready subscription automation platform** that enables users to purchase and manage digital subscriptions directly through **Telegram**.  
It leverages an **event-driven backend architecture** to automate payment verification, access control, and subscription lifecycle management.

---

## 🚀 Key Features

- **Seamless Integration:** Purchase and manage subscriptions without leaving Telegram.
- **Secure Payments:** Stripe Checkout with full webhook verification.
- **Event-Driven Architecture:** Real-time payment confirmation and instant access provisioning.
- **Asynchronous Processing:** Celery + Redis for expiry checks and automated notifications.
- **Automated Lifecycle Management:** Handles activation, renewals, and expiration cleanup.
- **Cloud Ready:** Fully containerized with Docker for scalable deployment.

---

## 🛠️ Tech Stack

| Layer        | Technology Used |
|-------------|-----------------|
| **Backend** | Python, Django, Django REST Framework |
| **Payments** | Stripe API (Checkout + Webhooks) |
| **Messaging** | Telegram Bot API |
| **Task Queue** | Celery & Redis |
| **Database** | PostgreSQL |
| **Deployment** | Docker, Gunicorn, Render |

---

## 🧠 System Workflow

1. **User Initiation** – User selects a subscription plan via Telegram Bot.
2. **Checkout Session Creation** – Backend generates a Stripe Checkout session.
3. **Secure Payment** – User completes payment on Stripe’s hosted page.
4. **Webhook Event** – Stripe sends `checkout.session.completed` to Django backend.
5. **Validation & Activation** – Backend verifies signature and activates subscription.
6. **Notification** – User receives confirmation message via Telegram.
7. **Monitoring & Expiry Handling** – Celery Beat monitors and revokes access on expiry.

---

## 📦 Project Structure

```bash
SubsBot/
│
├── bot/                # Telegram bot logic
├── subscriptions/      # Subscription & payment handling
├── core/               # Core Django settings
├── docker/             # Docker configuration files
├── manage.py
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Heshane-11/SubsBot.git
cd SubsBot
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your_django_secret_key
DEBUG=True

STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=your_webhook_secret

TELEGRAM_BOT_TOKEN=your_telegram_bot_token

DATABASE_URL=postgres://user:password@localhost:5432/subsbot
REDIS_URL=redis://localhost:6379/0
```

---

## 🐳 Running with Docker

```bash
docker-compose up --build
```

---

## 🔄 Running Celery Worker

```bash
celery -A core worker -l info
```

## ⏰ Running Celery Beat Scheduler

```bash
celery -A core beat -l info
```

---

## 🌍 Deployment

The project is deployment-ready and optimized for platforms like:

- Render
- AWS EC2
- DigitalOcean
- Railway

Make sure to:
- Set `DEBUG=False`
- Configure allowed hosts
- Secure environment variables
- Enable HTTPS

---

## 🔐 Security Considerations

- Stripe webhook signature verification implemented.
- Sensitive keys stored in environment variables.
- PostgreSQL used for production-grade reliability.
- Access control automated via backend validation.

---

## 📈 Future Enhancements

- Admin dashboard analytics
- Multi-plan discount support
- Subscription upgrade/downgrade flow
- Payment retry automation
- Role-based access control

---

## 👨‍💻 Author

**Heshane Garg**  
Backend Developer | Django & Systems Design Enthusiast  

- LinkedIn: https://linkedin.com/in/heshane-garg-9b638a28b/
- GitHub: https://github.com/Heshane-11


---

⭐ If you found this project helpful, consider giving it a star!
