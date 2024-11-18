### Web Scraper Project
This project is a web scraper that extracts product information from [estore.ua](https://estore.ua/) and stores it in a MongoDB database. It uses Python for scraping and data processing, Celery for task scheduling, and Docker for containerization.

## Features
Scrapes product and category data from estore.ua.
Stores data in a MongoDB database.
Uses Celery for asynchronous task management.
Generates reports on database updates.

## Project Structure
```
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   ├── parse.py
│   └── tasks.py
├── data/
│   ├── categories.json
│   └── [scraped data files]
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
└── README.md
```

- app: Contains the application source code.
 - parse.py: Functions for parsing categories and    products from the website.
 - models.py: Data models for Product and Category.
 - main.py: Main application logic for initializing the database and running the parser.
 - tasks.py: Celery tasks for running the parser asynchronously.
 - config.py: Configuration settings loaded from the environment.
 - data: Stores the scraped data and categories.
 - requirements.txt: Python dependencies.
 - Dockerfile: Docker image configuration.
 - docker-compose.yml: Docker Compose configuration for orchestrating services.
 - .env: Environment variables configuration.

## Prerequisites
- Python 3.10
- Docker and Docker Compose
- Redis (if not using Docker)
- MongoDB (if not using Docker)

## Installation

### Clone the repository
```bash
git clone https://github.com/ch4zzy/estore-parsing
cd estore-parsing
```

### Set Up Environment Variables
Create a .env file in the root directory and add the following variables:

- Replace `<username>`, `<password>`, and `<cluster-url>` with your MongoDB credentials and cluster URL.
- If you are using a local MongoDB instance, your MONGO_URL might look like mongodb://localhost:27017/.
### Install Dependencies
If you prefer to run the project locally without Docker, set up a virtual environment and install the dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```


## Running the Project
### Using Docker Compose
The easiest way to run the project is using Docker Compose, which will set up the application, Celery worker, and Redis services.

Build and start the services:
```bash
docker-compose up --build
```

The Celery worker will automatically start and run the parse_shop_task defined in tasks.py.

### Running Locally
If you prefer to run the project locally without Docker:

Start a Redis server (required for Celery):
```bash
redis-server
``` 

Ensure your MongoDB server is running and accessible.

Run the Celery worker:
```bash
celery -A app.tasks worker --loglevel=info
```

Run the main application:

```bash
python app/main.py
```

### Notes
- The scraped data will be stored in the data directory and in your MongoDB database.
- The project uses Celery to schedule and run scraping tasks asynchronously.
- Reports are generated and saved in the data directory whenever the database is updated with new or changed product information.
- The project is configured to start the scraping task automatically when the Celery worker starts, as defined in app/tasks.py.