# Wound Observations MVP - Implementation Plan

## 1. Objective
Implement an MVP for tracking patient wounds and their clinical evolution over time through chronological "Observations". This allows both specialists and patients to log wound status and specific clinical metrics.

**Note:** Photo capture and storage will be the final step, ensuring core data flows are stable first.

## 2. Data Architecture (Backend)

We will use a relational database structure with fixed fields. Choices match the exact strings, casing, and accentuation in the project documentation (`CICATRIZANDO.md`).

### 2.1. `Wound` Model
*   `patient`: ForeignKey to `Patient`
*   **Etiology (`etiology`):**
    *   Úlcera do pé diabético
    *   Lesão por pressão
    *   Úlcera venosa
    *   Úlcera arterial
    *   Ferida por trauma
    *   Ferida cirúrgica
    *   Queimadura
    *   Skin tear
    *   Fístula
    *   Ferida neoplásica
    *   Flebite
*   **Location (`location`):**
    *   Anterior do joelho
    *   Posterior do joelho
    *   Abaixo do joelho, região posterior
    *   Abaixo do joelho, região anterior
    *   Acima do maleolo medial
    *   Abaixo do maleolo medial
    *   Acima do maleolo lateral
    *   Abaixo do maleolo lateral
    *   Região calcaneana
    *   Dorso do pé
    *   Planta do pé
    *   Halux
    *   2ª Pododáctilo
    *   3ª Pododáctilo
    *   4ª Pododáctilo
    *   5ª Pododáctilo
*   `created_at`: DateTimeField
*   `is_healed`: BooleanField (Default: False)

### 2.2. `Observation` Model
*   `wound`: ForeignKey to `Wound`
*   `author`: ForeignKey to `WoundsUser`
*   `created_at`: DateTimeField
*   **Clinical Metrics:**
    *   `pain_level`: IntegerField (0 to 10)
    *   `exudate_amount`: Choices (Nenhum, Pouco, Médio, Muito)
    *   `exudate_type`: Choices (Seroso, Purulento, Sanguinolento, Serosanguinolento, Ausente)
    *   `tissue_type`: Choices (Cicatrizado, Epitelização, Granulação, Desvitalizado, Necrótico)
    *   `dressing_changes`: IntegerField (Quantidade de Trocas de Curativo por Dia)
    *   `periwound_skin`: Choices (Inchaço/Edema, Eritema menor que 2 cm, Eritema maior que 2 cm)
    *   `wound_edge`: Choices (Indefinidas, não visíveis claramente; Definidas, contorno claramente visível, aderidas, niveladas com a base da ferida; Bem definidas, não aderidas à base da ferida; Bem definidas, não aderidas à base, enrolada, espessada; Bem definidas, fibróticas, com crostas e/ou hiperqueratose.)
    *   `fever_24h`: BooleanField
*   **Notes:**
    *   `extra_notes`: TextField (Anotações extras)
    *   `patient_guidelines`: TextField (Orientações passadas ao paciente)
*   **Media (Implemented in Final Phase):**
    *   `image`: ImageField

## 3. API Endpoints
*   `POST /api/wounds/` - Register new wound (Specialist only).
*   `GET /api/wounds/?patient_id=<id>` - List wounds.
*   `POST /api/wounds/<id>/observations/` - Create observation (JSON initially, Multipart later).
*   `GET /api/wounds/<id>/observations/` - Chronological timeline.

## 4. Execution Phases

### Phase 1: Core Clinical Backend
*   Implement `Wound` and `Observation` models (without `image` field).
*   Create serializers and ViewSets.
*   Validate all choice fields against the strings above.

### Phase 2: Dashboard & Timeline UI
*   Add "Active Wounds" list to Specialist and Patient dashboards.
*   Create the "Wound Detail" screen with a vertical list of clinical observations.
*   Implement the API service layers in the frontend.

### Phase 3: Clinical Observation Form
*   Build the comprehensive `ObservationForm` component.
*   Ensure all dropdowns and validations work for text/numeric metrics.
*   Verify that both Patients and Specialists can submit and view these updates.

### Phase 4: Storage Infrastructure (Final Step)
*   Setup `django-storages` with S3/MinIO configuration.
*   Add the `image` field to the `Observation` model.
*   Update backend to handle file uploads.

### Phase 5: Capacitor Camera Integration
*   Integrate `@capacitor/camera` in the frontend.
*   Add photo capture, preview, and upload functionality to the `ObservationForm`.
