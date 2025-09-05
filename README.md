# Real Estate MVP - Agent Rewards System

A comprehensive real estate agent rewards system built with Django that tracks agent performance, customer payments, and automatically awards gifts based on milestone achievements.

## 🎯 Features

### User Roles
- **Admin**: Full system management, can add customers/agents/payments, update gift status
- **Agents**: View performance metrics, track points, see earned gifts
- **Customers**: View assigned agent and payment history

### Reward System
- **Points Calculation**: 1 point per ₹100 in customer payments
- **Star Levels**: 7 progressive star levels with automatic progression
- **Automatic Gift Assignment**: Gifts are automatically created when milestones are reached
- **Gift Management**: Admin can mark gifts as delivered

## ⭐ Star Level Progression

| Star Level | Points Required | Gift |
|------------|----------------|------|
| 1 ⭐ | 0+ | Coffee Mug |
| 2 ⭐ | 2,500+ | T-Shirt |
| 3 ⭐ | 5,000+ | Backpack |
| 4 ⭐ | 7,500+ | Headphones |
| 5 ⭐ | 10,000+ | Smartwatch |
| 6 ⭐ | 12,000+ | Laptop |
| 7 ⭐ | 15,000+ | Vacation Package |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2+
- SQLite (default) or PostgreSQL

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd RealestateMVP
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Set up default gifts**
   ```bash
   python manage.py setup_gifts
   ```

6. **Create a superuser (admin)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📱 Usage

### Admin Dashboard
- **URL**: `/admin-dashboard/`
- **Features**:
  - View all agents, customers, and payments
  - Add new customers and payments
  - Manage gift delivery status
  - Monitor system performance

### Agent Dashboard
- **URL**: `/agent-dashboard/`
- **Features**:
  - View current points and star level
  - See progress to next milestone
  - Track customer and payment history
  - View earned gifts and delivery status

### Customer Dashboard
- **URL**: `/customer-dashboard/<id>/`
- **Features**:
  - View assigned agent information
  - Check payment history
  - Monitor transaction details

## 🔧 System Architecture

### Models
- **Agent**: User model with points and star level tracking
- **Customer**: Customer information with agent assignment
- **Payment**: Transaction records with automatic point calculation
- **Gift**: Available rewards for each star level
- **AgentGift**: Junction table tracking earned gifts and delivery status

### Key Features
- **Automatic Point Calculation**: Points are calculated automatically when payments are added
- **Star Level Updates**: Star levels are updated automatically based on total points
- **Gift Assignment**: Gifts are automatically assigned when agents reach new star levels
- **Status Tracking**: Admin can track and update gift delivery status

## 📊 Database Schema

```
Agent (User)
├── username, email, password
├── total_points (Integer)
└── star_level (Integer)

Customer
├── name, email
└── agent (ForeignKey to Agent)

Payment
├── customer, agent, amount
├── points (auto-calculated)
├── project_name, receipt_number
└── date

Gift
├── name, description
└── required_star_level

AgentGift
├── agent, gift
├── status (pending/delivered)
├── date_earned, date_delivered
└── unique constraint on (agent, gift)
```

## 🎁 Gift System Workflow

1. **Payment Processing**:
   - Admin adds customer payment
   - System calculates points (₹100 = 1 point)
   - Agent's total points are updated
   - Star level is recalculated

2. **Gift Assignment**:
   - System checks if agent qualifies for new gifts
   - Creates AgentGift records for new star levels
   - Status set to 'pending' by default

3. **Gift Management**:
   - Admin views pending gifts in dashboard
   - Can mark gifts as 'delivered'
   - Delivery date is recorded automatically

## 🔒 Security Features

- **Role-based Access Control**: Different dashboards for different user types
- **Authentication Required**: All dashboards require proper login
- **Admin-only Operations**: Only admins can modify system data
- **CSRF Protection**: All forms include CSRF tokens

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 API Endpoints

The system includes REST API endpoints for:
- Agent information and performance
- Customer data and payment history
- Gift status and delivery tracking

## 🚀 Deployment

### Production Considerations
- Use PostgreSQL instead of SQLite
- Set `DEBUG = False`
- Configure proper `SECRET_KEY`
- Set up static file serving
- Use environment variables for sensitive data

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🔄 Changelog

### Version 1.0.0
- Initial MVP release
- Basic reward system implementation
- Three-tier user role system
- Automatic gift assignment
- Admin gift management

---

**Built with ❤️ using Django**
