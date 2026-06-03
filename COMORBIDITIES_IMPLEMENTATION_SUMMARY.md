# CID-11 Comorbidities Implementation Summary

This document outlines the changes made to both the backend (`server-wounds`) and frontend (`app-wounds`) to support the new many-to-many relationship for CID-11 comorbidities.

---

## 🛠️ Backend Updates (`server-wounds`)

### 1. `feat: format names and add code column to comorbidities`
**Files Modified:** `models.py`, `serializers.py`, `views.py`, `load_cid11.py`
*   **Database Model:** Added a `code` column (`CharField`, allowing nulls) to the `Comorbidity` model to store standard ICD codes (e.g., "1A00").
*   **Data Loading:** Improved the `load_cid11.py` management command. It now strips leading dashes (`-`) and spaces from the CID-11 tree names for cleaner display, and it extracts the `Code` column from the CSV.
*   **Search API:** Updated `ComorbiditySearchView` (`/comorbidities/search/`) to filter across both the `name` and the new `code` fields using Django's `Q` objects.
*   **Serialization:** Updated `ComorbiditySerializer` to expose the `code` field to the frontend.

### 2. `feat: handle comorbidities on patient registration and add update endpoint`
**Files Modified:** `serializers.py`, `views.py`, `urls.py`
*   **Registration API:** Modified `PatientRegisterSerializer` to accept an array of strings (`comorbidities: string[]`). 
*   **Registration Logic:** Updated `SpecialistPatientRegisterView` to parse the `comorbidities` list of CID-11 URIs and automatically link the corresponding `Comorbidity` objects to the `Patient` model using `.set()`.
*   **Update API:** Created a brand new `SpecialistPatientUpdateView` (`/specialist/patient/update/<id>/`) to allow specialists to edit existing patient data (including their comorbidities) after initial registration.

### 3. `fix: include comorbidities in patient list response`
**Files Modified:** `views.py`
*   **Dashboard API:** Fixed `SpecialistPatientListView` to serialize and include the full `comorbidities` list in the response for each patient, rather than just returning their basic contact info.

---

## 🎨 Frontend Updates (`app-wounds`)

### 4. `feat: refactor registration payload and add async comorbidity search component`
**Files Modified:** `app/(specialist)/register-patient/page.tsx`, `components/AsyncComorbiditySearch.tsx`
*   **Payload Refactor:** Removed all legacy hardcoded booleans (`diabetes_type_1`, `hypertension`, etc.) from the `PatientRegistrationRequest` interface and the React form state. Replaced them with a strict `comorbidities: string[]` array.
*   **Async Search Component:** Created a new, reusable `AsyncComorbiditySearch` component. It features:
    *   Debounced API fetching to `/comorbidities/search/`.
    *   Clean rendering of results (`[Code] Name`).
    *   Interactive tag-based selection UI that allows adding and removing multiple comorbidities easily.
*   **Form Integration:** Swapped out the old checkbox grid with the new async search component in the registration form.

### 5. `fix: render comorbidities list properly in specialist dashboard`
**Files Modified:** `app/page.tsx`
*   **Dashboard Refactor:** Updated the patient card rendering logic on the specialist dashboard.
*   **Dynamic Badges:** Removed the hardcoded UI logic that checked legacy boolean flags. It now maps dynamically over the `p.comorbidities` array returned from the backend, rendering a `Badge` component for every assigned condition. Displays "Nenhuma informada" if the array is empty.

---

## 💾 Database State
To complete these changes, the following actions were performed on the database:
1. Migrated the database to add the new `code` column (`python manage.py migrate`).
2. Cleared the old comorbidity records.
3. Reloaded all 37,052 CID-11 entries with clean names and explicit ICD codes using the updated `load_cid11.py` script.
