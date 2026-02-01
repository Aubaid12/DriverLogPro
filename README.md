# DriverLog Pro - Automated Trip Planner & Compliance

## 📌 Project Overview
**DriverLog Pro** is a specialized logistics application designed to automate trip planning and **Hours of Service (HOS)** compliance for truck drivers. It calculates safe, legal driving schedules based on FMCSA regulations (including the 70-hour/8-day rule) and generates fully compliant, printable daily log sheets.

### Key Features
- **Smart Trip Scheduling**: Automatically inserts mandatory breaks (30-min), sleeper berth splits (10-hr), and cycle restarts (34-hr) into the itinerary.
- **FMCSA Compliance Engine**: Enforces strict adherence to US Department of Transportation rules, preventing violations before they happen.
- **Interactive Route Map**: Visualizes the route with dynamic markers for **Start**, **Pickup**, and **Dropoff** locations using real-world routing geometry.
- **Automated Log Generation**: Produces a standardized, government-compliant PDF logbook (multi-page) populated with:
    - 24-hour Grid Graph.
    - Calculated Duty Totals (Off/Sleeper/Driving/On).
    - Auto-filled Remarks (Location, Activity, State).
    - Header Details (Carrier, Mileage, Dates).
- **PDF Export**: One-click download of the complete trip logbook.

---

## 🛠️ Technology Stack
- **Backend**: Python 3, Django, Django REST Framework.
- **Frontend**: React 19, Vite, Leaflet (Maps).
- **Compliance Logic**: Custom Python engine implementing FMCSA Part 395 regulations.
- **PDF Engine**: `Pillow` (PIL) for high-fidelity grid rendering and `ReportLab/PyPDF` logic for document assembly.
- **Routing**: Integration with OSRM (Open Source Routing Machine) and Nominatim (Geocoding).

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js & npm

### 1. Backend Setup (Django)
The backend manages the compliance logic and API.

1. **Activate Virtual Environment:**
   ```powershell
   .\venv\Scripts\Activate
   ```
   *(Or just run using the venv python directly: `.\venv\Scripts\python`)*

2. **Install Dependencies (if needed):**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the Server:**
   ```powershell
   python backend\manage.py runserver
   ```
   *Server will start at: `http://127.0.0.1:8000/`*

### 2. Frontend Setup (React)
The frontend provides the interactive planner interface.

1. **Navigate to Frontend Directory:**
   ```powershell
   cd frontend
   ```

2. **Install Dependencies:**
   ```powershell
   npm install
   ```

3. **Start Development Server:**
   ```powershell
   npm run dev
   ```
   *App will be accessible at: `http://localhost:5173/`*

---

## 📖 Usage Guide
1. **Enter Trip Details**: Input your "Start Location", "Pickup", and "Dropoff" cities (e.g., "Chicago, IL" to "Miami, FL").
2. **Set Current Status**: Input your "Cycle Used" hours to test compliance logic (e.g., enter `65` to force a cycle restart).
3. **Generate Plan**: Click the button to calculate the legal itinerary.
4. **View Results**:
    - **Itinerary**: Step-by-step compliant schedule.
    - **Map**: Visual route with markers.
    - **Logs**: Preview of the generated daily logs.
5. **Export**: Click **"Download Full Logs (PDF)"** to save the official record.

---

## 🧪 Testing
The project includes an automated test suite to verify HOS rules:
```powershell
.\venv\Scripts\python test_api.py
```
*(Confirms API connectivity, PDF generation, and itinerary logic)*

---

## 📄 License
Educational / Assessment Project. Uses OpenStreetMap data under ODbL.
