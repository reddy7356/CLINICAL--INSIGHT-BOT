#!/usr/bin/env python3
"""
EPIC FHIR Integration Module for Clinical Insight Bot
Connects to EPIC's FHIR APIs using SMART on FHIR authentication to extract patient data.
"""

import json
import base64
import requests
import secrets
import urllib.parse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import webbrowser
from clinical_insight_bot import ClinicalInsightBot


class EpicFHIRClient:
    """Client for connecting to EPIC FHIR APIs with SMART on FHIR authentication."""
    
    def __init__(self, client_id: str, client_secret: str = None, 
                 fhir_base_url: str = None, redirect_uri: str = "https://fhir.epic.com/test/smart"):
        """
        Initialize EPIC FHIR client.
        
        Args:
            client_id: OAuth client ID from EPIC registration
            client_secret: OAuth client secret (for confidential clients)
            fhir_base_url: Base URL for FHIR API (e.g., https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/)
            redirect_uri: OAuth redirect URI
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.fhir_base_url = fhir_base_url or "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
        self.redirect_uri = redirect_uri
        
        # OAuth endpoints (discovered from SMART configuration)
        self.authorization_endpoint = None
        self.token_endpoint = None
        self.smart_config = None
        
        # Authentication state
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.patient_id = None
        
        # Initialize Clinical Insight Bot
        self.insight_bot = ClinicalInsightBot()
    
    def discover_smart_configuration(self) -> Dict[str, Any]:
        """
        Discover SMART on FHIR configuration from the EPIC FHIR server.
        
        Returns:
            SMART configuration dictionary
        """
        well_known_url = f"{self.fhir_base_url.rstrip('/')}/.well-known/smart-configuration"
        
        try:
            response = requests.get(well_known_url, timeout=30)
            response.raise_for_status()
            
            self.smart_config = response.json()
            self.authorization_endpoint = self.smart_config.get('authorization_endpoint')
            self.token_endpoint = self.smart_config.get('token_endpoint')
            
            print(f"✓ Discovered EPIC SMART configuration")
            print(f"  Authorization endpoint: {self.authorization_endpoint}")
            print(f"  Token endpoint: {self.token_endpoint}")
            
            return self.smart_config
            
        except requests.RequestException as e:
            raise Exception(f"Failed to discover EPIC SMART configuration: {e}")
    
    def get_authorization_url(self, scopes: List[str] = None, 
                            launch_context: str = None) -> tuple:
        """
        Generate OAuth authorization URL for EPIC SMART on FHIR.
        
        Args:
            scopes: List of FHIR scopes to request
            launch_context: Launch context from EHR (if applicable)
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if not self.authorization_endpoint:
            self.discover_smart_configuration()
        
        # Default scopes for patient data access (EPIC-specific)
        if scopes is None:
            scopes = [
                'patient/Patient.read',
                'patient/Observation.read',
                'patient/Condition.read',
                'patient/MedicationRequest.read',
                'patient/AllergyIntolerance.read',
                'patient/Procedure.read',
                'patient/DiagnosticReport.read',
                'patient/DocumentReference.read',
                'openid',
                'fhirUser',
                'online_access'
            ]
        
        # Generate secure state parameter
        state = secrets.token_urlsafe(32)
        
        # Build authorization parameters
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes),
            'state': state,
            'aud': self.fhir_base_url
        }
        
        # Add launch context if provided (for EHR launch)
        if launch_context:
            params['launch'] = launch_context
            if 'launch' not in scopes:
                scopes.append('launch')
                params['scope'] = ' '.join(scopes)
        
        # Build authorization URL
        auth_url = f"{self.authorization_endpoint}?{urllib.parse.urlencode(params)}"
        
        return auth_url, state
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token with EPIC.
        
        Args:
            authorization_code: Authorization code from OAuth callback
            
        Returns:
            Token response dictionary
        """
        if not self.token_endpoint:
            raise ValueError("Token endpoint not discovered")
        
        # Prepare token request
        data = {
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        # Add client authentication for confidential clients
        if self.client_secret:
            auth_string = f"{self.client_id}:{self.client_secret}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            headers['Authorization'] = f"Basic {encoded_auth}"
        
        try:
            response = requests.post(self.token_endpoint, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            token_response = response.json()
            
            # Store token information
            self.access_token = token_response.get('access_token')
            self.refresh_token = token_response.get('refresh_token')
            
            # Calculate token expiration
            expires_in = token_response.get('expires_in', 3600)  # Default 1 hour
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Extract patient context if available
            self.patient_id = token_response.get('patient')
            
            print(f"✓ Successfully obtained access token")
            if self.patient_id:
                print(f"  Patient context: {self.patient_id}")
            
            return token_response
            
        except requests.RequestException as e:
            raise Exception(f"Failed to exchange authorization code with EPIC: {e}")
    
    def make_fhir_request(self, resource_path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make authenticated FHIR API request to EPIC.
        
        Args:
            resource_path: FHIR resource path (e.g., 'Patient/123')
            params: Query parameters
            
        Returns:
            FHIR response dictionary
        """
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        url = f"{self.fhir_base_url.rstrip('/')}/{resource_path.lstrip('/')}"
        
        headers = {
            'Authorization': f"Bearer {self.access_token}",
            'Accept': 'application/fhir+json',
            'Content-Type': 'application/fhir+json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            if response.status_code == 401:
                raise Exception(f"EPIC FHIR API authentication failed: {e}")
            elif response.status_code == 403:
                raise Exception(f"EPIC FHIR API access forbidden: {e}")
            else:
                raise Exception(f"EPIC FHIR API request failed: {e}")
    
    def get_patient_data(self, patient_id: str = None) -> Dict[str, Any]:
        """
        Retrieve comprehensive patient data from EPIC for anesthesia planning.
        
        Args:
            patient_id: Patient ID (uses context patient if not provided)
            
        Returns:
            Dictionary containing all relevant patient data
        """
        if not patient_id:
            patient_id = self.patient_id
        
        if not patient_id:
            raise ValueError("No patient ID available")
        
        patient_data = {
            'patient': None,
            'observations': [],
            'conditions': [],
            'medications': [],
            'allergies': [],
            'procedures': [],
            'diagnostic_reports': []
        }
        
        try:
            # Get patient demographics
            print(f"Retrieving patient data for: {patient_id}")
            patient_data['patient'] = self.make_fhir_request(f"Patient/{patient_id}")
            print("✓ Patient demographics retrieved")
            
            # Get observations (labs, vitals)
            obs_response = self.make_fhir_request("Observation", 
                                                params={'patient': patient_id, '_count': 100})
            if obs_response.get('entry'):
                patient_data['observations'] = [entry['resource'] for entry in obs_response['entry']]
                print(f"✓ {len(patient_data['observations'])} observations retrieved")
            
            # Get conditions (diagnoses, comorbidities)
            cond_response = self.make_fhir_request("Condition", 
                                                 params={'patient': patient_id, '_count': 100})
            if cond_response.get('entry'):
                patient_data['conditions'] = [entry['resource'] for entry in cond_response['entry']]
                print(f"✓ {len(patient_data['conditions'])} conditions retrieved")
            
            # Get medications
            med_response = self.make_fhir_request("MedicationRequest", 
                                                params={'patient': patient_id, '_count': 100})
            if med_response.get('entry'):
                patient_data['medications'] = [entry['resource'] for entry in med_response['entry']]
                print(f"✓ {len(patient_data['medications'])} medications retrieved")
            
            # Get allergies
            allergy_response = self.make_fhir_request("AllergyIntolerance", 
                                                    params={'patient': patient_id, '_count': 100})
            if allergy_response.get('entry'):
                patient_data['allergies'] = [entry['resource'] for entry in allergy_response['entry']]
                print(f"✓ {len(patient_data['allergies'])} allergies retrieved")
            
            # Get procedures
            proc_response = self.make_fhir_request("Procedure", 
                                                 params={'patient': patient_id, '_count': 100})
            if proc_response.get('entry'):
                patient_data['procedures'] = [entry['resource'] for entry in proc_response['entry']]
                print(f"✓ {len(patient_data['procedures'])} procedures retrieved")
            
        except Exception as e:
            print(f"Warning: Failed to retrieve some patient data: {e}")
        
        return patient_data
    
    def convert_fhir_to_text(self, patient_data: Dict[str, Any]) -> str:
        """
        Convert EPIC FHIR patient data to text format for Clinical Insight Bot.
        
        Args:
            patient_data: Dictionary containing FHIR resources
            
        Returns:
            Formatted text suitable for clinical insight extraction
        """
        text_parts = []
        
        # Patient demographics
        if patient_data.get('patient'):
            patient = patient_data['patient']
            
            # Basic info
            name = "Unknown"
            if patient.get('name') and len(patient['name']) > 0:
                name_parts = []
                if patient['name'][0].get('given'):
                    name_parts.extend(patient['name'][0]['given'])
                if patient['name'][0].get('family'):
                    name_parts.append(patient['name'][0]['family'])
                name = ' '.join(name_parts)
            
            text_parts.append(f"PATIENT: {name}")
            
            # Birth date / Age
            if patient.get('birthDate'):
                try:
                    birth_date = datetime.fromisoformat(patient['birthDate'].replace('Z', '+00:00'))
                    age = (datetime.now() - birth_date).days // 365
                    text_parts.append(f"AGE: {age} years old")
                except:
                    text_parts.append(f"BIRTH DATE: {patient['birthDate']}")
            
            # Gender
            if patient.get('gender'):
                text_parts.append(f"GENDER: {patient['gender'].title()}")
        
        # Conditions (Past Medical History)
        if patient_data.get('conditions'):
            text_parts.append("\nPAST MEDICAL HISTORY:")
            for condition in patient_data['conditions']:
                if condition.get('code', {}).get('text'):
                    condition_text = condition['code']['text']
                elif condition.get('code', {}).get('coding'):
                    condition_text = condition['code']['coding'][0].get('display', 'Unknown condition')
                else:
                    continue
                
                text_parts.append(f"- {condition_text}")
        
        # Medications
        if patient_data.get('medications'):
            text_parts.append("\nMEDICATIONS:")
            for med in patient_data['medications']:
                if med.get('medicationCodeableConcept', {}).get('text'):
                    med_name = med['medicationCodeableConcept']['text']
                elif med.get('medicationCodeableConcept', {}).get('coding'):
                    med_name = med['medicationCodeableConcept']['coding'][0].get('display', 'Unknown medication')
                else:
                    continue
                
                # Add dosage if available
                dosage = ""
                if med.get('dosageInstruction') and len(med['dosageInstruction']) > 0:
                    dose_info = med['dosageInstruction'][0]
                    if dose_info.get('text'):
                        dosage = f" - {dose_info['text']}"
                
                text_parts.append(f"- {med_name}{dosage}")
        
        # Allergies
        if patient_data.get('allergies'):
            text_parts.append("\nALLERGIES:")
            for allergy in patient_data['allergies']:
                if allergy.get('code', {}).get('text'):
                    allergen = allergy['code']['text']
                elif allergy.get('code', {}).get('coding'):
                    allergen = allergy['code']['coding'][0].get('display', 'Unknown allergen')
                else:
                    continue
                
                # Add reaction if available
                reaction = ""
                if allergy.get('reaction') and len(allergy['reaction']) > 0:
                    manifestations = allergy['reaction'][0].get('manifestation', [])
                    if manifestations and len(manifestations) > 0:
                        if manifestations[0].get('text'):
                            reaction = f" ({manifestations[0]['text']})"
                
                text_parts.append(f"- {allergen}{reaction}")
        
        # Lab Values (Observations)
        if patient_data.get('observations'):
            text_parts.append("\nLABORATORY VALUES:")
            
            # Group observations by type
            lab_values = {}
            for obs in patient_data['observations']:
                if obs.get('code', {}).get('text'):
                    lab_name = obs['code']['text']
                elif obs.get('code', {}).get('coding'):
                    lab_name = obs['code']['coding'][0].get('display', 'Unknown lab')
                else:
                    continue
                
                # Extract value
                value = ""
                if obs.get('valueQuantity'):
                    value_num = obs['valueQuantity'].get('value', '')
                    unit = obs['valueQuantity'].get('unit', '')
                    value = f"{value_num} {unit}".strip()
                elif obs.get('valueString'):
                    value = obs['valueString']
                
                if value and lab_name not in lab_values:
                    lab_values[lab_name] = value
            
            # Add lab values to text
            for lab_name, value in lab_values.items():
                text_parts.append(f"{lab_name}: {value}")
        
        # Procedures
        if patient_data.get('procedures'):
            text_parts.append("\nPROCEDURES:")
            for proc in patient_data['procedures']:
                if proc.get('code', {}).get('text'):
                    proc_name = proc['code']['text']
                elif proc.get('code', {}).get('coding'):
                    proc_name = proc['code']['coding'][0].get('display', 'Unknown procedure')
                else:
                    continue
                
                # Add date if available
                date_info = ""
                if proc.get('performedDateTime'):
                    date_info = f" ({proc['performedDateTime'][:10]})"
                
                text_parts.append(f"- {proc_name}{date_info}")
        
        return '\n'.join(text_parts)
    
    def get_clinical_insights(self, patient_id: str = None) -> Dict[str, Any]:
        """
        Get clinical insights for anesthesia planning using EPIC FHIR data.
        
        Args:
            patient_id: Patient ID (uses context patient if not provided)
            
        Returns:
            Clinical insights dictionary from the bot
        """
        # Get patient data from EPIC FHIR
        patient_data = self.get_patient_data(patient_id)
        
        # Convert to text format
        patient_text = self.convert_fhir_to_text(patient_data)
        
        # Process with Clinical Insight Bot
        insights = self.insight_bot.process_emr_text(patient_text)
        
        # Add EPIC FHIR source metadata
        insights['metadata']['fhir_source'] = {
            'fhir_base_url': self.fhir_base_url,
            'patient_id': patient_id or self.patient_id,
            'data_extraction_timestamp': datetime.now().isoformat(),
            'epic_version': 'FHIR R4'
        }
        
        return insights
    
    def test_connection(self) -> bool:
        """
        Test connection to EPIC FHIR server without authentication.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            print("Testing connection to EPIC FHIR server...")
            self.discover_smart_configuration()
            print("✓ Successfully connected to EPIC FHIR server")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to EPIC FHIR server: {e}")
            return False


def start_epic_oauth_flow(client_id: str, fhir_base_url: str = None, 
                         scopes: List[str] = None) -> tuple:
    """
    Helper function to start OAuth flow for EPIC integration.
    
    Args:
        client_id: OAuth client ID from EPIC registration
        fhir_base_url: FHIR base URL (defaults to EPIC sandbox)
        scopes: List of scopes to request
        
    Returns:
        Tuple of (EpicFHIRClient instance, state parameter)
    """
    if not fhir_base_url:
        fhir_base_url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
    
    client = EpicFHIRClient(client_id=client_id, fhir_base_url=fhir_base_url)
    
    # Test connection first
    print("Testing connection to EPIC FHIR server...")
    if not client.test_connection():
        return None, None
    
    # Generate authorization URL
    print("Generating authorization URL...")
    try:
        auth_url, state = client.get_authorization_url(scopes)
        print(f"✓ Authorization URL generated")
        print(f"\nPlease visit this URL to authorize the application:")
        print(f"{auth_url}")
        print(f"\nState parameter (keep this for verification): {state}")
        
        # Optionally open browser
        try:
            webbrowser.open(auth_url)
            print("✓ Browser opened automatically")
        except:
            print("Unable to open browser automatically")
        
        return client, state
        
    except Exception as e:
        print(f"✗ Failed to generate authorization URL: {e}")
        return None, None


def test_epic_connection(fhir_base_url: str = None) -> bool:
    """
    Test connection to EPIC FHIR server without requiring credentials.
    
    Args:
        fhir_base_url: FHIR base URL (defaults to EPIC sandbox)
        
    Returns:
        True if connection successful, False otherwise
    """
    if not fhir_base_url:
        fhir_base_url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/"
    
    client = EpicFHIRClient(client_id="test", fhir_base_url=fhir_base_url)
    return client.test_connection()


if __name__ == "__main__":
    print("EPIC FHIR Integration Module")
    print("This module provides integration with EPIC's FHIR APIs")
    
    # Test connection to EPIC sandbox
    print("\nTesting connection to EPIC FHIR sandbox...")
    if test_epic_connection():
        print("✓ Ready for EPIC FHIR integration!")
    else:
        print("✗ Unable to connect to EPIC FHIR server")
        print("Please check your internet connection and EPIC FHIR service status") 