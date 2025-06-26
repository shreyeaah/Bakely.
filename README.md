# Bakely. - AI-Powered Cake Builder + Multi-Bakery Platform

A multi-tenant bakery platform where independent bakers can create their own digital storefronts, manage custom cake orders, showcase menus, and interact directly with customers. It is designed to empower local bakers with modern online tools—without any centralized control.It also enables customers to customize and order cakes online. The platform is enhanced with AI-generated cake visualizations using Stability AI, providing an interactive and intelligent ordering experience.

###  For Customers:
- Browse local bakeries and menus
- Build your own custom cake (flavor, size, frosting, toppers, reference image etc.)
- View AI-generated cake previews using [Stability AI](https://platform.stability.ai/)
- Real-time pricing based on selected specifications, custom pricing particular to each baker
- Track your orders and receive status updates

###  For Bakers:
- Register and manage your own profile and branding
- Upload and manage your  menu (items, prices, images and description)
- Add/edit/delete menu items and pricing tiers
- Receive and manage orders (custom and standard)
- Update order status manually
- Maintain full control over your bakery's dashboard

## AI Integration

Bakely uses the **Stability AI** API to generate realistic cake images based on custom user inputs such as frosting, layers, toppers, and themes. This enhances the user's ability to visualize their order before placing it — making the experience smarter, more personalized, and fun.


##  Tech Stack

| Layer       | Technology                          |
|------------|--------------------------------------|
| Frontend    | HTML + Jinja2 + Tailwind CSS        |
| Backend     | Flask (Python)                      |
| Auth        | Flask-Login, bcrypt                 |
| Database    | PostgreSQL (via Supabase)           |
| Deployment  | Render                              |


## ⚙️ Setup & Deployment

### 1. Clone the repo
```bash
git clone https://github.com/shreyeaah/Bakely..git
cd bakely

### 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv\Scripts\activate on Windows
pip install -r requirements.txt

### 3. Set environment variables
Create a .env file or set the following variables:
SECRET_KEY=your-secret
DATABASE_URL=postgres://...
ADMIN_PASSWORD=your-admin-password
STABILITY_API_KEY=your-stability-api-key

### 4. Initialize the database
flask db init
flask db migrate -m "Initial"
flask db upgrade

### 5. Run the server
python run.py

### 6. Deployment on Render
Build command: pip install -r requirements.txt
Start command: gunicorn run:app
Set all required environment variables under Render → Environment.

## Admin Access
The admin user is auto-created on first deploy if ADMIN_PASSWORD is set in the environment. Use:
  Username: admin
  Password: (your env-defined password)

## Screenshots:
![Screenshot 2025-06-25 161909](https://github.com/user-attachments/assets/341cf165-0f87-4efe-a1ce-496c53a341c3)


### User Page:
![Screenshot 2025-06-25 161955](https://github.com/user-attachments/assets/911da5ab-635c-493e-b700-a0f7e9eb04a7)
Bakery Profile:
![Screenshot 2025-06-25 163904](https://github.com/user-attachments/assets/ca3af1e5-aa44-4d75-b48f-fee98084de43)
![Screenshot 2025-06-25 162058](https://github.com/user-attachments/assets/0265befb-23ae-46e9-951f-0b45c75e5c42)
![Screenshot 2025-06-25 162129](https://github.com/user-attachments/assets/4998c05c-d931-4f2d-bd95-1f6e8f18b485)

![Screenshot 2025-06-25 162058](https://github.com/user-attachments/assets/7bd533a5-fd3a-4f43-8aac-57578adf87d9)
![Screenshot 2025-06-25 162058](https://github.com/user-attachments/assets/7bd533a5-fd3a-4f43-8aac-57578adf87d9)

