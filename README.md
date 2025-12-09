# Intrusion Detection System (IDS) Web Application

A production-ready Intrusion Detection System built with **FastAPI** backend and **React** frontend, featuring real-time network monitoring, ML-based attack detection, and a comprehensive dashboard. The system uses machine learning models to classify network flows and detect various types of attacks in real-time.

## 🚀 Features

- **Real-time Network Monitoring**: Live packet capture using Scapy with automatic flow aggregation
- **ML-Powered Detection**: Binary (SVM) and multiclass (Random Forest) attack classification
- **Attack Types Detected**: Port Scan, DoS/DDoS, Brute Force, Bot, Web Attack, and more
- **Interactive Dashboard**: Real-time metrics, charts, and flow visualization
- **WebSocket Support**: Live streaming of detected attacks with persistent connections
- **In-Memory Event Store**: Fast, lightweight storage for recent predictions (last 2000 events)
- **Interface Selector**: Dynamic network interface selection via UI dropdown
- **RESTful API**: Complete API for predictions, history, model insights, and system health
- **Flow Analyzer**: Manual flow analysis tool for testing individual flows

## 📁 Project Structure

```
IDS_System/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py             # Configuration settings (Pydantic)
│   │   ├── ml/                   # ML models and preprocessing
│   │   │   ├── predictor.py     # Model loading and prediction
│   │   │   └── preprocessing.py # Feature extraction and preprocessing
│   │   ├── routers/              # API route handlers
│   │   │   ├── predictions.py   # Prediction endpoints
│   │   │   ├── models.py         # Model info/metrics endpoints
│   │   │   ├── health.py         # Health check and sniffer control
│   │   │   └── stats.py          # Statistics endpoints
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   └── prediction.py
│   │   ├── services/             # Core services
│   │   │   ├── packet_sniffer.py # Scapy-based packet capture
│   │   │   └── flow_manager.py   # Flow aggregation and management
│   │   └── store/                # In-memory event store
│   │       └── prediction_store.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                # React page components
│   │   │   ├── Dashboard.jsx    # Overview dashboard
│   │   │   ├── LiveMonitoring.jsx # Real-time monitoring
│   │   │   ├── ModelInsights.jsx  # Model metrics and charts
│   │   │   └── FlowAnalyzer.jsx   # Manual flow analysis
│   │   ├── contexts/             # React contexts
│   │   │   └── WebSocketContext.jsx # Global WebSocket management
│   │   ├── api/                  # API client
│   │   │   └── client.js
│   │   └── config.js             # Frontend configuration
│   └── package.json
├── saved_models/                 # Trained ML models (required)
│   ├── binary_svm_model.pkl     # Binary classifier (attack vs benign)
│   ├── multiclass_rf_model.pkl  # Multiclass classifier (attack types)
│   ├── scaler.pkl               # StandardScaler for normalization
│   └── pca.pkl                  # PCA for dimensionality reduction
├── scripts/                      # Utility scripts
│   └── test_models.py            # Model testing script
├── Makefile                      # Development automation
├── ATTACK_GUIDE.md              # Detailed attack simulation guide
└── README.md
```

## 📋 Prerequisites

- **Python 3.8+** (tested with Python 3.13)
- **Node.js 18+** and npm (tested with Node.js 20.11.1)
- **macOS** (for Multipass VMs) or **Linux**
- **Root/Admin privileges** for packet capture (required for live monitoring)
- **Trained ML models** in `saved_models/` directory

## 🛠️ Installation

### Quick Setup (Recommended)

Use the Makefile for easy setup:

```bash
# Install all dependencies
make setup

# Or install separately
make install-backend
make install-frontend
```

### Manual Setup

#### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Verify models are in place:**
```bash
cd ..
ls saved_models/
# Should show: binary_svm_model.pkl, multiclass_rf_model.pkl, scaler.pkl, pca.pkl
```

#### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure API URL (optional):**
The default configuration in `src/config.js` points to `http://localhost:8000`. To change it, edit the file or set environment variables.

