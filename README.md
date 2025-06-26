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
```
### 2. Create a virtual environment and install dependencies
```bash
python -m venv .venv
.venv\Scripts\activate on Windows
pip install -r requirements.txt
```
### 3. Set environment variables
Create a .env file or set the following variables:
```bash
SECRET_KEY=your-secret
DATABASE_URL=postgres://...
ADMIN_PASSWORD=your-admin-password
STABILITY_API_KEY=your-stability-api-key
```

### 4. Initialize the database
```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
```
### 5. Run the server
```bash
python run.py
```
### 6. Deployment on Render
```bash
Build command: pip install -r requirements.txt
Start command: gunicorn run:app
Set all required environment variables under Render → Environment.
```
## Admin Access
The admin user is auto-created on first deploy if ADMIN_PASSWORD is set in the environment. Use:
  Username: admin
  Password: (your env-defined password)

## Screenshots:
![Screenshot 2025-06-25 161909](https://github.com/user-attachments/assets/341cf165-0f87-4efe-a1ce-496c53a341c3)


### User Dashboard:
![Screenshot 2025-06-25 161955](https://github.com/user-attachments/assets/911da5ab-635c-493e-b700-a0f7e9eb04a7)

![Screenshot 2025-06-25 163904](https://github.com/user-attachments/assets/ca3af1e5-aa44-4d75-b48f-fee98084de43)
![Screenshot 2025-06-25 162058](https://github.com/user-attachments/assets/0265befb-23ae-46e9-951f-0b45c75e5c42)
![Screenshot 2025-06-25 162129](https://github.com/user-attachments/assets/4998c05c-d931-4f2d-bd95-1f6e8f18b485)
![Screenshot 2025-06-25 162148](https://github.com/user-attachments/assets/a7a627f9-7d1b-4c7e-a80d-b8eabf9b866c)
![Screenshot 2025-06-25 162249](https://github.com/user-attachments/assets/81e68426-f5a3-465d-a14d-b759d6c1ff4e)
![Screenshot 2025-06-25 162507](https://github.com/user-attachments/assets/5248bc61-d5a3-4a38-9329-bb81ab6db17d)
![Screenshot 2025-06-25 162446](https://github.com/user-attachments/assets/a6571ad5-ad3b-4044-832d-10927a1c01b1)

### Baker Dashboard
![Screenshot 2025-06-25 162558](https://github.com/user-attachments/assets/50d64d11-e7d9-4093-a043-735a1aaecfc2)
![Screenshot 2025-06-25 162759](https://github.com/user-attachments/assets/35d15123-4771-4f6d-aa9d-703dff03ca47)
![Screenshot 2025-06-25 162739](https://github.com/user-attachments/assets/62892acc-ef1a-461c-b9e1-89ce1458ddef)
![Screenshot 2025-06-25 162620](https://github.com/user-attachments/assets/22a725e1-596a-4b8a-b443-14f73419bc29)
![Screenshot 2025-06-25 162639](https://github.com/user-attachments/assets/85dca543-5541-40ec-bb97-1497cd96f637)

### Admin Dashboard:
![Screenshot 2025-06-25 164105](https://github.com/user-attachments/assets/e52f6560-2144-467f-ab90-44169224ff71)


