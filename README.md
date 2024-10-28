# WebWatch

**WebWatch** is a web vulnerability scanning application that helps users identify security issues on their websites. Built with Flask, Celery, and Nikto, it enables asynchronous domain scanning and generates detailed reports in XML and HTML formats.

Credits; this tool is created by [GRC Assure](https://grcassure.com/) and Maintainer by [Mafu.Tech](https://www.mufa.tech/) on behalf of [PlusClouds](https://plusclouds.com).

## Features

- **Automated Vulnerability Scanning**: Utilizes Nikto to scan domains for vulnerabilities.
- **Asynchronous Task Management**: Runs background scanning tasks with Celery and Redis.
- **Environment Configurations**: Supports both development and production setups via Docker and .env configurations.
- **Report Generation**: Provides XML and HTML report downloads for each scan.
- **API Access**: Exposes endpoints to initiate scans and retrieve results.

## Getting Started

### Prerequisites

Ensure the following software is installed:

- Docker
- Docker Compose

### Installation

1. **Clone the Repository**

   ```
   git clone https://github.com/plusclouds/webwatch.git
   cd webwatch
   ```

2. **Create a `.env` File**

   In the root directory, create an `.env` file to set up your environment variables. Example:

   ```
   ENVIRONMENT=development
   SECRET_KEY=your_secret_key_here
   ```

3. **Build and Start Services with Docker**

   To start the application, run:

   ```
   docker-compose up -d --build
   ```

   This will start the app, Celery worker, Redis, and Nginx services. By default:

   - The app is accessible via **Nginx** on port `8080`.
   - Internal services communicate within the Docker network.

### Usage

1. **Access the Application**

   Open your browser and go to http://localhost:8080.

2. **Initiate a Scan**

   - Enter the target domain in the input field and click "Start Scan."
   - A background task will start to scan the domain for vulnerabilities.

3. **Download Scan Results**

   - Once the scan is complete, download links for XML and HTML reports are available.
   - Reports can also be accessed via the API (see below).

### API Documentation

#### Start a Scan

**Endpoint**: `POST /`

**Description**: Starts a vulnerability scan for a specified domain.

**Payload**:

```
{
  "domain": "example.com"
}
```

#### Check Scan Status

**Endpoint**: `GET /status/<task_id>`

**Description**: Returns the current status of a scan.

#### Retrieve Scan Results

**Endpoint**: `GET /api/results/<domain>`

**Description**: Provides URLs to download the XML and HTML reports.

**Response**:

```
{
  "message": "Scan results found.",
  "xml_url": "http://localhost:8080/scan_results/domain_nikto_scan.xml",
  "html_url": "http://localhost:8080/scan_results/domain_nikto_report.html"
}
```

### Folder Structure

```
.
├── Dockerfile               # Dockerfile for building the app container
├── README.md                # Project documentation
├── app.py                   # Main application code
├── docker-compose.yml       # Docker Compose configuration
├── nginx-entrypoint.sh      # Entrypoint script for Nginx
├── nginx.conf.template      # Nginx configuration template
├── requirements.txt         # Python dependencies
├── scan_results/            # Directory for storing scan reports
└── templates/               # Directory for HTML templates
```

### Built With

- **Flask** - Web framework for Python
- **Celery** - Asynchronous task queue
- **Redis** - Message broker for Celery
- **Nikto** - Open-source web server scanner
- **Docker** - Containerization platform
