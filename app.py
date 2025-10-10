from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import torch
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
from torchvision import transforms
from PIL import Image
import io
import math
from datetime import datetime, timezone, timedelta
import logging
import timm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snakesafe.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'a-very-long-random-string-1234567890'  # Replace with secure key in production
db = SQLAlchemy(app)

# Define Nepal Time Zone (UTC+5:45)
npt_tz = timezone(timedelta(hours=5, minutes=45))

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Hospital(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Rescuer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    snake_species = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    request_type = db.Column(db.String(20), default='hospital')
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(npt_tz), nullable=False)

# Snake Information
SNAKE_INFO = {
    'Ahaetulla_nasuta': {
        'common_name': 'Sri Lankan Green Vine Snake',
        'nepali_name': 'हरियो लताके सर्प (Hariyo Latake Sarpa)',
        'danger': 'Mildly venomous',
        'habitat': 'Forests, shrubs'
    },
    'Amphiesma_stolatum': {
        'common_name': 'Buff Striped Keelback',
        'nepali_name': 'बगाले सर्प (Bagale Sarpa), आहारा (Aahara), हररा (Harara)',
        'danger': 'Non-venomous',
        'habitat': 'Wetlands, rice fields'
    },
    'Boiga_ochracea': {
        'common_name': 'Tawny Cat Snake',
        'nepali_name': 'बिरालो सर्प (Biralo Sarpa)',
        'danger': 'Mildly venomous',
        'habitat': 'Forests'
    },
    'Boiga_trigonata': {
        'common_name': 'Common Cat Snake',
        'nepali_name': 'बिरालो सर्प (Biralo Sarpa)',
        'danger': 'Mildly venomous',
        'habitat': 'Scrub forests, rocky terrain'
    },
    'Bungarus_caeruleus': {
        'common_name': 'Common Krait',
        'nepali_name': 'करेत (Krait), Seto-kalo Chure Sarpa',
        'danger': 'Highly venomous',
        'habitat': 'Forests, fields'
    },
    'Bungarus_fasciatus': {
        'common_name': 'Banded Krait',
        'nepali_name': 'गनगलि, गनग्वली (Gangawari, Panhelo-kalo Chure Sarpa, Kanthamala, Laxmi Sanp, Raja Sanp, Maher, Gwala Sarpa, Ahiriniya Sanp)',
        'danger': 'Highly venomous',
        'habitat': 'Forests, grasslands'
    },
    'Calliophis_bivirgatus': {
        'common_name': 'Blue Coral Snake',
        'nepali_name': 'नीलो मूँगा सर्प (Nilo Moonga Sarpa)',
        'danger': 'Highly venomous',
        'habitat': 'Rainforests'
    },
    'Coelognathus_radiatus': {
        'common_name': 'Copperhead Racer',
        'nepali_name': 'तामाको टाउको सर्प (Tamako Tauko Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Forests, farmlands'
    },
    'Craspedocephalus_albolabris': {
        'common_name': 'White-lipped Pit Viper',
        'nepali_name': 'सेतो ओठे सर्प (Seto Othe Sarpa)',
        'danger': 'Venomous',
        'habitat': 'Himalayan forests'
    },
    'Daboia_russelii': {
        'common_name': "Russell's Viper",
        'nepali_name': 'बाघ सर्प (Baghe sarpa), Suskar',
        'danger': 'Highly venomous',
        'habitat': 'Grasslands, farmlands'
    },
    'Dendrelaphis_tristis': {
        'common_name': 'Bronze-backed Tree Snake',
        'nepali_name': 'काँसे ढाडे सर्प (Kanse Dhade Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Trees, gardens'
    },
    'Eryx_johnii': {
        'common_name': 'Red Sand Boa',
        'nepali_name': 'दुईमुखे सर्प (Duimukhe Sarpa), बालुवा सर्प (Baluwa Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Deserts, scrublands'
    },
    'Gloydius_himalayanus': {
        'common_name': 'Himalayan Pit Viper',
        'nepali_name': 'भ्यागुते सर्प (Bhyagute Sarpa)',
        'danger': 'Venomous',
        'habitat': 'Himalayan forests'
    },
    'Indotyphlops_braminus': {
        'common_name': 'Brahminy Blind Snake',
        'nepali_name': 'अन्धो सर्प (Andho Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Soil, compost piles'
    },
    'Lycodon_aulicus': {
        'common_name': 'Common Wolf Snake',
        'nepali_name': 'ब्वाँसो सर्प (Bwanso Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Urban areas, forests'
    },
    'Naja_kaouthia': {
        'common_name': 'Monocled Cobra',
        'nepali_name': 'गोमन (Goman)',
        'danger': 'Highly venomous',
        'habitat': 'Wetlands, forests'
    },
    'Naja_naja': {
        'common_name': 'Indian Cobra',
        'nepali_name': 'गोमन (Goman)',
        'danger': 'Highly venomous',
        'habitat': 'Plains, forests'
    },
    'Oligodon_arnensis': {
        'common_name': 'Banded Kukri Snake',
        'nepali_name': 'कुक्रे सर्प (Kukre Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Agricultural lands, forests'
    },
    'Ophiophagus_hannah': {
        'common_name': 'King Cobra',
        'nepali_name': 'राज गोमन (Raj Goman), Kalinag, Kenwata',
        'danger': 'Highly venomous',
        'habitat': 'Rainforests'
    },
    'Oreocryptophis_porphyraceus': {
        'common_name': 'Beautiful Rat Snake',
        'nepali_name': 'रङ्गीचङ्गी धामन (Rangichangi Dhaman)',
        'danger': 'Non-venomous',
        'habitat': 'Mountain forests'
    },
    'Ovophis_monticola': {
        'common_name': 'Mountain Pit Viper',
        'nepali_name': 'अंध सर्प (Andho Sarpa), Gurube, Chhirbire Sarpa',
        'danger': 'Venomous',
        'habitat': 'Montane forests'
    },
    'Ptyas_mucosa': {
        'common_name': 'Indian Rat Snake',
        'nepali_name': 'धामन (Dhaman)',
        'danger': 'Non-venomous',
        'habitat': 'Fields, forests, human settlements'
    },
    'Python_molurus': {
        'common_name': 'Indian Rock Python',
        'nepali_name': 'अजिंगर (Ajingara)',
        'danger': 'Non-venomous',
        'habitat': 'Forests, grasslands'
    },
    'Rhabdophis_subminiatus': {
        'common_name': 'Red-necked Keelback',
        'nepali_name': 'रातो घाँटी सर्प (Rato Ghati Sarpa)',
        'danger': 'Mildly venomous',
        'habitat': 'Streams, wetlands, forests'
    },
    'Sibynophis_subpunctatus': {
        'common_name': 'Duméril’s Black-headed Snake',
        'nepali_name': 'कालो टाउको सर्प (Kalo Tauko Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Forests, plantations'
    },
    'Xenochrophis_piscator': {
        'common_name': 'Checkered Keelback',
        'nepali_name': 'पानी सर्प (Pani Sarpa)',
        'danger': 'Non-venomous',
        'habitat': 'Wetlands, rivers'
    }
}

