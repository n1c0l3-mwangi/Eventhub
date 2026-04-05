# EventHub - Event Management and Discovery System

EventHub is a web-based event management and discovery platform designed for the Kenyan market. It allows users to discover events, purchase tickets via M-Pesa, receive QR code tickets, and provides organizers with real-time sales analytics.

## Features

### For Event Goers
- Browse and search events by category, date, and location
- One-click "Events Near Me" geolocation discovery
- Purchase tickets with M-Pesa payment simulation
- Receive QR code tickets for event entry
- View all purchased tickets
- Print tickets with QR codes

### For Event Organizers
- Create and manage events with images
- Set VIP and Regular ticket tiers with separate pricing
- View real-time ticket sales and revenue analytics
- Track recent ticket purchases
- Edit event details anytime

### For Administrators
- Approve or reject pending events
- Manage users, categories, and events
- View organizer revenue summaries
- Full Django admin panel access

## Tech Stack

- **Backend:** Python 3.12, Django 5.0
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Payment:** M-Pesa simulation module
- **QR Codes:** qrcode library with PIL

## Installation

### Prerequisites
- Python 3.12 or higher
- Git

### Step 1: Clone the Repository
```bash
git clone https://github.com/n1c0l3-mwangi/Eventhub.git
cd Eventhub
