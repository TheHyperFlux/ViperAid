
# 🐍 ViperAid

**ViperAid** is a Flask-based web application that integrates modern deep learning models (EfficientNet, TIMM, PyTorch) into an intuitive interface for intelligent image processing and classification.  
It includes user authentication, a relational database, and a clean UI for easy deployment and testing of AI models.

---

## 🌟 Key Features

- 🔐 **Secure User Authentication** — Register, log in, and manage sessions via Flask-Login  
- 🧠 **AI-Powered Image Classification** — Uses EfficientNet and TIMM models with PyTorch backend  
- 🗂 **Database Integration** — Store user and inference data with SQLAlchemy ORM  
- 🖼 **Image Upload & Processing** — Upload images directly through the UI  
- ⚙️ **RESTful API Support** — Provides JSON endpoints for programmatic use  
- 🪶 **Lightweight Web Interface** — Built with Flask and Jinja2 templates  
- 📊 **Logging & Analytics** — Integrated logging for debugging and tracking  


## 🧰 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | HTML5, Jinja2 Templates, Bootstrap |
| **Backend** | Flask (Python) |
| **Database** | SQLAlchemy (SQLite/PostgreSQL/MySQL supported) |
| **AI Model** | PyTorch, torchvision, EfficientNet-PyTorch, timm |
| **Image Processing** | Pillow (PIL) |
| **Authentication** | Flask-Login, Werkzeug Security |

---

## 📁 Project Structure

```

ViperAid/
├── app.py                 # Main Flask app
├── dbverify.py            # Database integrity check
├── populate_db.py         # Populate database with initial data
├── requirements.txt       # Project dependencies
├── templates/             # Jinja2 HTML templates
├── instance/              # Instance folder (config/db)
└── .gitignore             # Git ignore rules

````

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/TheHyperFlux/ViperAid.git
cd ViperAid
````

### 2️⃣ Create and Activate a Virtual Environment

```bash
py -3.12 -m venv myvenv # install python version 3.12 for larger library support
source venv/bin/activate   # On Windows: Powershell: myvenv\Scripts\activate or Bash: source myvenv/Scripts/activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables - Optional

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
export SECRET_KEY='your_secret_key'
```

### 5️⃣ Initialize the Database

```bash
python populate_db.py
```

### 6️⃣ Run the Application

```bash
python app.py
```

Now open **[http://127.0.0.1:5000/](http://127.0.0.1:5000/)** in your browser 🎉

---

## 🧠 Model Information

ViperAid uses **EfficientNet** and **timm** pretrained models for efficient and accurate image classification.

* Models are initialized in PyTorch (`torch`, `torchvision`, `timm`, `efficientnet_pytorch`)
* Images are preprocessed with transformations (`torchvision.transforms`)
* Predictions are returned in real time after inference

---

## 🧪 Example Usage

1. Log in or register a new user
2. Upload an image (e.g., animal, object, or medical scan)
3. The model analyzes the image
4. Results (predicted class, confidence score, timestamp) are displayed on-screen or via JSON

---

## 📜 Requirements

See [`requirements.txt`](./requirements.txt).
Key dependencies include:

* Flask
* Flask-SQLAlchemy
* Flask-Login
* Werkzeug
* torch, torchvision
* timm
* efficientnet-pytorch
* Pillow

---

## 🛠 Logging & Error Handling

ViperAid uses Python’s built-in `logging` module to monitor application activity and capture errors.
Log files are automatically generated with timestamps for easy debugging.

---

## 🤝 Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m "Add new feature"`
4. Push to your fork: `git push origin feature/YourFeature`
5. Open a **Pull Request**

Please ensure code adheres to PEP8 and is well-documented.

---

## 🧾 License

This project is open-source and available under the **MIT License**.
You are free to use, modify, and distribute it with proper attribution.

---

## 📧 Contact

**Author:** [TheHyperFlux](https://github.com/TheHyperFlux)
For questions, suggestions, or collaboration, feel free to open an issue or reach out directly.

---

## 🧩 Acknowledgments

* [Flask](https://flask.palletsprojects.com/)
* [PyTorch](https://pytorch.org/)
* [timm](https://github.com/huggingface/pytorch-image-models)
* [EfficientNet-PyTorch](https://github.com/lukemelas/EfficientNet-PyTorch)
* Open-source contributors who made this possible ❤️

---

⭐ **If you find this project useful, consider starring the repo to show your support!**
