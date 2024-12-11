# BUMP - Basic Uptime Monitoring Program

## Overview
BUMP is a locally-hosted application for monitoring the availability of web resources. It was developed as a learning project to gain experience with Python, front-end technologies (HTML, CSS, JavaScript), and the pywebview library. While functional, this tool is not intended to replace professional or cloud-hosted monitoring solutions.

### Disclaimer
This project is provided as-is, primarily as a demonstration of learning and experimentation. For real-world uptime monitoring, better alternatives are available.

## Features
- Monitor the availability of web resources.
- Locally-hosted, with no dependencies on external services.
- Evaluate response times and validate content against predefined conditions.
- Can send toast, email and email-to-SMS alerts of status changes.
- Maintain a history of different statuses and events.
- Displays a timeline and history logs per monitored resource.

## Quick Start and Demo
BUMP is easy to use, with a simple installation process and intuitive interface. This section will include:
- **Screenshots**: Visuals showcasing the app's main features.
- **Video Walkthrough**: A quick overview of BUMP in action.

*(Content pending)*

## Stack
BUMP is built using a combination of technologies designed to provide a simple but functional uptime monitoring solution:
- **Backend**: Python, with a lightweight Bottle server.
- **Frontend**: Raw HTML, CSS, and JavaScript (no frameworks like React or Angular).
- **Desktop Integration**: Pywebview for a seamless GUI experience within a locally-hosted application.

## Project Structure
The project is organized into a clear folder hierarchy to separate concerns and maintain modularity:
- **`src/app.py`**: Entry point of the application.
- **`src/common/`**: Core modules and utility functions.
- **`src/frontend/`**: Frontend assets and logic for the graphical interface.
- **`src/monitor/`**: Modules and classes related to monitoring web resources.
- **`src/queries/`**: Implementations of different query types and result processing.
- **`./assets/`**: Icons, fonts, and other static assets.
- **`./config/`**: Application settings stored in YAML format.
- **`./data/`**: App-generated configurations such as monitoring setups and historical results.
- **`./logs/`**: Log files generated during runtime.

## Dependencies
BUMP’s dependencies are managed through a `requirements.txt` file for easy setup. The main dependencies include:
- **Backend**: Bottle, Pythonnet, and Playwright.
- **Frontend/GUI**: Pywebview, Plyer, and Pystray.
- **Utility Libraries**: ruamel.yaml for configuration handling, pathvalidate for validation, and more.

For a full list of dependencies and their versions, refer to the `requirements.txt` file in the root directory.

## Installation
To get started with BUMP, you have two options:

1. **From Source**:
   - Ensure Python is installed on your system.
   - Install the required dependencies using:
     ```
     pip install -r requirements.txt
     ```
   - Launch the application by running:
     ```
     python src/app.py
     ```

2. **Pre-Bundled Executable**:
   - Download the pre-bundled executable created with PyInstaller.
   - Simply run the executable to start the application.

## Status and Contributions
BUMP is provided as-is with no plans for future development. 

- **Contributions**: This project was created as a learning exercise and is not actively maintained. Contributions are not expected.  
- **Support**: Use this software as-is, with no guarantees or active support. It is not intended for production or critical use cases.
- **Future Plans**: The current version represents the final state of this project. While it could theoretically be adapted into a hosted solution by removing the GUI, there are no current intentions to pursue this idea, as better alternatives already exist.


## License
This project is licensed under the MIT License. See the LICENSE file for details.

Here's an even more neutral version:

## Acknowledgments
This project was made possible by the following libraries and tools:
- **Pywebview**: For the GUI framework.
- **Bottle**: For the backend server.
- **Playwright**: For web-based monitoring tasks.
- **ruamel.yaml**: For handling configurations.
- **PyInstaller**: For creating the standalone executable.
