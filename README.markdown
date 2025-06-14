# Smart Library System

This repository contains the implementation of a **Smart Library System** developed as part of my Distributed Systems course. The project evolves through four phases, transitioning from a monolithic application to a containerized microservices architecture.

## Project Overview
The Smart Library System manages library operations, including user management, book cataloging, and loan tracking. It is implemented in Python using FastAPI, SQLAlchemy, and PostgreSQL, with each phase demonstrating different architectural and deployment strategies.

## Phases

### Phase 1: Monolithic Application
- A single FastAPI application handling all functionalities (users, books, loans).
- Uses PostgreSQL for data storage and SQLAlchemy for ORM.
- Deployed locally for simplicity.

### Phase 2: Microservices Architecture
- Splits the monolithic application into three independent services:
  - **User Service**: Manages user related functionalities.
  - **Book Service**: Handles book cataloging and availability.
  - **Loan Service**: Tracks book borrowing and returns.
- Each service has its own FastAPI instance and PostgreSQL database.
- Services communicate via HTTP APIs.

### Phase 3: Reverse Proxy with Nginx
- Introduces Nginx as a reverse proxy to route requests to the appropriate microservice.
- Enhances scalability and load balancing.

### Phase 4: Containerization with Docker
- Containerizes each microservice (User, Book, Loan) using Docker.
- Uses `python:3.10-slim` base image for FastAPI services.
- Configures PostgreSQL to run on the host or in a container.

## Setup Instructions
1. **Prerequisites**:
   - Python 3.10+
   - PostgreSQL
   - Nginx (for Phase-3)
   - Docker (for Phase-4)

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/smart-library-system.git
   cd smart-library-system
   ```

3. **Phase-Specific Setup**:
   - **Phase 1**: Navigate to `Phase-1`, install dependencies (`pip install -r requirements.txt`), set up PostgreSQL and add your configurations to the .env file, and run `uvicorn main:app --port 8000`.
   - **Phase 2**: For each service in `Phase-2`, configure `.env` with `DATABASE_URL`, install dependencies, and run each service (e.g., `uvicorn app.main:app --port 8081` for UserService).
   - **Phase 3**: Configure Nginx in `Phase-3` to route to services, then start Nginx and microservices.
   - **Phase 4**: Navigate to each service in `Phase-4`, build Docker images (`docker build -t service-name:v1 .`), and run containers (e.g., `docker run -d -p 8081:8081 user-service:v1`).

4. **Environment Configuration**:
   - Create a `.env` file for each service with:
     ```plaintext
     DATABASE_URL=postgresql://postgres:your-password@host:5432/db_name
     ```
   - Ensure PostgreSQL is running and accessible.

## Technologies Used
- **Backend**: Python, FastAPI, SQLAlchemy
- **Database**: PostgreSQL
- **Containerization**: Docker
- **Reverse Proxy**: Nginx