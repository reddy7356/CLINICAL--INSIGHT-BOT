# Cerner Authentication Setup Guide

## Phase 1: Developer Registration (No Admin Required)

### Step 1: Create CernerCare Account
1. **Visit**: https://code.cerner.com
2. **Click**: "Sign Up for CernerCare account"
3. **Fill out**:
   - Email address
   - Password
   - Name and organization
   - Agree to terms

### Step 2: Register Your Application
1. **Login** to code.cerner.com
2. **Navigate**: "My Apps" → "Register a New App"
3. **Configure Application**:
   ```
   Application Name: Clinical Insight Bot
   Application Type: Patient (for patient-facing) OR Provider (for EHR-embedded)
   FHIR Specification: R4
   Application Privacy: Public (for most use cases)
   Redirect URI: http://localhost:8080/callback
   Launch URI: http://localhost:8080/launch (if EHR-launched)
   ```

### Step 3: Get Your Credentials
After registration, you'll receive:
- **Client ID**: Public identifier for your app (e.g., `bb318a62-fa61-49ae-b692-7d99214f0ec7`)
- **Client Secret**: Only for confidential clients (backend apps)
- **Sandbox FHIR URL**: `https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d`

### Step 4: Test Configuration
```bash
export CERNER_CLIENT_ID="your-client-id-from-step-3"
export CERNER_FHIR_URL="https://fhir-ehr-code.cerner.com/r4/ec2458f2-1e24-41c8-b71b-0e701af7583d"

python3 cerner_example.py
```

## Phase 2: Production Deployment (Admin Required)

### When You Need Administration
- **Real patient data** access
- **EHR integration** (provider-facing apps)
- **System-to-system** authentication
- **Custom FHIR endpoints**

### Who You Need to Contact
1. **EHR Administrator**: Manages Cerner system configuration
2. **IT Security**: Handles application approvals and security reviews
3. **Clinical Informatics**: Reviews clinical workflow integration
4. **Compliance Officer**: HIPAA and regulatory approval

### What Administrators Need to Do

#### Healthcare Organization Side:
1. **Enable SMART on FHIR**: Ensure Cerner SMART capabilities are enabled
2. **App Whitelisting**: Add your app to approved applications list
3. **Scope Approval**: Approve specific FHIR scopes your app needs
4. **User Access**: Grant users permission to launch your app
5. **Production URLs**: Provide production FHIR endpoints

#### Cerner Central Management:
1. **System Account**: Create system account for your app (if backend service)
2. **Client Credentials**: Generate production client ID/secret
3. **Tenant Configuration**: Configure app for specific Cerner tenant
4. **Security Settings**: Set up authentication and authorization rules

## Phase 3: Authentication Types

### 1. Public Client (Patient-Facing Apps)
**No Admin Required for Development**
```python
client = CernerFHIRClient(
    client_id="your-public-client-id",
    fhir_base_url="https://fhir-ehr-code.cerner.com/r4/tenant-id"
)
```

**Credentials Needed:**
- ✅ Client ID (from code.cerner.com)
- ❌ Client Secret (not needed)
- ✅ FHIR Base URL (sandbox provided)

### 2. Confidential Client (Provider-Facing Apps)
**Admin Required for Production**
```python
client = CernerFHIRClient(
    client_id="your-confidential-client-id",
    client_secret="your-client-secret",
    fhir_base_url="https://fhir-ehr.cerner.com/r4/tenant-id"
)
```

**Credentials Needed:**
- ✅ Client ID (from admin)
- ✅ Client Secret (from admin/Cerner Central)
- ✅ Production FHIR URL (from admin)

### 3. System Account (Backend Services)
**Admin Required**
```python
# System-to-system authentication (no user interaction)
client = CernerFHIRClient(
    client_id="system-account-id",
    client_secret="system-account-secret",
    fhir_base_url="https://fhir-ehr.cerner.com/r4/tenant-id"
)
```

**Credentials Needed:**
- ✅ System Account ID (from Cerner Central)
- ✅ System Account Secret (from Cerner Central)
- ✅ Production FHIR URL (from admin)

## Quick Start Options

### Option 1: Immediate Testing (No Admin)
```bash
# 1. Register at code.cerner.com (5 minutes)
# 2. Get client ID
# 3. Use sandbox environment
export CERNER_CLIENT_ID="your-sandbox-client-id"
python3 cerner_example.py
```

### Option 2: Real Data Access (Admin Required)
```bash
# 1. Contact your IT/EHR administrator
# 2. Request production FHIR access
# 3. Get production credentials
# 4. Configure production environment
export CERNER_CLIENT_ID="prod-client-id"
export CERNER_FHIR_URL="https://fhir-ehr.cerner.com/r4/your-tenant"
```

## Credential Security Best Practices

### Development Environment
```bash
# Use environment variables (never hardcode)
export CERNER_CLIENT_ID="development-client-id"
export CERNER_FHIR_URL="sandbox-url"

# Optional: Use .env file
echo "CERNER_CLIENT_ID=your-client-id" > .env
echo "CERNER_FHIR_URL=sandbox-url" >> .env
```

### Production Environment
```bash
# Secure credential storage
export CERNER_CLIENT_ID="production-client-id"
export CERNER_CLIENT_SECRET="secure-secret"
export CERNER_FHIR_URL="https://fhir-ehr.cerner.com/r4/tenant"

# Consider using secrets management
# - AWS Secrets Manager
# - Azure Key Vault
# - HashiCorp Vault
# - Kubernetes Secrets
```

## Troubleshooting Authentication

### Common Issues

#### "Invalid Client" Error
```
Problem: Client ID not recognized
Solutions:
- Verify client ID is correct
- Check if app is properly registered
- Ensure using correct environment (sandbox vs production)
```

#### "Insufficient Scope" Error
```
Problem: App doesn't have permission for requested scopes
Solutions:
- Check app registration scopes
- Contact admin to approve additional scopes
- Verify scope syntax in authorization request
```

#### "Invalid Redirect URI" Error
```
Problem: Redirect URI doesn't match registration
Solutions:
- Ensure exact match with registered URI
- Include protocol (http/https)
- Check for trailing slashes
```

### Debug Authentication Flow
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed OAuth flow information
client = CernerFHIRClient(client_id="your-id", fhir_base_url="url")
auth_url, state = client.get_authorization_url()
print(f"Authorization URL: {auth_url}")
```

## Getting Help

### Self-Service Resources
- **Cerner FHIR Docs**: https://fhir.cerner.com/
- **SMART on FHIR**: https://docs.smarthealthit.org/
- **Code Console Help**: Built-in help at code.cerner.com

### When to Contact Administration
- Need access to real patient data
- Want to integrate with provider workflows
- Require system-to-system authentication
- Need custom FHIR endpoints or configurations

### What to Ask Administration
1. "Does our organization support SMART on FHIR applications?"
2. "Can you help me register a clinical application for anesthesia planning?"
3. "What are the approval requirements for accessing patient FHIR data?"
4. "Do you have development/testing FHIR endpoints available?"
5. "What scopes and permissions can be approved for anesthesia applications?" 