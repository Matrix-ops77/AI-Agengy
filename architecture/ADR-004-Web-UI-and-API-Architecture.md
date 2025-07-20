# ADR-004: Web UI and Backend API Architecture

**Date:** 2025-07-19

**Status:** Proposed

## Context

The invoice processing system currently lacks a user interface, making it inaccessible to non-technical users. To create a monetizable product, we need a secure, scalable, and user-friendly web application for invoice submission and data review.

## Decision

We will adopt a decoupled, modern web architecture consisting of a Single-Page Application (SPA) frontend and a containerized microservice backend.

1.  **Frontend (Web UI):**
    *   **Framework:** A modern JavaScript framework like **React** or **Vue.js** will be used to build the user interface.
    *   **Hosting:** The compiled static application will be hosted on **Firebase Hosting** to leverage its global CDN, automated SSL, and simple deployment process.
2.  **Backend (API):**
    *   **Framework:** A lightweight Python web framework, preferably **FastAPI**, will be used to build the backend API.
    *   **Containerization:** The API will be packaged as a **Docker** container.
    *   **Hosting:** The container will be deployed to **Google Cloud Run**, providing a serverless, scalable, and cost-effective hosting solution.
3.  **Authentication:**
    *   **Firebase Authentication** will be used for user identity and access management. It will handle user sign-up, login, and secure token generation. The backend API will validate these tokens to authorize requests.
4.  **API Gateway (Future):**
    *   We will plan to introduce **Google Cloud API Gateway** in a future iteration to provide a unified entry point to our API, enabling features like rate limiting, API key validation, and enhanced monitoring.

## Consequences

**Positive:**
-   **Scalability:** Both Firebase Hosting and Cloud Run are serverless and scale automatically to handle fluctuating traffic.
-   **Developer Experience:** The decoupled architecture allows frontend and backend development to proceed independently. FastAPI provides excellent performance and automatic API documentation.
-   **Security:** Firebase Authentication provides a robust and secure identity management solution.
-   **Cost-Effectiveness:** The serverless nature of Cloud Run and Firebase Hosting means we only pay for what we use.
-   **Maintainability:** The separation of concerns between the frontend and backend makes the system easier to understand, maintain, and evolve.

**Negative:**
-   **Increased Complexity:** This architecture involves more moving parts than a traditional monolithic application.
-   **Initial Setup:** Requires initial setup and configuration of Firebase, Cloud Run, and the CI/CD pipeline for both the frontend and backend. This is a one-time cost that pays off in the long run.

---