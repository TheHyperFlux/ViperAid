from app import app, db, Hospital, Rescuer, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create tables
    db.create_all()

    # Add sample hospitals
    hospitals = [
    {'name': 'Tribhuvan University Teaching Hospital', 'phone': '+977-1-4410911', 'latitude': 27.7480, 'longitude': 85.3240},
    {'name': 'Bir Hospital', 'phone': '+977-1-4221119', 'latitude': 27.7060, 'longitude': 85.3150},
    {'name': 'Patan Hospital', 'phone': '+977-1-5522295', 'latitude': 27.6680, 'longitude': 85.3200},
    {'name': 'Sukraraj Tropical & Infectious Disease Hospital (Teku Hospital)', 'phone': '+977-1-425xxxx', 'latitude': 27.7060, 'longitude': 85.3120},
    {'name': 'Bheri Hospital (Nepalgunj)', 'phone': '+977-81-520188', 'latitude': 28.0530, 'longitude': 81.6170},
    {'name': 'BP Koirala Institute of Health Sciences (Dharan)', 'phone': '+977-25-525015', 'latitude': 26.8110, 'longitude': 87.2829},
    {'name': 'Katari Hospital (Udayapur)', 'phone': '+977-31-560128', 'latitude': 26.9200, 'longitude': 86.7100},
    {'name': 'Mahakali Provincial Hospital (Mahendranagar)', 'phone': '+977-99-523xxxx', 'latitude': 28.6340, 'longitude': 80.6190},
    {'name': 'Bharatpur Hospital (Chitwan)', 'phone': '+977-56-520xxx', 'latitude': 27.6833, 'longitude': 84.4333},
    {'name': 'Rapti Provincial Hospital (Tulsipur)', 'phone': '+977-82-520xxx', 'latitude': 28.0600, 'longitude': 82.2890}
]

    for hospital in hospitals:
        if not Hospital.query.filter_by(name=hospital['name']).first():
            new_hospital = Hospital(
                name=hospital['name'],
                phone=hospital['phone'],
                latitude=hospital['latitude'],
                longitude=hospital['longitude']
            )
            db.session.add(new_hospital)

    # Add sample rescuers
    rescuers = [
    {'name': 'Ramji Gautam', 'phone': '+977-9846033459', 'latitude': 28.2098, 'longitude': 83.9856},  # Kaski
    {'name': 'Keshab Raj Sapkota', 'phone': '+977-9856024195', 'latitude': 28.2098, 'longitude': 83.9856},  # Kaski
    {'name': 'Asbin Ojha', 'phone': '+977-9845370199', 'latitude': 27.7000, 'longitude': 84.5000},  # Nawalpur
    {'name': 'Rishi Baral', 'phone': '+977-9856038360', 'latitude': 28.2098, 'longitude': 83.9856},  # Kaski
    {'name': 'Aakash Bhandari', 'phone': '+977-9816636337', 'latitude': 28.2098, 'longitude': 83.9856},  # Lakeside, Kaski
    {'name': 'Siddhartha Bhandari', 'phone': '+977-9806600444', 'latitude': 28.2098, 'longitude': 83.9856},  # Lekhnath
    {'name': 'Roshan Giri', 'phone': '+977-9840290781', 'latitude': 28.2098, 'longitude': 83.9856},  # Chorepatan, Kaski
    {'name': 'Rohit Giri', 'phone': '+977-9866344156', 'latitude': 28.2098, 'longitude': 83.9856},  # Chorepatan, Kaski
    {'name': 'Niroj Karki', 'phone': '+977-9849517193', 'latitude': 27.6730, 'longitude': 85.3430},  # Duwakot, Bhaktapur
    {'name': 'Subodh Acharya', 'phone': '+977-9843286283', 'latitude': 27.6790, 'longitude': 85.1900},  # Dakshinkali, Kathmandu
    {'name': 'Prithivi Narayan Sharma', 'phone': '+977-9856055058', 'latitude': 28.0500, 'longitude': 83.8500},  # Syangja
    {'name': 'Anirudra Sapkota', 'phone': '+977-9845070473', 'latitude': 27.7000, 'longitude': 84.4320},  # Bharatpur, Chitwan
    {'name': 'Sunil Sapkota', 'phone': '+977-9845364525', 'latitude': 27.7000, 'longitude': 84.4320},  # Bharatpur, Chitwan :contentReference[oaicite:1]{index=1}
    {'name': 'Puskal Nepal', 'phone': '+977-9845703045', 'latitude': 27.7000, 'longitude': 84.4320},  # Sauraha, Chitwan
    {'name': 'Yam Lal Bhandari', 'phone': '+977-9855081753', 'latitude': 27.7000, 'longitude': 84.4320},  # Bharatpur, Chitwan
    {'name': 'NTNC‑BCC (Chitwan)', 'phone': '+977-56-58062', 'latitude': 27.7000, 'longitude': 84.4320},
    {'name': 'Dr. Amod Ghimire', 'phone': '+977-9865005828', 'latitude': 27.5000, 'longitude': 84.7500},  # Kawasoti, Nawalpur
    {'name': 'Prem Mahato', 'phone': '+977-9805423471', 'latitude': 27.4830, 'longitude': 84.2750},  # Nawalparasi
    {'name': 'Mithila Wildlife Trust', 'phone': '+977-9817629229', 'latitude': 26.7167, 'longitude': 85.8667},  # Janakpur area :contentReference[oaicite:2]{index=2}
    {'name': 'Nepal Snake Rescue Team (Pokhara)', 'phone': '+977-9814142349', 'latitude': 28.2098, 'longitude': 83.9856},  # Pokhara :contentReference[oaicite:3]{index=3}
    {'name': 'Rohit Giri (Pokhara)', 'phone': '98245786xx', 'latitude': 28.2098, 'longitude': 83.9856}  # no direct phone; known Pokhara rescuer :contentReference[oaicite:4]{index=4}
]

    for rescuer in rescuers:
        if not Rescuer.query.filter_by(name=rescuer['name']).first():
            new_rescuer = Rescuer(
                name=rescuer['name'],
                phone=rescuer['phone'],
                latitude=rescuer['latitude'],
                longitude=rescuer['longitude']
            )
            db.session.add(new_rescuer)

    # Add default admin user
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)

    # Commit changes
    db.session.commit()
    print("Sample hospitals, rescuers, and admin user added successfully!")