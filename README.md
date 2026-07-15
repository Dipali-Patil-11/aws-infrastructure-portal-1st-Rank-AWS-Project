# AWS Controller: Cloud Infrastructure Automation Portal

AWS Controller is an enterprise-grade, modern cloud infrastructure management portal built with Python, Flask, and the AWS SDK for Python (`boto3`). It provides a sleek, secure, and user-friendly web interface to monitor, manage, and provision AWS resources without directly accessing the complex AWS Management Console.

## 🚀 Key Features

*   **🔒 Secure STS Authentication:** Users authenticate with their own AWS Access Keys. The application uses AWS STS to instantly exchange long-term keys for temporary, 1-hour session tokens. **Long-term credentials are never logged or stored.**
*   **📊 Live Dashboard & Monitoring:** View real-time aggregated metrics across your AWS account, including running instances, active S3 buckets, and RDS databases. Includes live CloudWatch storage charts.
*   **💻 EC2 Instance Management:** Launch new instances (with automatic Amazon Linux AMI selection), start, stop, and terminate instances across any region.
*   **🪣 S3 File Management:** A modern card-based interface for managing S3 buckets. Includes drag-and-drop file uploads, secure presigned URL downloads, and inline file deletions—all isolated strictly to your own account.
*   **🗄️ Database Management:** Quickly view the status, size, and configurations of your Amazon RDS Instances and DynamoDB Tables.
*   **💰 Real-Time Cost Analysis:** Integrates directly with the AWS Cost Explorer API to fetch your actual unblended costs for the last 30 days, grouped by service. Generate and download CSV invoices directly from the portal.

## 🏗️ Architecture

The application is built on a scalable Blueprint architecture:
*   **Backend:** Python 3 + Flask + Boto3
*   **Frontend:** HTML5, Bootstrap 5, Vanilla JS, Chart.js, FontAwesome
*   **Security:** In-memory UUID-based session store, leveraging AWS STS for short-lived credential rotation.

## 📋 Prerequisites

To run this application locally, you will need:
*   Python 3.9 or higher
*   An active AWS Account
*   AWS Access Key ID and Secret Access Key (with permissions for EC2, S3, RDS, DynamoDB, CloudWatch, and Cost Explorer).

## 🛠️ Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/aws-controller.git
   cd aws-controller
   ```

2. **Create a virtual environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Portal**
   Open your browser and navigate to `http://127.0.0.1:5000`.

## 🔒 Security Notice
This application is designed with "Privacy First" principles. When you log in, your Access Key and Secret Key are sent directly to AWS STS. The resulting temporary credentials are held securely in your server's RAM for the duration of your session and are automatically destroyed when you log out or when the server restarts.

## 📂 Folder Structure
```text
AWS_Automation/
├── api/                  # Backend API routes (EC2, S3, RDS, DynamoDB, Cost, etc.)
├── screenshots/          # Folder for your project screenshots
├── static/               # CSS, JS, and image assets (Theme and Chart logic)
├── templates/            # HTML templates for the beautiful web UI
├── utils/                # Helper functions (AWS clients, logger)
├── app.py                # Main Flask application entry point
├── config.py             # Configuration and environment settings
├── requirements.txt      # Python package dependencies
└── session_store.py      # In-memory secure session management
```

## 📝 Suggested GitHub Info
*   **Repository Name:** `aws-cloud-controller` or `aws-infrastructure-portal`
*   **Description:** "A modern, secure cloud infrastructure automation portal built with Flask and Boto3. Features live AWS metric tracking, S3/EC2/RDS/DynamoDB management, and real-time Cost Explorer integrations."

## 📷 Screenshots
Drop your screenshots into the `screenshots/` folder and link them here to showcase your project!
*   `![Dashboard](screenshots/dashboard.png)`
*   `![S3 Management](screenshots/s3.png)`

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check.