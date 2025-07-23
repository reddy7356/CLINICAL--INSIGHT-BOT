# EPIC FHIR Integration Guide for Clinical Insight Bot

This guide walks you through connecting the Clinical Insight Bot to EPIC's health system using SMART on FHIR APIs to automatically extract patient data for anesthesia planning.

## Overview

EPIC provides FHIR R4 APIs that allow third-party applications to access patient data through the SMART on FHIR framework. This integration enables:

- **Automated Data Extraction**: Pull patient data directly from EPIC EHR
- **Real-time Insights**: Process current patient information for anesthesia planning  
- **Standardized Access**: Use industry-standard FHIR APIs
- **Secure Authentication**: OAuth 2.0 with SMART on FHIR

## Prerequisites

### 1. EPIC Developer Account
- Sign up for an **Epic on FHIR account** at [fhir.epic.com](https://fhir.epic.com)
- Register your application in the Epic on FHIR website
- Obtain your OAuth client ID (and secret if confidential client)

### 2. Application Registration
When registering your app, you'll need:
- **Application Name**: "Clinical Insight Bot" or your preferred name
- **Application Type**: Patient-facing or Provider-facing
- **FHIR Specification**: R4
- **Redirect URI**: `http://localhost:8080/callback` (for testing)
- **Launch URL**: Your application's launch endpoint (if EHR-launched)
- **Scopes**: Patient data access scopes

### 3. Python Dependencies
```bash
pip install requests
```

## Setup Instructions

### Step 1: Configure Environment Variables

```bash
# Set your EPIC credentials
export EPIC_CLIENT_ID="your-client-id-from-epic"
export EPIC_CLIENT_SECRET="your-client-secret"  # If confidential client
export EPIC_FHIR_URL="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
```

### Step 2: Basic Integration Example

```python
from epic_integration import EpicFHIRClient, start_oauth_flow
import os
import json

# Initialize with your credentials
client_id = os.getenv('EPIC_CLIENT_ID')
fhir_url = os.getenv('EPIC_FHIR_URL')

# Start OAuth flow
client, state = start_oauth_flow(client_id, fhir_url)

# After user authorization, exchange code for token
authorization_code = "code-from-oauth-callback"
token_response = client.exchange_code_for_token(authorization_code)

# Get clinical insights for a patient
insights = client.get_clinical_insights(patient_id="12345")
print(json.dumps(insights, indent=2))
```

## FHIR Scopes and Permissions

### Required Scopes
The integration requests the following FHIR scopes:

```python
scopes = [
    'patient/Patient.read',           # Patient demographics
    'patient/Observation.read',       # Lab values, vitals
    'patient/Condition.read',         # Diagnoses, comorbidities
    'patient/MedicationRequest.read', # Current medications
    'patient/AllergyIntolerance.read',# Allergies
    'patient/Procedure.read',         # Surgical history
    'patient/DiagnosticReport.read',  # Lab reports
    'patient/DocumentReference.read', # Clinical documents
    'patient/Immunization.read',      # Vaccination history
    'patient/Goal.read',              # Care goals
    'openid',                        # OpenID Connect
    'fhirUser',                      # FHIR user resource
    'online_access'                  # Refresh tokens
]
```

### Scope Meanings
- **`patient/*`**: Access to specific patient resources in context
- **`user/*`**: Access to resources the authenticated user can see
- **`system/*`**: Server-to-server access (backend services)

## Authentication Flow

### 1. Patient-Facing Apps (MyChart/Patient Portal)
```python
# Initialize client
client = EpicFHIRClient(
    client_id="your-client-id",
    fhir_base_url="https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
)

# Get authorization URL
auth_url, state = client.get_authorization_url()

# User visits auth_url and authorizes app
# Callback receives authorization code
# Exchange code for token
token_response = client.exchange_code_for_token(auth_code)
```

### 2. Provider-Facing Apps (EHR Launch)
```python
# For EHR-launched apps with launch context
launch_context = "launch-id-from-ehr"
auth_url, state = client.get_authorization_url(launch_context=launch_context)
```

## EPIC FHIR Endpoints

### Common EPIC FHIR Base URLs:
- **Sandbox**: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
- **Production**: Varies by organization (provided by Epic Community Member)

### Well-Known Endpoints:
- **SMART Configuration**: `{base_url}/.well-known/smart-configuration`
- **Authorization**: Discovered from SMART configuration
- **Token**: Discovered from SMART configuration

## Data Extraction and Processing

### Retrieved FHIR Resources
The integration automatically extracts:

1. **Patient Demographics**
   - Name, age, gender, birth date
   - Contact information

2. **Observations** 
   - Laboratory values (Hgb, platelets, creatinine, etc.)
   - Vital signs (BP, HR, O2 sat)
   - Clinical measurements

3. **Conditions**
   - Active diagnoses
   - Past medical history
   - Comorbidities relevant to anesthesia

4. **Medications**
   - Active prescriptions
   - Medication history
   - Dosages and frequencies

5. **Allergies**
   - Drug allergies
   - Environmental allergies
   - Reaction descriptions

6. **Procedures**
   - Surgical history
   - Procedure dates and descriptions

7. **Immunizations**
   - Vaccination history
   - Dates and types

### FHIR to Text Conversion
The integration converts FHIR resources to structured text:

```python
patient_data = client.get_patient_data("patient-123")
patient_text = client.convert_fhir_to_text(patient_data)

# Example output:
"""
PATIENT: Jane Smith
AGE: 68 years old
GENDER: Female

PAST MEDICAL HISTORY:
- Hypertension
- Type 2 Diabetes Mellitus
- Chronic kidney disease

MEDICATIONS:
- Metoprolol 50mg BID
- Insulin glargine 24 units nightly
- Lisinopril 10mg daily

ALLERGIES:
- Penicillin (rash)
- Morphine (nausea)

LABORATORY VALUES:
Hemoglobin: 11.8 g/dL
Creatinine: 1.4 mg/dL
Platelets: 245 K/uL
"""
```

## Security and Compliance

### HIPAA Compliance
- **Encryption**: All API calls use HTTPS/TLS 1.2+
- **Authentication**: OAuth 2.0 with SMART on FHIR
- **Access Controls**: Scope-limited access to patient data
- **Audit Trails**: Requests are logged by EPIC

### Best Practices
1. **Store Tokens Securely**: Never log or expose access tokens
2. **Token Refresh**: Handle token expiration gracefully
3. **Error Handling**: Implement robust error handling for API failures
4. **Rate Limiting**: Respect EPIC's API rate limits
5. **Data Minimization**: Only request needed scopes and data

## Testing and Development

### EPIC Sandbox Environment
- **Sandbox URL**: https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/
- **Test Patient Data**: Use EPIC's sample patients
- **No PHI**: Sandbox contains synthetic data only

### Test Patient IDs
EPIC provides test patients for development:
- Check EPIC on FHIR documentation for current test patient IDs
- Use sandbox environment for all development and testing

### Validation Checklist
- [ ] OAuth flow completes successfully
- [ ] FHIR resources are retrieved without errors
- [ ] Patient data converts to text format correctly
- [ ] Clinical Insight Bot processes the text
- [ ] Output includes anesthesia-relevant information
- [ ] Error handling works for various scenarios

## Production Deployment

### Environment Configuration
```bash
# Production environment variables
export EPIC_CLIENT_ID="prod-client-id"
export EPIC_CLIENT_SECRET="prod-client-secret"
export EPIC_FHIR_URL="https://production-epic-fhir-url/api/FHIR/R4/"
export ENCRYPTION_KEY="your-encryption-key-for-tokens"
```

### Epic Community Member Requirements
To use your app in production, Epic Community Members must:
1. Download your app from Epic on FHIR website
2. Configure client credentials in their Epic environment
3. Enable appropriate security settings
4. Sign the open.epic API Subscription Agreement

## Support and Resources

### EPIC Documentation
- [Epic on FHIR Documentation](https://fhir.epic.com/Documentation)
- [SMART on FHIR Specification](https://hl7.org/fhir/smart-app-launch/)
- [OAuth 2.0 Guide](https://tools.ietf.org/html/rfc6749)

### Community Support
- [Epic on FHIR Support](https://fhir.epic.com/Home/Contact)
- [SMART on FHIR Community](https://chat.fhir.org/#narrow/stream/179170-smart)

## Common EPIC-Specific Considerations

### 1. App Registration Process
- Must register app on Epic on FHIR website
- Epic Community Members download your app using client ID
- Different process than Cerner's code.cerner.com

### 2. Client ID Management
- Production and non-production client IDs provided
- Each Epic Community Member downloads separately
- Client secrets managed per organization

### 3. FHIR Implementation
- Follows EPIC's specific FHIR implementation
- Some resource structures may differ from other vendors
- Test thoroughly with EPIC's sandbox

### 4. MyChart Integration
- Patient-facing apps integrate with MyChart
- Patients authenticate through MyChart credentials
- Supports patient portal workflows

---

**⚠️ Important Security Note**: This integration handles protected health information (PHI). Ensure your implementation complies with HIPAA, institutional policies, and applicable regulations. Always test thoroughly in sandbox environments before production deployment.

**🏥 EPIC-Specific Note**: EPIC integration requires coordination with Epic Community Members for production deployment. The sandbox environment is available for development and testing without requiring organizational approval. 