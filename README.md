# CADodiles STEM Trivia Game

## Overview
CADodiles is an interactive STEM trivia game designed for 5th grade classrooms. The system combines a touchscreen interface with physical feedback to create an engaging, hands-on learning experience.

The project is powered by a Raspberry Pi Zero 2 WH and uses a Python-based application built with the Kivy framework. Students answer questions on the touchscreen, and correct answers trigger a physical response through a servo-driven dispensing mechanism and LED feedback.

---

## Features
- Touchscreen-based graphical user interface (Kivy)
- Singleplayer and multiplayer game modes
- Chapter/topic selection aligned with 5th grade STEM concepts
- Real-time feedback for correct and incorrect answers
- Servo-controlled dispensing mechanism
- LED-based visual feedback system

---

## Hardware Used
- Raspberry Pi Zero 2 WH  
- Waveshare 7” HDMI Touchscreen Display  
- MG90S Micro Servo Motor  
- WS2812B LED Strip  
- External power supply (USB power bank)

---

## Software
- Python 3  
- Kivy Framework  
- GPIO control libraries  

---

## Tools Used
- Kivy (Python UI framework)
- Raspberry Pi OS / Pi Imager
- Kivy UI Designer (used for prototyping interface layouts): https://labdeck.com/kivy-tutorial/kivy-ui-designer/

---

## File Structure

- `main.py` – main application and game loop  
- `config.py` – configuration settings  
- `hardware.py` – GPIO and hardware control  
- `translations.py` – text and UI strings  

---

## CAD Files

SolidWorks parts, assemblies, and exported 3D models are available in the following folder:

`Solidworks Files and 3D Models/`

### Contents:
- Native SolidWorks part (`.SLDPRT`) and assembly (`.SLDASM`) files  
- Exported 3D models for viewing and presentation  

These files document the mechanical design of the system and can be used for further modification, analysis, or replication.

---

## How It Works
1. User selects a game mode and topic  
2. A question is displayed on the touchscreen  
3. The user selects an answer  
4. The system evaluates the response:
   - Correct → servo dispenses a game piece + LED feedback  
   - Incorrect → on-screen feedback only  
5. Gameplay continues until completion  

---

## Setup Instructions

### 1. Flash OS
Use Raspberry Pi Imager to install Raspberry Pi OS onto a microSD card.

### 2. Install Dependencies
Install required Python libraries (Kivy, GPIO libraries).

### 3. Clone Repository
```bash
git clone https://github.com/skyomni/CADodiles-STEM-Game.git
