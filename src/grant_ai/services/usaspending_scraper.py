"""
USASpending.gov Scraper Service

Fetches awarded grants for an organization by name or EIN from USASpending.gov.
"""
import requests
import json
import time
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import re
from ..models.organization import PastGrant
from ..models.organization import OrganizationProfile

USASPENDING_SEARCH_URL = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
USASPENDING_AWARD_URL = "https://www.usaspending.gov/award/{}"

class USASpendingScraper:
    """
    Service to fetch awarded grants for an organization from USASpending.gov.
    """
    def __init__(self):
        self.base_url = "https://api.usaspending.gov/api/v2/search/spending_by_award/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_awarded_grants(self, org_name: Optional[str] = None, ein: Optional[str] = None, limit: int = 50) -> List[PastGrant]:
        """
        Fetch awarded grants for an organization by name or EIN.
        Args:
            org_name: Organization name (as registered in federal records)
            ein: Employer Identification Number (if available)
            limit: Max number of results
        Returns:
            List of PastGrant objects
        """
        filters = {}
        if org_name:
            filters["recipient_search_text"] = [org_name]
        if ein:
            filters["recipient_tin"] = [ein]
        # Only grants
        filters["award_type_codes"] = ["02", "03", "04", "05"]  # Grant, Direct Payment, etc.

        payload = {
            "filters": filters,
            "fields": [
                "Award ID", "Recipient Name", "Base Obligation Date", "Award Amount", 
                "Awarding Agency", "Award Type"
            ],
            "limit": limit,
            "page": 1,
            "sort": "Base Obligation Date",
            "order": "desc"
        }

        response = self.session.post(USASPENDING_SEARCH_URL, json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        past_grants = []
        for item in results:
            try:
                award_id = item.get("Award ID") or ""
                name = item.get("Award Type") or "Federal Grant"
                funder = item.get("Awarding Agency") or "US Federal Agency"
                year = int(item.get("Base Obligation Date", "").split("-")[0]) if item.get("Base Obligation Date") else None
                amount = float(item.get("Award Amount", 0))
                status = "won"
                url = USASPENDING_AWARD_URL.format(award_id) if award_id else None
                # Estimate next open: assume annual if possible
                next_estimated_open = f"{year+1}-01-01" if year else None
                past_grants.append(PastGrant(
                    grant_id=award_id,
                    name=name,
                    funder=funder,
                    year=year,
                    amount=amount,
                    status=status,
                    url=url,
                    next_estimated_open=next_estimated_open
                ))
            except Exception as e:
                continue
        return past_grants

    def search_organization_grants(self, organization_name: str, ein: Optional[str] = None) -> List[PastGrant]:
        """
        Search for past grants awarded to an organization.
        
        Args:
            organization_name: Name of the organization
            ein: EIN number (optional)
            
        Returns:
            List of PastGrant objects
        """
        try:
            # Create search variations for better matching
            search_variations = self._create_search_variations(organization_name)
            
            all_grants = []
            
            for variation in search_variations:
                try:
                    grants = self._search_single_variation(variation, ein)
                    all_grants.extend(grants)
                    time.sleep(1)  # Rate limiting
                except Exception as e:
                    print(f"Error searching variation '{variation}': {e}")
                    continue
            
            # Remove duplicates and sort by date
            unique_grants = self._deduplicate_grants(all_grants)
            return sorted(unique_grants, key=lambda x: x.award_date, reverse=True)
            
        except Exception as e:
            print(f"Error in search_organization_grants: {e}")
            return []
    
    def _create_search_variations(self, organization_name: str) -> List[str]:
        """Create different search variations for better matching."""
        variations = [organization_name]
        
        # Remove common suffixes
        name_clean = organization_name.lower()
        if name_clean.endswith((' inc', ' llc', ' corp', ' corporation', ' foundation', ' nonprofit')):
            name_clean = re.sub(r'\s+(inc|llc|corp|corporation|foundation|nonprofit)$', '', name_clean)
            variations.append(name_clean.title())
        
        # For Coda Mountain Academy specifically
        if 'coda' in name_clean and 'mountain' in name_clean:
            variations.extend([
                'Coda Mountain Academy',
                'Coda Mountain',
                'Coda Academy',
                'CODA Mountain Academy',
                'CODA Mountain',
                'CODA Academy'
            ])
        
        # Split into words and try partial matches
        words = organization_name.split()
        if len(words) > 2:
            # Try first two words
            variations.append(' '.join(words[:2]))
            # Try first and last word
            variations.append(f"{words[0]} {words[-1]}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_variations = []
        for var in variations:
            if var.lower() not in seen:
                seen.add(var.lower())
                unique_variations.append(var)
        
        return unique_variations
    
    def _search_single_variation(self, organization_name: str, ein: Optional[str] = None) -> List[PastGrant]:
        """Search for a single organization name variation."""
        
        # Build the search payload
        payload = {
            "filters": {
                "award_type_codes": ["02", "03", "04", "05"],  # Grants and cooperative agreements
                "time_period": [
                    {
                        "start_date": "2015-01-01",
                        "end_date": datetime.now().strftime("%Y-%m-%d")
                    }
                ],
                "award_amounts": [
                    {
                        "lower_bound": 1000,
                        "upper_bound": 10000000
                    }
                ]
            },
            "fields": [
                "Award ID",
                "Recipient Name",
                "Recipient DUNS",
                "Recipient EIN",
                "Award Amount",
                "Award Date",
                "Award Type",
                "Awarding Agency",
                "Awarding Sub Agency",
                "CFDA Number",
                "CFDA Title",
                "Program Title",
                "Program Description",
                "NAICS Code",
                "NAICS Description",
                "Recipient Address",
                "Recipient City",
                "Recipient State",
                "Recipient ZIP Code"
            ],
            "page": 1,
            "limit": 100,
            "sort": "Award Date",
            "order": "desc"
        }
        
        # Add recipient name filter
        if organization_name:
            payload["filters"]["recipient_search_text"] = organization_name
        
        # Add EIN filter if provided
        if ein:
            payload["filters"]["recipient_ein"] = ein
        
        try:
            response = self.session.post(self.base_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('results'):
                return []
            
            grants = []
            for result in data['results']:
                try:
                    grant = self._parse_grant_result(result)
                    if grant:
                        grants.append(grant)
                except Exception as e:
                    print(f"Error parsing grant result: {e}")
                    continue
            
            return grants
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for '{organization_name}': {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON decode error for '{organization_name}': {e}")
            return []
    
    def _parse_grant_result(self, result: Dict[str, Any]) -> Optional[PastGrant]:
        """Parse a single grant result from the API response."""
        try:
            # Extract basic information
            award_id = result.get('Award ID', '')
            recipient_name = result.get('Recipient Name', '')
            award_amount = result.get('Award Amount', 0)
            award_date_str = result.get('Award Date', '')
            
            # Parse award date
            award_date = None
            if award_date_str:
                try:
                    award_date = datetime.strptime(award_date_str, '%Y-%m-%d')
                except ValueError:
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y-%m-%dT%H:%M:%S']:
                        try:
                            award_date = datetime.strptime(award_date_str, fmt)
                            break
                        except ValueError:
                            continue
            
            # Extract additional information
            awarding_agency = result.get('Awarding Agency', '')
            awarding_sub_agency = result.get('Awarding Sub Agency', '')
            cfda_number = result.get('CFDA Number', '')
            cfda_title = result.get('CFDA Title', '')
            program_title = result.get('Program Title', '')
            program_description = result.get('Program Description', '')
            
            # Extract location information
            recipient_city = result.get('Recipient City', '')
            recipient_state = result.get('Recipient State', '')
            recipient_zip = result.get('Recipient ZIP Code', '')
            
            # Build location string
            location_parts = []
            if recipient_city:
                location_parts.append(recipient_city)
            if recipient_state:
                location_parts.append(recipient_state)
            if recipient_zip:
                location_parts.append(recipient_zip)
            
            location = ', '.join(location_parts) if location_parts else ''
            
            # Build description
            description_parts = []
            if program_title:
                description_parts.append(program_title)
            if program_description:
                description_parts.append(program_description)
            if cfda_title:
                description_parts.append(f"CFDA: {cfda_title}")
            
            description = ' | '.join(description_parts) if description_parts else 'No description available'
            
            # Estimate next open date (typically 1-2 years after award)
            next_open_date = None
            if award_date:
                # Most grants re-open 12-24 months after award
                next_open_date = award_date + timedelta(days=365)
            
            return PastGrant(
                id=award_id,
                title=program_title or f"Grant from {awarding_agency}",
                description=description,
                funder_name=awarding_agency,
                funder_type="Federal Government",
                amount=award_amount,
                award_date=award_date,
                next_open_date=next_open_date,
                location=location,
                cfda_number=cfda_number,
                cfda_title=cfda_title,
                awarding_sub_agency=awarding_sub_agency,
                source="USASpending.gov",
                source_url=f"https://www.usaspending.gov/award/{award_id}"
            )
            
        except Exception as e:
            print(f"Error parsing grant result: {e}")
            return None
    
    def _deduplicate_grants(self, grants: List[PastGrant]) -> List[PastGrant]:
        """Remove duplicate grants based on award ID."""
        seen_ids = set()
        unique_grants = []
        
        for grant in grants:
            if grant.id not in seen_ids:
                seen_ids.add(grant.id)
                unique_grants.append(grant)
        
        return unique_grants
    
    def search_by_profile(self, profile: OrganizationProfile) -> List[PastGrant]:
        """
        Search for past grants using an organization profile.
        
        Args:
            profile: Organization profile
            
        Returns:
            List of PastGrant objects
        """
        if not profile:
            return []
        
        # Try organization name first
        grants = self.search_organization_grants(profile.name)
        
        # If no results and we have an EIN, try that
        if not grants and hasattr(profile, 'ein') and profile.ein:
            grants = self.search_organization_grants(profile.name, profile.ein)
        
        # If still no results, try alternative names
        if not grants and hasattr(profile, 'alternative_names') and profile.alternative_names:
            for alt_name in profile.alternative_names:
                alt_grants = self.search_organization_grants(alt_name)
                grants.extend(alt_grants)
        
        return grants 