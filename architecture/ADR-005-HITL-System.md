# ADR-005: Human-in-the-Loop (HITL) System for Data Correction

**Date:** 2025-07-19

**Status:** Proposed

## Context

Automated data extraction from Document AI is not always 100% accurate. To ensure the highest level of data quality for our users, we need a system that allows for human review and correction of low-confidence extractions.

## Decision

We will implement a Human-in-the-Loop (HITL) system that is integrated into our existing Web UI and backend API.

1.  **Confidence Scoring:** The `invoice-processing-workflow.yaml` will be modified to inspect the `confidence` score for each entity extracted by Document AI.
2.  **Status Field:** A new `status` column will be added to the `processed_invoices` table in BigQuery. This field will store the status of the invoice: `PROCESSED`, `REVIEW_REQUIRED`, or `VERIFIED`.
3.  **Workflow Logic:**
    *   If all key entities have a confidence score above a predefined threshold (e.g., 0.95), the invoice status will be set to `PROCESSED`.
    *   If any key entity's confidence score is below the threshold, the status will be set to `REVIEW_REQUIRED`.
4.  **HITL User Interface:**
    *   A new "Review Queue" page will be added to the Web UI.
    *   This page will display a list of all invoices with the `REVIEW_REQUIRED` status.
    *   When an invoice is selected, the UI will display an image of the original document alongside the extracted data in editable form fields.
5.  **Correction and Verification:**
    *   A human operator can review the data, make any necessary corrections, and submit the form.
    *   The backend API will receive the corrected data, update the corresponding record in BigQuery, and change the invoice status to `VERIFIED`.
6.  **Feedback Loop (Future):** The `VERIFIED` data can be used as a high-quality dataset for fine-tuning custom Document AI models, creating a continuous improvement loop.

## Consequences

**Positive:**
-   **Data Accuracy:** Significantly improves the accuracy and reliability of the final data.
-   **User Trust:** Builds user trust by providing transparency and control over the data extraction process.
-   **AI Improvement:** Creates a valuable dataset for future AI model improvements.
-   **Seamless Integration:** The HITL system is seamlessly integrated into the main user application, providing a unified user experience.

**Negative:**
-   **Increased Development Effort:** Requires additional development work on both the frontend and backend to build the review interface and the correction logic.
-   **Manual Effort:** Introduces a manual step into the process, which will require human operator time. This is a necessary trade-off for achieving high data accuracy.

---