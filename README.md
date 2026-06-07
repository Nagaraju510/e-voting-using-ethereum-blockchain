# E-Voting System Using Ethereum Blockchain

## Overview

The E-Voting System Using Ethereum Blockchain is a secure and transparent online voting platform designed to improve the reliability and integrity of elections. The system leverages blockchain technology to store votes securely, preventing vote tampering and ensuring transparency throughout the voting process.

The application integrates facial verification using OpenCV and CNN-based face recognition to authenticate voters before allowing them to cast their votes.

## Features

* Secure voter registration and authentication
* Face recognition-based voter verification
* Blockchain-based vote storage
* Prevention of duplicate voting
* Transparent and tamper-proof voting process
* Admin panel for managing parties and candidates
* Real-time vote counting and monitoring
* Decentralized architecture using blockchain principles

## Technologies Used

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Django

### Blockchain

* Ethereum Blockchain
* Smart Contracts

### Machine Learning

* OpenCV
* CNN (Convolutional Neural Network)

### Database

* MySQL

## System Modules

### Admin Module

* Admin Login
* Add Political Parties
* Add Candidate Details
* View Party Information
* Monitor Vote Counts

### User Module

* User Registration
* User Login
* Face Verification
* Cast Vote
* View Voting Status

## Workflow

1. User registers with personal details and face image.
2. Admin adds party and candidate information.
3. User logs in and completes facial verification.
4. System validates voter identity using CNN and OpenCV.
5. User selects a candidate and casts a vote.
6. Vote information is encrypted and stored in the blockchain.
7. Admin can monitor vote counts securely.

## Advantages

* High Security
* Transparency
* Decentralization
* Immutable Voting Records
* Prevention of Election Fraud
* Enhanced Voter Trust

## Hardware Requirements

* Processor: Pentium IV or Above
* RAM: 256 MB Minimum
* Hard Disk: 20 GB
* Webcam for Face Verification

## Software Requirements

* Windows 7/8/10
* Python
* Django
* OpenCV
* MySQL
* Ethereum

## Installation

### Clone Repository

```bash
git clone https://github.com/your-username/e-voting-using-ethereum-blockchain.git
cd e-voting-using-ethereum-blockchain
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Project

```bash
python manage.py runserver
```

Open browser and visit:

```text
http://127.0.0.1:8000/
```

## Future Enhancements

* Multi-factor Authentication
* Mobile Application Support
* Integration with Government ID Verification
* Enhanced Smart Contract Security
* Cloud Deployment

## License

This project is developed for educational and academic purposes.