## 🚀 Running the Application

### Using Makefile (Recommended)

```bash
# Start both backend and frontend simultaneously
make dev

# Or start separately
make dev-backend    # Starts backend on http://localhost:8000
make dev-frontend   # Starts frontend on http://localhost:5173
```

### Manual Start

#### Start Backend

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Note:** On macOS/Linux, you may need root privileges for packet capture:
```bash
sudo uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

#### Start Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at **http://localhost:5173**

## 🌐 Network Interface Configuration

The IDS monitors network traffic on a specific interface. You can configure this in multiple ways:

### Method 1: Environment Variable (Recommended)

Create a `.env` file in the project root:
```bash
INTERFACE_NAME=bridge100
```

### Method 2: UI Dropdown (Dynamic)

1. Start the backend and frontend
2. Navigate to **Live Monitoring** page
3. Stop monitoring (if running)
4. Select your interface from the **"Change Interface"** dropdown
5. Start monitoring again

### Common Interface Names

- **`bridge0`** or **`bridge100`** - Multipass VMs on macOS
- **`en0`** - Primary Ethernet/WiFi interface (macOS)
- **`enp0s1`** - Common Linux network interface
- **`lo0`** - Loopback interface (localhost only)

### Finding Your Interface

**On macOS:**
```bash
ifconfig | grep -A 5 bridge
# Or list all interfaces
ifconfig | grep "^[a-z]"
```

**On Linux:**
```bash
ip link show
# Or
ifconfig -a
```

**Important:** Packet capture requires root/admin privileges. On macOS, you may need to:
- Run backend with `sudo`, or
- Grant Terminal/IDE network access in **System Preferences → Security & Privacy → Privacy → Full Disk Access**

## 🎯 Using the Application

### 1. Start the System

1. Start backend: `make dev-backend` or manually
2. Start frontend: `make dev-frontend` or manually
3. Open browser: http://localhost:5173

### 2. Live Monitoring

1. Navigate to **"Live Monitoring"** page
2. Select your network interface from the dropdown
3. Click **"Start Monitoring"**
4. Watch flows appear in real-time as network traffic is captured

### 3. Dashboard

- View overall statistics (total flows, attacks, attack ratio)
- See charts for attacks over time and attack type distribution
- Review recent flows table

### 4. Model Insights

- View model performance metrics (accuracy, precision, recall, F1-score)
- See confusion matrices for binary and multiclass models
- Understand model capabilities and limitations

### 5. Flow Analyzer

- Manually input flow features
- Get instant predictions for individual flows
- Test specific attack scenarios

## 🧪 Attack Simulation with Multipass VMs

For detailed attack simulation instructions, see **[ATTACK_GUIDE.md](ATTACK_GUIDE.md)**.

### Quick Start

1. **Install Multipass:**
```bash
brew install multipass  # macOS
```

2. **Create VMs:**
```bash
multipass launch --name attacker --cpus 2 --mem 2G --disk 10G
multipass launch --name victim --cpus 2 --mem 2G --disk 10G
```

3. **Get IPs:**
```bash
multipass list
```

4. **Install attack tools on attacker VM:**
```bash
multipass shell attacker
sudo apt update
sudo apt install -y nmap hping3 hydra
```

5. **Set up victim VM:**
```bash
multipass shell victim
sudo systemctl enable ssh
sudo systemctl start ssh
sudo useradd -m -s /bin/bash testuser
echo "testuser:password123" | sudo chpasswd
```

6. **Generate attacks:**
```bash
# From attacker VM
multipass shell attacker
nmap -sS -p 1-1000 192.168.64.3  # Replace with victim IP
```

7. **Monitor in IDS:**
   - Start monitoring in the Live Monitoring page
   - Watch attacks appear in real-time

See **[ATTACK_GUIDE.md](ATTACK_GUIDE.md)** for comprehensive attack examples and sequences.

## 📡 API Endpoints

### Health & System

- `GET /api/health` - System health check and sniffer status
- `GET /api/health/interfaces` - List available network interfaces
- `POST /api/health/sniffer/start` - Start packet sniffer
- `POST /api/health/sniffer/stop` - Stop packet sniffer
- `POST /api/health/sniffer/interface?interface=<name>` - Change network interface

### Predictions

- `POST /api/predictions/predict-flow` - Predict attack type for a single flow
- `GET /api/predictions/history?limit=100` - Get prediction history

### Statistics

- `GET /api/stats` - Get overall statistics (total flows, attacks, ratios)

### Models

- `GET /api/models/info` - Get model information (algorithms, classes)
- `GET /api/models/metrics` - Get model performance metrics

### WebSocket

- `WS /api/live` - Live stream of detected flows (connects automatically)

## 🖥️ Frontend Pages

### Dashboard
- **Overview statistics**: Total flows, attacks detected, attack ratio, most frequent attack type
- **Charts**: Attacks over time (line chart), attack type distribution (pie chart)
- **Recent flows table**: Last 10 detected flows with details

### Live Monitoring
- **Real-time flow table**: Live updates via WebSocket
- **Interface selector**: Dropdown to change network interface
- **Sniffer statistics**: Packets captured, processed, active flows
- **Filters**: Filter by all flows, attacks only, or specific attack type
- **Monitoring controls**: Start/stop monitoring buttons

### Model Insights
- **Binary model metrics**: Accuracy, precision, recall, F1-score, ROC AUC
- **Multiclass model metrics**: Per-class and overall metrics
- **Confusion matrices**: Visual representation of model performance
- **Model information**: Algorithm details and class descriptions

### Flow Analyzer
- **Manual flow input**: Form to enter flow features
- **Instant prediction**: Get attack classification and confidence scores
- **Feature validation**: Input validation and helpful error messages

## 🤖 Machine Learning Models

### Binary Classifier (SVM)
- **Algorithm**: Support Vector Machine with RBF kernel
- **Purpose**: Distinguish between benign traffic and attacks
- **Output**: `is_attack` (boolean) and `binary_confidence` (0-1)

### Multiclass Classifier (Random Forest)
- **Algorithm**: Random Forest with balanced class weights
- **Purpose**: Classify specific attack types
- **Classes**: `BENIGN`, `Bot`, `Brute Force`, `DDoS`, `DoS`, `Port Scan`, `Web Attack`
- **Output**: `attack_type` (string) and `class_probabilities` (dict)

### Preprocessing Pipeline
1. **Feature Extraction**: 70+ flow features (packet counts, sizes, timings, flags, etc.)
2. **StandardScaler**: Normalize features to zero mean and unit variance
3. **IncrementalPCA**: Dimensionality reduction (70 → 35 features, 99.3% variance retained)
4. **Prediction**: Binary classification first, then multiclass if attack detected

### Model Training
Models were trained on the **CICIDS2017** dataset with:
- **SMOTE** for handling class imbalance
- **Cross-validation** for robust evaluation
- **Feature selection** based on correlation analysis

## 🗄️ Data Storage

The system uses an **in-memory event store** (not a database):
- **Storage**: `collections.deque` with max length of 2000 events
- **Persistence**: Data is lost on backend restart (acceptable for demo/testing)
- **Performance**: Fast read/write operations, no I/O overhead
- **Location**: `backend/app/store/prediction_store.py`

## 🔧 Configuration

### Backend Configuration

Edit `backend/app/config.py` or create `.env` file:

```python
# Network Interface
INTERFACE_NAME=bridge100

