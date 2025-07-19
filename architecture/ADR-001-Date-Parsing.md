# ADR-001: Robust Date Parsing for Invoice Data

**Date:** 2025-07-18

**Status:** Proposed

## Context

The `invoice-processing-workflow` extracts `invoice_date` and `due_date` fields from documents. These fields are strings and may come in various formats (e.g., "MM/DD/YYYY", "Month DD, YYYY", etc.) or be non-date strings. The target BigQuery table schema requires these columns to be of the `DATE` type. Directly inserting the raw string will cause the `tabledata.insertAll` step to fail if the format is not "YYYY-MM-DD" or if the value is not a valid date.

## Decision

We will create a dedicated, single-purpose Cloud Function named `date-parser-helper` to handle all date string parsing.

1.  **Technology:** Python 3.9+ with the `python-dateutil` library for robust parsing.
2.  **Interface:** The function will be an HTTP-triggered function that accepts a JSON payload `{ "date_string": "..." }`.
3.  **Output:** It will return a JSON payload `{ "parsed_date": "YYYY-MM-DD" }` on success, or `{ "parsed_date": null }` if the input string is empty, null, or cannot be parsed.
4.  **Integration:** The main `invoice-processing-workflow.yaml` will be modified to call this function for the `invoice_date` and `due_date` fields. The result will be used in the `record_to_insert` object.
5.  **Deployment:** The `deploy.py` script will be updated to include the deployment of this new Cloud Function.

## Consequences

**Positive:**
-   **Decoupling:** The complex parsing logic is removed from the workflow YAML, making it cleaner and easier to maintain.
-   **Robustness:** `python-dateutil` can handle a wide variety of date formats automatically.
-   **Data Integrity:** Ensures that only valid `DATE` types (or `NULL`) are sent to BigQuery, preventing insertion failures.
-   **Testability:** The function can be tested independently.

**Negative:**
-   **Increased Infrastructure:** Introduces one additional Cloud Function, leading to a minor increase in deployment complexity and cost.
-   **Latency:** Adds a small amount of latency due to the network call from the workflow to the Cloud Function. This is considered acceptable for this non-real-time workflow.

---