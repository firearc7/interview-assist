# Software Requirements Specification (SRS)

## Table of Contents

- [1. Introduction](#1-introduction)
  - [1.1 Purpose](#11-purpose)
  - [1.2 Scope](#12-scope)
  - [1.3 Definitions, Acronyms, and Abbreviations](#13-definitions-acronyms-and-abbreviations)
  - [1.4 Overview](#14-overview)
- [2. Overall Description](#2-overall-description)
  - [2.1 Product Perspective](#21-product-perspective)
  - [2.2 Product Functions](#22-product-functions)
  - [2.3 User Classes and Characteristics](#23-user-classes-and-characteristics)
  - [2.4 Operating Environment](#24-operating-environment)
  - [2.5 Design and Implementation Constraints](#25-design-and-implementation-constraints)
  - [2.6 User Documentation](#26-user-documentation)
  - [2.7 Assumptions and Dependencies](#27-assumptions-and-dependencies)
- [3. System Features and Requirements](#3-system-features-and-requirements)
  - [3.1 Functional Requirements](#31-functional-requirements)
  - [3.2 Non-functional Requirements](#32-non-functional-requirements)
- [4. External Interface Requirements](#4-external-interface-requirements)
  - [4.1 User Interfaces](#41-user-interfaces)
  - [4.2 Hardware Interfaces](#42-hardware-interfaces)
  - [4.3 Software Interfaces](#43-software-interfaces)
  - [4.4 Communication Interfaces](#44-communication-interfaces)
- [5. Other Requirements](#5-other-requirements)
- [6. Appendix](#6-appendix)

---

## 1. Introduction

### 1.1 Purpose
The purpose of this Software Requirements Specification (SRS) is to define the requirements for the AI Interview Simulator, an interactive, AI-powered platform to help users prepare for job interviews by simulating realistic interview scenarios, providing customized questions, evaluating responses, and offering constructive feedback.

### 1.2 Scope
The AI Interview Simulator will provide:
- Text-based interview simulation
- Customizable interview environments (job role, job description, difficulty, number of questions)
- Performance evaluation and feedback
- Session history and progress tracking (for logged-in users)
- User authentication (username/password)

Potential future enhancements include voice interaction and more advanced customization.

### 1.3 Definitions, Acronyms, and Abbreviations
- **AI**: Artificial Intelligence
- **LLM**: Large Language Model
- **SRS**: Software Requirements Specification
- **UI**: User Interface

### 1.4 Overview
This document describes the system’s intended features, constraints, and interfaces, and serves as a basis for development and validation.

---

## 2. Overall Description

### 2.1 Product Perspective
The AI Interview Simulator is currently a standalone web application built with Streamlit. It utilizes Python modules for core functionalities like question generation, evaluation, and database interactions. The long-term vision includes refactoring into a microservice backend architecture.

### 2.2 Product Functions
- User authentication (signup, login, logout)
- Role/interview configuration (job role, description, difficulty, number of questions)
- Dynamic question generation
- Real-time answer evaluation
- Feedback delivery (immediate or delayed)
- Session management and progress tracking (view past interviews and results)
- Database storage for user accounts and interview history

Optional voice and video interaction are planned for future phases.

### 2.3 User Classes and Characteristics
- **Job Seekers**: Individuals preparing for interviews

### 2.4 Operating Environment
- Web-based application (Streamlit)
- Desktop and mobile browsers
- Cloud-based backend (AWS, GCP, or Azure)

### 2.5 Design and Implementation Constraints
- Current: Monolithic Streamlit application with modular Python components.
- Future: Microservice architecture.
- LLM integration via API (handled by backend modules).
- Compliance with accessibility standards (WCAG 2.1)

### 2.6 User Documentation
- User manual
- Online help and FAQs
- Screen reader compatibility
- Keyboard navigation
- Color contrast and adjustable text size

### 2.7 Assumptions and Dependencies
- Reliable internet connection
- Availability of LLM provider APIs
- Cloud infrastructure for deployment

---

## 3. System Features and Requirements

### 3.1 Functional Requirements

#### 3.1.1 Interview Setup
- Users can input job role and job description.
- Users can configure interview difficulty and number of questions.

#### 3.1.2 Interview Simulation
- System generates questions dynamically based on configuration.
- Real-time analysis of user responses.
- Support for free-form text input.
- Users can navigate between answered questions to review responses and feedback.

#### 3.1.3 Feedback System
- Real-time evaluation of answers during the interview.
- Scoring of responses.
- Identification of strengths and areas for improvement.
- Constructive feedback and sample ideal answers.
- Overall performance analysis after completing all questions.

#### 3.1.4 Session Management
- User accounts with signup and login.
- Session history storage for logged-in users.
- Ability to view past interview details and overall performance.
- Progress tracking through a dashboard displaying completed interviews.

#### 3.1.5 Advanced Features (Optional/Future)
- Voice interaction (speech input/output, tone analysis)
- Video analysis (facial expression, body language)
- Personalized coaching and improvement plans

### 3.2 Non-functional Requirements

#### 3.2.1 Performance
- Low response time
- Support for multiple users

#### 3.2.2 Security
- Encrypted data storage
- Privacy-preserving data handling

#### 3.2.3 Reliability
- High uptime
- Error logging

#### 3.2.4 Scalability
- Scalable architecture

---

## 4. External Interface Requirements

### 4.1 User Interfaces
- Streamlit-based responsive UI
- Progress indicators, feedback scoring, and dashboards

### 4.2 Hardware Interfaces
- None (web-based, standard devices)

### 4.3 Software Interfaces
- LLM provider API (abstracted by Python modules)
- Local SQLite database for user and interview data storage
- Authentication via username and password

### 4.4 Communication Interfaces
- HTTPS for all client-server and API communications

---

## 5. Other Requirements

- Agile development methodology, equipped with pair programming
- Unit, integration, and user acceptance testing
- Continuous integration and deployment
- Regular maintenance and updates

---

## 6. Appendix

### 6.1 Sample Question Banks
- Software Engineering, Product Management, Data Science etc.

### 6.2 Evaluation Rubrics
- Technical accuracy, communication, problem-solving, professional presence

### 6.3 Integration Specifications
- API documentation templates
- Data schema definitions
- Service interaction protocols

---

*This SRS is subject to review and revision as the project evolves.*
