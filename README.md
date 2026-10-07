# 🚁 AI Drone Rescue System (AIRSS)

An AI-powered drone surveillance system that detects survivors in real time using **YOLOv8**, captures their GPS location, sends emergency alerts, and displays live monitoring through a web dashboard.

The system is designed to assist rescue teams during natural disasters, search-and-rescue operations, and emergency response scenarios by automating survivor detection and location tracking.

---

## 📌 Project Overview

The AI Drone Rescue System processes a live drone/IP camera video stream and performs real-time human detection using the YOLOv8 object detection model.

Whenever a survivor is detected, the system:

- Detects people in the live video feed
- Draws bounding boxes around detected survivors
- Captures a screenshot of the detected frame
- Retrieves the GPS location of the drone/camera
- Converts GPS coordinates into a readable address
- Sends an automated email alert with survivor details
- Displays detection information on a live monitoring dashboard

The system automates survivor detection, location mapping, and alert generation, enabling faster situational awareness during search and rescue operations.

---

# ✨ Features

- Real-time survivor detection using YOLOv8
- Live drone/IP camera video processing
- Automatic GPS location retrieval
- Reverse geocoding for readable addresses
- Screenshot capture of detected survivors
- Email notification system
- Live web dashboard
- Detection logging
- Multi-threaded video processing
- Shared state management for smooth communication between modules

---

# 🛠 Tech Stack

## Programming Language

- Python 3

## Artificial Intelligence

- YOLOv8
- Ultralytics
- OpenCV

## Backend

- Flask

## Frontend

- HTML
- CSS
- JavaScript

## Libraries

- OpenCV
- Ultralytics
- NumPy
- Flask
- Requests
- Geopy
- Pyttsx3
- Threading
- Queue
- Dotenv

---

# 📂 Project Structure

```
AI-Drone-Rescue-System
│
├── main.py
├── main_v2.py
├── detector.py
├── gps_mapper.py
├── alert.py
├── dashboard.py
├── shared_state.py
├── config.py
├── requirements.txt
│
├── templates/
│     └── dashboard.html
│
├── static/
│
└── README.md
```

---

# ⚙️ System Workflow

```
Live Drone/IP Camera Stream
            │
            ▼
     Frame Acquisition
            │
            ▼
      YOLOv8 Detection
            │
            ▼
 Detect Survivors (Person Class)
            │
            ▼
 Draw Bounding Boxes
            │
            ▼
 Capture Screenshot
            │
            ▼
 Retrieve GPS Coordinates
            │
            ▼
 Reverse Geocoding
            │
            ▼
 Send Email Alert
            │
            ▼
 Update Dashboard
```

---

# 🧠 Algorithm

1. Initialize the YOLOv8 model.
2. Connect to the drone/IP camera video stream.
3. Continuously capture video frames.
4. Resize frames for faster inference.
5. Perform YOLOv8 object detection.
6. Filter detections belonging to the **Person** class.
7. Count detected survivors.
8. Draw bounding boxes and confidence scores.
9. Capture a screenshot of the detection.
10. Retrieve GPS coordinates from the camera/drone.
11. Convert coordinates into a readable location.
12. Send an email alert containing survivor information.
13. Update the live dashboard with detection details.
14. Repeat until the video stream stops.

---

# ⚙️ Installation

Clone the repository

```bash
git clone https://github.com/Muskangarg05/AI-Drone-Rescue-System.git
```

Navigate to the project directory

```bash
cd AI-Drone-Rescue-System
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file with the required configuration.

Run the project

```bash
python main.py
```
---

## 📸 Sample Output

The system provides:

- Real-time annotated video feed
- Survivor count
- Bounding boxes with confidence scores
- GPS coordinates
- Human-readable location
- Detection screenshots
- Email notifications
- Live dashboard updates
  
# 📈 Future Enhancements

- Multi-drone support
- Cloud deployment
- Mobile application
- SOS notification system
- WhatsApp/SMS alerts
- Face recognition
- Rescue route optimization
- Object tracking (DeepSORT/ByteTrack)
- Model optimization using TensorRT
- Integration with emergency response systems

---

## 👩‍💻 Author

**Muskan Garg**

AI & Machine Learning Student

- GitHub: https://github.com/Muskangarg05
- LinkedIn: www.linkedin.com/in/muskan-garg-41a077381

## 📄 License

This project is intended for educational and research purposes.
