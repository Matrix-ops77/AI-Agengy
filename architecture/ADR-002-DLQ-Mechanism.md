# ADR-002: Dead-Letter Queue (DLQ) for Failed Invoices

**Date:** 2025-07-19

**Status:** Proposed

## Context

The invoice processing workflow can fail for various reasons, such as malformed documents, unexpected Document AI responses, or downstream service unavailability. If an invoice consistently fails after all retries, it is currently dropped from the system, making it difficult to track and reprocess.

## Decision

We will implement a Dead-Letter Queue (DLQ) mechanism using a dedicated Google Cloud Storage (GCS) bucket and a helper Cloud Function.

1.  **DLQ GCS Bucket:** A new GCS bucket, named `<project-id>-invoices-dlq`, will be created to store all failed invoices.
2.  **Workflow Error Handling:** The main `invoice-processing-workflow.yaml` will be wrapped in a global `try/except` block. The `except` block will catch any unhandled exceptions from the main processing steps.
3.  **Helper Cloud Function:** A new, HTTP-triggered Cloud Function named `move-to-dlq-helper` will be created.
    *   **Interface:** It will accept a JSON payload containing the original GCS event and the error message from the workflow.
    *   **Logic:** The function will move the failed invoice from the main processing bucket to the DLQ bucket and log a structured error message to Cloud Logging.
4.  **Integration:** The `except` block in the workflow will call this helper function, passing the necessary information.
5.  **Deployment:** The `cloudbuild.yaml` will be updated to include the creation of the DLQ GCS bucket and the deployment of the `move-to-dlq-helper` function.

## Consequences

**Positive:**
-   **Reliability:** No invoices will be silently lost. All failures will be captured for manual review.
-   **Auditability:** Provides a clear audit trail of all failed invoices.
-   **Separation of Concerns:** The DLQ logic is encapsulated in a dedicated function, keeping the main workflow cleaner.
-   **Reprocessing:** Failed invoices can be easily reprocessed by moving them from the DLQ bucket back to the main processing bucket.

**Negative:**
-   **Increased Infrastructure:** Adds one additional GCS bucket and one Cloud Function, leading to a minor increase in deployment complexity and cost.
-   **Manual Intervention:** Requires a manual process for reviewing and reprocessing failed invoices from the DLQ bucket. This is an acceptable trade-off for ensuring no data is lost.

---