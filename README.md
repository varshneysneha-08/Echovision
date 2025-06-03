EchoVision

EchoVision is an intelligent assistant designed to help **visually impaired individuals** navigate safely and independently. By combining object detection, depth estimation, and voice-based feedback, it provides real-time situational awareness and path guidance using cutting-edge technologies.

## 🌟 Features

- 🎯 **Object Detection** – Detects and labels nearby objects using YOLOv9.
- 📏 **Depth Estimation** – Calculates the distance of each object from the user using an ONNX depth model.
- 🔊 **Voice Feedback** – Announces detected objects and their distances in real-time.
- 🧭 **Path Guidance** – Integrates with Azure Maps API to guide users through desired routes.
- ⚙️ **Web Interface** – A simple Django-based interface for route planning and visualization.

## 🚀 Technologies Used

- **Python**
- **Django**
- **YOLOv9**
- **ONNX Runtime**
- **Azure Maps API**
- **Machine Learning & Computer Vision**

## 🛠️ Getting Started

### Prerequisites

Make sure you have the following installed:

- Python 3.8+
- Django 4.x
- ONNX Runtime
- OpenCV
- Azure Maps Key (for route planning)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/varshneysneha-08/echovision.git
   cd echovision
