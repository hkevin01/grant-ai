"""
Streamlit GUI for Grant AI grant search and management.
"""
import streamlit as st

from grant_ai.analysis.grant_researcher import GrantResearcher
from grant_ai.models.organization import OrganizationProfile
from grant_ai.scrapers.state_federal import StateFederalGrantScraper

st.set_page_config(page_title="Grant Research AI", layout="wide")
st.title("Grant Research AI - Grant Search & Management")

st.sidebar.header("Organization Profile")
org_name = st.sidebar.text_input("Organization Name", "CODA")
focus_areas = st.sidebar.multiselect(
    "Focus Areas", ["education", "music", "art", "robotics", "housing", "community"]
)

if st.sidebar.button("Load Profile"):
    st.session_state["org_profile"] = OrganizationProfile(
        name=org_name,
        focus_areas=focus_areas,
    )

org_profile = st.session_state.get("org_profile")
if org_profile:
    st.write(f"### Organization: {org_profile.name}")
    st.write(f"Focus Areas: {', '.join(org_profile.focus_areas)}")

    st.header("Grant Search")
    query = st.text_input("Search Grants", "education technology")
    if st.button("Search State/Federal Grants"):
        scraper = StateFederalGrantScraper()
        results = scraper.search_grants(query)
        st.write(f"Found {len(results)} grants.")
        for grant in results:
            st.write(f"- {grant.title} ({grant.funder_name})")
else:
    st.info("Load an organization profile to begin.")
