# Patient Dashboard Implementation Plan

This document outlines the strategy for implementing the Patient Dashboard and Timeline, focusing on a seamless integration at the root (`/`) of the application.

## 1. Objectives
*   Provide patients with a clear overview of their health data and wound history.
*   Render the dashboard at the root URL (`/`), dynamically switching based on user role.
*   Establish a foundation for future wound observations (size, state, photos).

## 2. Backend Implementation (server-wounds)

### 2.1. Patient Profile Endpoint
*   **Action**: Create `PatientMeView` at `/api/patient/me/`.
*   **Permissions**: Restrict access to authenticated users with the `Patient` role.
*   **Data Payload**:
    *   Basic info: Name, age (calculated from birth date), location.
    *   Metrics: Height, weight, smoking status, alcohol consumption.
    *   Comorbidities: List of linked ICD-11 codes and names.
    *   Assigned Specialists: Contact info of specialists assigned to the patient.

### 2.2. Future-Proofing Observations
*   **Observation Model**: Define a structure to store wound observations.
*   **Authorship**: Ensure both patients and specialists can create observations for the same wound.

## 3. Frontend Implementation (app-wounds)

### 3.1. Routing and Role Selection
*   **Root Component (`app/page.tsx`)**: Update the root page to act as a "Role Dispatcher".
    *   If user is `specialist` -> Render `SpecialistDashboard`.
    *   If user is `patient` -> Render `PatientDashboard` (Timeline).
*   **Middleware/Store**: Ensure `authStore` and `userStore` correctly identify and persist the user role after login.

### 3.2. Patient Timeline (Issue #104)
*   **Location**: `app/(patient)/timeline/page.tsx` (but also rendered via `/`).
*   **Components**:
    *   **Health Summary Card**: Quick view of metrics and comorbidities.
    *   **Timeline List**: Chronological list of past observations (placeholder for now).
    *   **Action Button**: "Report Wound Status" (Future functionality).

## 4. Maintenance and Testing (Issue #133)
*   **Management Command**: Convert the `cleanup_data.py` script into a native Django management command: `python manage.py clear_test_data`.
*   **Scope**: Delete all non-superuser records to allow clean testing cycles.

---

## Execution Strategy
1.  **Branching**: Create `feat/patient-me-api` (Backend) and `feat/patient-timeline` (Frontend).
2.  **Implementation**: Follow the surgical edit process for each component.
3.  **Verification**: Use local testing and existing `quickstart.py` infrastructure.