# Flow Manager Settings
FLOW_IDLE_TIMEOUT=60  # seconds (flows expire after this idle time)
FLOW_BATCH_SIZE=10    # batch size for predictions

# Model Paths (relative to project root)
MODEL_DIR=saved_models
```

### Frontend Configuration

Edit `frontend/src/config.js`:

```javascript
export const API_BASE_URL = 'http://localhost:8000';
export const WS_BASE_URL = 'ws://localhost:8000';
```

## 🐛 Troubleshooting

### No Flows Appearing

1. **Check sniffer status:**
   - Look at "Sniffer Statistics" in Live Monitoring page
   - Verify "Packets Captured" is increasing
   - Check backend logs for errors

2. **Verify interface:**
   - Ensure correct interface is selected
   - Check interface exists: `ifconfig` or `ip link show`
   - Try different interface (bridge0, en0, etc.)

3. **Check permissions:**
   - Run backend with `sudo` if needed
   - On macOS: Grant network access in System Preferences

4. **Test packet capture:**
```bash
sudo tcpdump -i bridge100 -c 10
```

### WebSocket Not Connecting

1. Check browser console (F12) for errors
2. Verify backend is running on port 8000
3. Check CORS settings in `backend/app/config.py`
4. Ensure WebSocket URL is correct in `frontend/src/config.js`

### Models Not Loading

1. **Verify models exist:**
```bash
ls -la saved_models/
# Should show: binary_svm_model.pkl, multiclass_rf_model.pkl, scaler.pkl, pca.pkl
```

2. **Check file paths:**
   - Models should be in `saved_models/` directory at project root
   - Check `backend/app/config.py` for correct paths

3. **Check backend logs:**
   - Look for "✓ Models loaded successfully" message
   - Check for FileNotFoundError messages

### Interface Not Found

1. **List available interfaces:**
   - Use the dropdown in Live Monitoring page
   - Or check backend logs for available interfaces

2. **Update interface:**
   - Use UI dropdown (recommended)
   - Or update `.env` file: `INTERFACE_NAME=<interface>`
   - Or update `backend/app/config.py`

### Frontend Can't Connect to Backend

1. **Verify backend is running:**
```bash
curl http://localhost:8000/api/health
```

2. **Check CORS settings:**
   - Verify `CORS_ORIGINS` in `backend/app/config.py` includes frontend URL
   - Default includes `http://localhost:5173`

