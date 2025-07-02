# GS Oasis - Scam Detection and Education Platform

**GS Oasis** is a program designed to educate older individuals and others less confident with technology about common scams and how to identify them. It features a web-based interface that uses AI to analyse files, text messages, and URLs for potential threats. The system provides detailed insights on detected scams, explaining their impact and offering guidance on recognizing similar threats in the future. The platform is primarily developed in HTML, Java, and Python.


## Overview
GS Oasis is built to be an educational tool, providing users with:
- **AI-based Scanning**: Analyses files, text, and URLs to detect scams.
- **Educational Feedback**: Provides detailed explanations of scam types.
- **Interactive Quiz**: Reinforces learning through an educational quiz.
- **User Accounts**: Allows users to create accounts for managing their submissions and feedback.

It is designed to help users recognize threats and stay safe online.

## Features
- **File, URL, and Image Scanning**: Users can submit files, links, or images to be analyzed for potential scams.
- **AI Integration**: Uses AI via API to identify scams in submitted data.
- **Scam Identification Guidance**: Provides feedback to users on how to identify and avoid scams in the future.
- **Interactive Quiz**: Users can test their knowledge on scam detection.
- **User Authentication**: Users can create accounts, log in, and manage submissions.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python
- **Database**: MySQL (or another secure database) for user authentication and data storage
- **API Integration**: AI API for scam detection
- **OCR Tools**: To scan images and detect readable text or suspicious patterns

## Legal and Ethical Considerations
When developing **GS Oasis**, we ensure:
- **Data Privacy**: User data (username, password, email, uploaded content) is securely stored.
- **Ethical Coding**: We adhere to ethical coding standards, ensuring no exploitation of user data.
- **Open Source & Licensing**: We use open-source tools like GitHub Copilot and respect all relevant licensing agreements.
- **User Consent**: Users must accept the terms and conditions before interacting with the platform.

## Functional and Non-functional Requirements

### Functional Requirements
| Requirement | Description |
| ----------- | ----------- |
| File, URL, and Image Scanning | GS Oasis should process user-uploaded content to detect scams. |
| AI Integration | The system uses AI to analyze the content and provide feedback. |
| Complex Query Handling | GS Oasis handles user queries with AI-generated responses. |
| Limited Requests | Users can submit up to three files or URLs for analysis at a time. |
| User Accounts | Users can sign up, log in, and manage their data securely. |

### Non-functional Requirements
| Requirement | Description |
| ----------- | ----------- |
| Fast Response | GS Oasis aims for fast scanning and feedback. |
| Security | User accounts and data are stored securely. |
| User-friendly Interface | The platform is designed for non-tech-savvy users, with simple navigation and a clean layout. |
| Visual Appeal | The site should look professional and welcoming. |
| Terms and Conditions | Users must accept the terms before using the platform. |

## Implementation Method
The platform will be implemented using a phased strategy, utilizing a combination of HTML, CSS, JavaScript, and Python. 

### Development Process:
1. **Frontend**: Built using HTML for structure, CSS for styling, and JavaScript for interactivity.
2. **Backend**: Primarily Python for handling requests, integrating AI APIs, and managing database interactions.
3. **OCR Integration**: Using GitHub Copilot to assist with OCR tools for image analysis and detecting suspicious content.
4. **Database**: A MySQL database will store user data (e.g., usernames, emails) securely.

### AI Integration:
The AI system will scan user-submitted content (files, links, and images) via an OCR tool and determine whether the content is likely to be a scam. The AI will provide users with educational feedback on how to identify scams in the future.

### Tools and Libraries:
- **GitHub Copilot**: Assists in writing and optimizing code.
- **OCR Tools**: For analyzing images containing readable text or suspicious links.
- **Python Libraries**: For backend logic and API integration.
- **MySQL or equivalent database**: To handle user accounts and data securely.
