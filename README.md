# LAR_Messi - Autonomous TurtleBot Soccer Player  
*Precision Robotic Football System*

![Robotic Soccer Demo](./docs/media/robot_score.gif)  
*Real-time demonstration of the autonomous scoring system*

## 🏆 System Overview
An autonomous robotic platform that enables TurtleBot to play soccer through:

- **Computer Vision** - Real-time ball and goal detection
- **Path Planning** - Optimal scoring trajectory calculation
- **Precision Control** - Velocity-regulated movement system
- **Decision Making** - 12-state finite state machine

**Technology Stack**:  
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python) ![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green?logo=opencv) ![ROS](https://img.shields.io/badge/ROS-Noetic-purple?logo=ros) ![RealSense](https://img.shields.io/badge/RealSense-D435-red?logo=intel)

## 🗂️ Project Structure
LAR_Messi/

├── docs/    
│ ├── media/ # Demo videos and images  
│ └── README.md # This documentation
├── src/    
│ ├── main.py # Primary control system     
│ ├── motor_driver.py # Robot movement control   
│ ├── image_processor.py # Vision pipeline     
│ ├── scene_info.py # Detection data structure     
│ ├── search_engine.py # Scene analysis     
│ ├── visualizer.py # Debug visualization    
│ ├── hsv_filter.py # Color detection    
│ └── path_info.py # Navigation data   


## 🧩 Module Documentation

💻 Installation

# Clone repository
git clone https://github.com/Papouc/LAR_Messi
cd LAR_Messi

# Install dependencies
pip install -r requirements.txt

# Run program
python src/main.py

📊 System Architecture
mermaid

flowchart TD
    A[Camera Input] --> B[Ball Detection]
    A --> C[Goal Detection]
    B --> D[Path Planning]
    C --> D
    D --> E[Motor Control]

📝 Technical Report Requirements

    Problem Analysis: Computer vision challenges

    Solution Design: HSV filtering + path planning

    Implementation: Python/OpenCV pipeline

    Results: Success rate metrics

    Improvements: Error handling suggestions

✅ Code Quality

# Run PEP8 check
flake8 src/

# Expected output:
# 0 violations (with proper formatting)

👥 Team
Member  
Adam Hendrych,
David Horňáček,
Adam Hejtmánek

📅 Last Updated: {current_date}
🏷️ Version: {git_version}
