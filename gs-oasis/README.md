# GS Oasis Project

## Overview
GS Oasis is a simple web application built using HTML, CSS, and Python. This project serves as a personal website showcasing various features and information about the GS Oasis initiative.

## Project Structure
```
gs-oasis
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── script.js
├── templates
│   ├── base.html
│   ├── index.html
│   └── about.html
├── app.py
├── config.py
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd gs-oasis
   ```
3. Install the required dependencies. If using Flask, you can do this with:
   ```
   pip install Flask
   ```

## Running the Application
To run the application, execute the following command:
```
python app.py
```
The application will start on `http://127.0.0.1:5000/` by default.

## Features
- A homepage that introduces the GS Oasis project.
- An about page that provides more detailed information.
- Responsive design with custom styles defined in `static/css/style.css`.
- Client-side interactivity managed by `static/js/script.js`.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.