snake_classes = list(SNAKE_INFO.keys())

# Load model models/efficientv2sv2.pth
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Load Model
try:
    model = timm.create_model('efficientnetv2_s', pretrained=False, num_classes=len(snake_classes))
    state_dict = torch.load('models/efficientv2sv2.pth', map_location=device)
    model.load_state_dict(state_dict, strict=True)
    model.to(device)
    model.eval()
    logger.info("EfficientNetV2-S model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {str(e)}")
    raise

# Transform for inference
transform = transforms.Compose([
    transforms.Resize((384, 384)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Haversine Formula
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Flask-Login User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/snakebite', methods=['GET'])
def snakebite():
    try:
        user_lat = request.args.get('lat', type=float, default=27.7172)
        user_lon = request.args.get('lon', type=float, default=85.3240)
        hospitals = Hospital.query.all()
        hospitals_with_distance = [
            {
                'id': h.id,
                'name': h.name,
                'phone': h.phone,
                'latitude': h.latitude,
                'longitude': h.longitude,
                'distance': haversine(user_lat, user_lon, h.latitude, h.longitude)
            }
            for h in hospitals
        ]
        hospitals_with_distance.sort(key=lambda x: x['distance'])
        return render_template('snakebite.html', hospitals=hospitals_with_distance, user_lat=user_lat, user_lon=user_lon)
    except Exception as e:
        logger.error(f"Error in snakebite route: {str(e)}")
        flash('An error occurred while loading hospitals.', 'danger')
        return render_template('snakebite.html', hospitals=[], user_lat=27.7172, user_lon=85.3240)

@app.route('/api/hospitals', methods=['GET'])
def get_hospitals():
    try:
        user_lat = request.args.get('lat', type=float, default=27.7172)
        user_lon = request.args.get('lon', type=float, default=85.3240)
        hospitals = Hospital.query.all()
        hospital_list = [
            {
                'id': h.id,
                'name': h.name,
                'phone': h.phone,
                'latitude': h.latitude,
                'longitude': h.longitude,
                'distance': haversine(user_lat, user_lon, h.latitude, h.longitude)
            }
            for h in hospitals
        ]
        hospital_list.sort(key=lambda x: x['distance'])
        return jsonify({'hospitals': hospital_list})
    except Exception as e:
        logger.error(f"Error in get_hospitals: {str(e)}")
        return jsonify({'error': 'Failed to fetch hospitals'}), 500

@app.route('/rescue', methods=['GET'])
def rescue():
    try:
        user_lat = request.args.get('lat', type=float, default=27.7172)
        user_lon = request.args.get('lon', type=float, default=85.3240)
        rescuers = Rescuer.query.all()
        rescuers_with_distance = [
            {
                'id': r.id,
                'name': r.name,
                'phone': r.phone,
                'latitude': r.latitude,
                'longitude': r.longitude,
                'distance': haversine(user_lat, user_lon, r.latitude, r.longitude)
            }
            for r in rescuers
        ]
        rescuers_with_distance.sort(key=lambda x: x['distance'])
        return render_template('rescue.html', rescuers=rescuers_with_distance, user_lat=user_lat, user_lon=user_lon)
    except Exception as e:
        logger.error(f"Error in rescue route: {str(e)}")
        flash('An error occurred while loading rescuers.', 'danger')
        return render_template('rescue.html', rescuers=[], user_lat=27.7172, user_lon=85.3240)

@app.route('/api/rescuers', methods=['GET'])
def get_rescuers():
    try:
        user_lat = request.args.get('lat', type=float, default=27.7172)
        user_lon = request.args.get('lon', type=float, default=85.3240)
        rescuers = Rescuer.query.all()
        rescuer_list = [
            {
                'id': r.id,
                'name': r.name,
                'phone': r.phone,
                'latitude': r.latitude,
                'longitude': r.longitude,
                'distance': haversine(user_lat, user_lon, r.latitude, r.longitude)
            }
            for r in rescuers
        ]
        rescuer_list.sort(key=lambda x: x['distance'])
        return jsonify({'rescuers': rescuer_list})
    except Exception as e:
        logger.error(f"Error in get_rescuers: {str(e)}")
        return jsonify({'error': 'Failed to fetch rescuers'}), 500

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    try:
        requests = Request.query.all()
        return render_template('dashboard.html', requests=requests)
    except Exception as e:
        logger.error(f"Error in dashboard route: {str(e)}")
        flash('An error occurred while loading requests.', 'danger')
        return render_template('dashboard.html', requests=[])

@app.route('/predict', methods=['POST'])
def predict():
    if 'snakeImage' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['snakeImage']
    try:
        img = Image.open(file).convert('RGB')
        img = transform(img).unsqueeze(0)
        with torch.no_grad():
            output = model(img)
            probabilities = torch.softmax(output, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
            species = snake_classes[predicted.item()]
            snake_info = SNAKE_INFO.get(species, {
                'common_name': 'Unknown',
                'nepali_name': 'Unknown',
                'danger': 'Unknown',
                'habitat': 'Unknown'
            })
        return jsonify({
            'species': species,
            'confidence': confidence.item() * 100,
            'common_name': snake_info['common_name'],
            'nepali_name': snake_info['nepali_name'],
            'danger': snake_info['danger'],
            'habitat': snake_info['habitat']
        })
    except Exception as e:
        logger.error(f"Error in predict route: {str(e)}")
        return jsonify({'error': 'Failed to process image'}), 500

@app.route('/submit_request', methods=['POST'])
def submit_request():
    try:
        data = request.form
        request_type = data.get('request_type', 'hospital')
        name = data.get('name')
        phone = data.get('phone')
        snake_species = data.get('snakeSpecies')
        location = data.get('location')
        lat = data.get('latitude')
        lon = data.get('longitude')

        if not name or not phone:
            return jsonify({'error': 'Name and phone are required'}), 400

        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
            except ValueError:
                lat, lon = None, None
        elif location and ',' in location:
            try:
                lat_str, lon_str = location.split(',')
                lat = float(lat_str.strip())
                lon = float(lon_str.strip())
            except ValueError:
                lat, lon = None, None

        new_request = Request(
            name=name,
            phone=phone,
            snake_species=snake_species if snake_species else 'Unknown',
            location=location if location else 'Not specified',
            request_type=request_type,
            latitude=lat,
            longitude=lon,
            timestamp=datetime.now(npt_tz)
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Request submitted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in submit_request: {str(e)}")
        return jsonify({'error': 'Failed to submit request'}), 500

@app.route('/delete_request/<int:request_id>', methods=['POST'])
@login_required
def delete_request(request_id):
    try:
        request_to_delete = Request.query.get(request_id)
        if not request_to_delete:
            return jsonify({'error': 'Request not found'}), 404
        db.session.delete(request_to_delete)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Request deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in delete_request: {str(e)}")
        return jsonify({'error': 'Failed to delete request'}), 500

@app.route('/info')
def info():
    return render_template('info.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

# Initialize Database
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

if __name__ == '__main__':
    app.run(debug=True)