3. **Check API URL:**
   - Verify `API_BASE_URL` in `frontend/src/config.js`
   - Should be `http://localhost:8000`

## 🧪 Development

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest tests/  # If tests exist
```

### Code Structure

- **Backend**: FastAPI with async support, Pydantic for validation, Scapy for packet capture
- **Frontend**: React 18+ with Vite, TailwindCSS for styling, Recharts for visualization
- **ML**: scikit-learn models loaded via joblib
- **Storage**: In-memory event store using `collections.deque`

### Key Technologies

- **Backend**: FastAPI, Pydantic, Scapy, scikit-learn, joblib
- **Frontend**: React, Vite, TailwindCSS, Recharts, Axios
- **ML**: scikit-learn (SVM, Random Forest), StandardScaler, IncrementalPCA
- **Networking**: Scapy for packet capture, WebSocket for real-time updates

## 📚 Additional Documentation

- **[ATTACK_GUIDE.md](ATTACK_GUIDE.md)** - Comprehensive guide for attack simulation with Multipass VMs
- **API Documentation**: Interactive docs at http://localhost:8000/docs (when backend is running)

## 📝 Notes

- **Data Persistence**: The system uses in-memory storage. All data is lost on backend restart.
- **Root Privileges**: Packet capture requires root/admin privileges on most systems.
- **Model Requirements**: Trained models must be present in `saved_models/` directory.
- **Network Traffic**: The system captures and analyzes all traffic on the selected interface.

## 🤝 Contributing

This project is for educational and research purposes. Contributions are welcome!

## 📄 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

- **CICIDS2017 Dataset**: Models trained on the Canadian Institute for Cybersecurity Intrusion Detection Systems dataset
- **Scapy**: Network packet manipulation library
- **FastAPI**: Modern Python web framework
- **React**: JavaScript library for building user interfaces

---

**Built with ❤️ for network security research and education**
