"""
Competitive Analysis Features for Grant AI

This module analyzes other organizations' grant histories and success patterns
to identify opportunities and strategies for competitive advantage.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict, Counter

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

from grant_ai.models.grant import Grant
from grant_ai.models.organization import OrganizationProfile


@dataclass
class CompetitorProfile:
    """Profile of a competing organization."""
    organization_id: str
    organization_name: str
    total_applications: int
    success_rate: float
    total_funding_won: float
    avg_grant_size: float
    primary_focus_areas: List[str]
    funding_sources: List[str]
    success_strategies: List[str]
    competitive_advantages: List[str]
    recent_wins: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'organization_id': self.organization_id,
            'organization_name': self.organization_name,
            'total_applications': self.total_applications,
            'success_rate': self.success_rate,
            'total_funding_won': self.total_funding_won,
            'avg_grant_size': self.avg_grant_size,
            'primary_focus_areas': self.primary_focus_areas,
            'funding_sources': self.funding_sources,
            'success_strategies': self.success_strategies,
            'competitive_advantages': self.competitive_advantages,
            'recent_wins': self.recent_wins
        }


@dataclass
class MarketOpportunity:
    """Identified market opportunity based on competitive analysis."""
    opportunity_id: str
    opportunity_type: str  # 'underserved_niche', 'emerging_funder', 'gap_analysis'
    description: str
    estimated_value: float
    competition_level: str  # 'Low', 'Medium', 'High'
    success_probability: float
    key_requirements: List[str]
    similar_organizations: List[str]
    recommended_strategy: str
    timeline: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary format."""
        return {
            'opportunity_id': self.opportunity_id,
            'opportunity_type': self.opportunity_type,
            'description': self.description,
            'estimated_value': self.estimated_value,
            'competition_level': self.competition_level,
            'success_probability': self.success_probability,
            'key_requirements': self.key_requirements,
            'similar_organizations': self.similar_organizations,
            'recommended_strategy': self.recommended_strategy,
            'timeline': self.timeline
        }


class CompetitiveAnalysisEngine:
    """Advanced competitive analysis and opportunity identification system."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the competitive analysis engine."""
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path(data_dir)
        
        # Market intelligence data
        self.competitor_profiles = {}
        self.market_segments = {}
        self.funding_landscape = {}
        self.success_patterns = {}
        
        # ML components for clustering and analysis
        self.scaler = StandardScaler()
        self.clustering_model = KMeans(n_clusters=5, random_state=42)
        
        self.logger.info("Competitive Analysis Engine initialized")

    def analyze_competitive_landscape(
        self,
        target_organization: OrganizationProfile,
        market_data: List[Dict],
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Comprehensive competitive landscape analysis."""
        try:
            analysis_results = {
                'market_overview': {},
                'competitor_profiles': [],
                'market_opportunities': [],
                'strategic_recommendations': [],
                'competitive_positioning': {},
                'market_trends': {}
            }
            
            # Filter market data by focus areas if specified
            if focus_areas:
                filtered_data = [
                    record for record in market_data
                    if any(area in record.get('grant', {}).get('focus_areas', [])
                          for area in focus_areas)
                ]
            else:
                filtered_data = market_data
            
            # Analyze market overview
            analysis_results['market_overview'] = self._analyze_market_overview(
                filtered_data
            )
            
            # Identify and profile competitors
            competitors = self._identify_competitors(
                target_organization, filtered_data
            )
            analysis_results['competitor_profiles'] = [
                comp.to_dict() for comp in competitors
            ]
            
            # Identify market opportunities
            opportunities = self._identify_market_opportunities(
                target_organization, filtered_data, competitors
            )
            analysis_results['market_opportunities'] = [
                opp.to_dict() for opp in opportunities
            ]
            
            # Generate strategic recommendations
            analysis_results['strategic_recommendations'] = (
                self._generate_strategic_recommendations(
                    target_organization, competitors, opportunities
                )
            )
            
            # Analyze competitive positioning
            analysis_results['competitive_positioning'] = (
                self._analyze_competitive_positioning(
                    target_organization, competitors
                )
            )
            
            # Identify market trends
            analysis_results['market_trends'] = self._analyze_market_trends(
                filtered_data
            )
            
            self.logger.info("Competitive landscape analysis completed")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"Error in competitive analysis: {e}")
            return {}

    def _analyze_market_overview(self, market_data: List[Dict]) -> Dict[str, Any]:
        """Analyze overall market characteristics."""
        try:
            overview = {
                'total_grants': len(market_data),
                'total_funding': 0,
                'avg_grant_size': 0,
                'success_rate': 0,
                'top_funders': [],
                'popular_focus_areas': [],
                'funding_distribution': {},
                'competition_intensity': 'Medium'
            }
            
            if not market_data:
                return overview
            
            # Calculate funding metrics
            grant_amounts = []
            successful_grants = 0
            funders = Counter()
            focus_areas = Counter()
            
            for record in market_data:
                grant_info = record.get('grant', {})
                amount = grant_info.get('amount_typical', 0)
                
                if amount > 0:
                    grant_amounts.append(amount)
                    overview['total_funding'] += amount
                
                if record.get('outcome') in ['awarded', 'funded', 'approved']:
                    successful_grants += 1
                
                # Track funders
                funder = record.get('funder', 'Unknown')
                funders[funder] += 1
                
                # Track focus areas
                for area in grant_info.get('focus_areas', []):
                    focus_areas[area] += 1
            
            # Calculate averages and rates
            if grant_amounts:
                overview['avg_grant_size'] = np.mean(grant_amounts)
            
            if market_data:
                overview['success_rate'] = successful_grants / len(market_data)
            
            # Top funders and focus areas
            overview['top_funders'] = [
                {'name': funder, 'count': count}
                for funder, count in funders.most_common(10)
            ]
            
            overview['popular_focus_areas'] = [
                {'area': area, 'count': count}
                for area, count in focus_areas.most_common(10)
            ]
            
            # Funding distribution analysis
            if grant_amounts:
                overview['funding_distribution'] = {
                    'small_grants': len([a for a in grant_amounts if a < 25000]),
                    'medium_grants': len([a for a in grant_amounts 
                                        if 25000 <= a < 100000]),
                    'large_grants': len([a for a in grant_amounts if a >= 100000])
                }
            
            # Assess competition intensity
            unique_orgs = len(set(record.get('organization_id', 'unknown') 
                                for record in market_data))
            applications_per_org = len(market_data) / max(unique_orgs, 1)
            
            if applications_per_org > 10:
                overview['competition_intensity'] = 'High'
            elif applications_per_org < 5:
                overview['competition_intensity'] = 'Low'
            else:
                overview['competition_intensity'] = 'Medium'
            
            return overview
            
        except Exception as e:
            self.logger.error(f"Error analyzing market overview: {e}")
            return {}

    def _identify_competitors(
        self,
        target_org: OrganizationProfile,
        market_data: List[Dict]
    ) -> List[CompetitorProfile]:
        """Identify and profile competing organizations."""
        try:
            # Group data by organization
            org_data = defaultdict(list)
            for record in market_data:
                org_id = record.get('organization_id', 'unknown')
                if org_id != 'unknown':
                    org_data[org_id].append(record)
            
            competitors = []
            target_focus_areas = set(getattr(target_org, 'focus_areas', []))
            
            for org_id, records in org_data.items():
                # Skip if this is the target organization
                target_id = getattr(target_org, 'id', 
                                  getattr(target_org, 'name', 'target'))
                if org_id == target_id:
                    continue
                
                # Analyze organization's grants
                competitor_profile = self._create_competitor_profile(
                    org_id, records, target_focus_areas
                )
                
                # Only include organizations with sufficient activity
                if competitor_profile.total_applications >= 3:
                    competitors.append(competitor_profile)
            
            # Sort by relevance (combination of focus area overlap and success)
            competitors.sort(
                key=lambda c: (
                    len(set(c.primary_focus_areas) & target_focus_areas) * 
                    c.success_rate
                ),
                reverse=True
            )
            
            return competitors[:20]  # Return top 20 competitors
            
        except Exception as e:
            self.logger.error(f"Error identifying competitors: {e}")
            return []

    def _create_competitor_profile(
        self,
        org_id: str,
        records: List[Dict],
        target_focus_areas: Set[str]
    ) -> CompetitorProfile:
        """Create detailed profile for a competitor organization."""
        try:
            total_applications = len(records)
            successful_apps = [r for r in records 
                             if r.get('outcome') in ['awarded', 'funded', 'approved']]
            success_rate = len(successful_apps) / total_applications
            
            # Calculate funding metrics
            total_funding = sum(r.get('amount_awarded', 0) for r in successful_apps)
            avg_grant_size = (total_funding / len(successful_apps) 
                            if successful_apps else 0)
            
            # Analyze focus areas
            focus_areas = Counter()
            for record in records:
                grant_info = record.get('grant', {})
                for area in grant_info.get('focus_areas', []):
                    focus_areas[area] += 1
            
            primary_focus_areas = [area for area, _ in focus_areas.most_common(5)]
            
            # Identify funding sources
            funding_sources = list(set(
                record.get('funder', 'Unknown') for record in successful_apps
            ))
            
            # Analyze success strategies
            success_strategies = self._identify_success_strategies(successful_apps)
            
            # Identify competitive advantages
            competitive_advantages = self._identify_competitive_advantages(
                records, target_focus_areas
            )
            
            # Recent wins (last 12 months)
            recent_cutoff = datetime.now() - timedelta(days=365)
            recent_wins = []
            for record in successful_apps:
                if record.get('award_date'):
                    try:
                        award_date = datetime.fromisoformat(str(record['award_date']))
                        if award_date > recent_cutoff:
                            recent_wins.append({
                                'grant_title': record.get('grant', {}).get('title', 'Unknown'),
                                'amount': record.get('amount_awarded', 0),
                                'funder': record.get('funder', 'Unknown'),
                                'date': record.get('award_date')
                            })
                    except:
                        pass
            
            org_name = records[0].get('organization_name', f'Organization_{org_id}')
            
            return CompetitorProfile(
                organization_id=org_id,
                organization_name=org_name,
                total_applications=total_applications,
                success_rate=success_rate,
                total_funding_won=total_funding,
                avg_grant_size=avg_grant_size,
                primary_focus_areas=primary_focus_areas,
                funding_sources=funding_sources,
                success_strategies=success_strategies,
                competitive_advantages=competitive_advantages,
                recent_wins=recent_wins
            )
            
        except Exception as e:
            self.logger.error(f"Error creating competitor profile: {e}")
            return CompetitorProfile(
                organization_id=org_id,
                organization_name=f'Organization_{org_id}',
                total_applications=0,
                success_rate=0.0,
                total_funding_won=0.0,
                avg_grant_size=0.0,
                primary_focus_areas=[],
                funding_sources=[],
                success_strategies=[],
                competitive_advantages=[],
                recent_wins=[]
            )

    def _identify_success_strategies(self, successful_apps: List[Dict]) -> List[str]:
        """Identify patterns in successful applications."""
        strategies = []
        
        if not successful_apps:
            return strategies
        
        # Analyze grant amounts
        amounts = [app.get('amount_awarded', 0) for app in successful_apps]
        avg_amount = np.mean(amounts)
        
        if avg_amount > 100000:
            strategies.append("Focuses on large-scale grants")
        elif avg_amount < 25000:
            strategies.append("Successful with smaller, targeted grants")
        
        # Analyze funders
        funders = [app.get('funder', '') for app in successful_apps]
        funder_counts = Counter(funders)
        
        if len(funder_counts) < len(successful_apps) * 0.7:
            strategies.append("Builds strong relationships with specific funders")
        
        # Analyze timing patterns
        submission_months = []
        for app in successful_apps:
            if app.get('submission_date'):
                try:
                    date = datetime.fromisoformat(str(app['submission_date']))
                    submission_months.append(date.month)
                except:
                    pass
        
        if submission_months:
            month_counts = Counter(submission_months)
            if max(month_counts.values()) > len(submission_months) * 0.4:
                strategies.append("Strategic timing of applications")
        
        # Analyze focus area concentration
        focus_areas = []
        for app in successful_apps:
            grant_info = app.get('grant', {})
            focus_areas.extend(grant_info.get('focus_areas', []))
        
        if focus_areas:
            area_counts = Counter(focus_areas)
            if len(area_counts) <= 3:
                strategies.append("Specialized expertise in key areas")
        
        return strategies

    def _identify_competitive_advantages(
        self,
        records: List[Dict],
        target_focus_areas: Set[str]
    ) -> List[str]:
        """Identify competitive advantages of the organization."""
        advantages = []
        
        # High success rate
        success_rate = len([r for r in records 
                          if r.get('outcome') in ['awarded', 'funded', 'approved']]) / len(records)
        if success_rate > 0.7:
            advantages.append("Exceptional success rate")
        
        # Consistent funding
        years = set()
        for record in records:
            if record.get('submission_date'):
                try:
                    date = datetime.fromisoformat(str(record['submission_date']))
                    years.add(date.year)
                except:
                    pass
        
        if len(years) >= 3:
            advantages.append("Sustained funding track record")
        
        # Focus area overlap with target
        org_focus_areas = set()
        for record in records:
            grant_info = record.get('grant', {})
            org_focus_areas.update(grant_info.get('focus_areas', []))
        
        overlap = len(org_focus_areas & target_focus_areas)
        if overlap >= 2:
            advantages.append("Competes in similar focus areas")
        
        # Large grant capability
        amounts = [record.get('amount_awarded', 0) for record in records 
                  if record.get('outcome') in ['awarded', 'funded', 'approved']]
        if amounts and max(amounts) > 250000:
            advantages.append("Capable of winning large grants")
        
        return advantages

    def _identify_market_opportunities(
        self,
        target_org: OrganizationProfile,
        market_data: List[Dict],
        competitors: List[CompetitorProfile]
    ) -> List[MarketOpportunity]:
        """Identify market opportunities based on competitive analysis."""
        opportunities = []
        
        try:
            # Analyze underserved niches
            opportunities.extend(
                self._find_underserved_niches(target_org, market_data, competitors)
            )
            
            # Identify emerging funders
            opportunities.extend(
                self._find_emerging_funders(market_data)
            )
            
            # Gap analysis opportunities
            opportunities.extend(
                self._find_gap_opportunities(target_org, competitors)
            )
            
            # Sort by estimated value and success probability
            opportunities.sort(
                key=lambda o: o.estimated_value * o.success_probability,
                reverse=True
            )
            
            return opportunities[:10]  # Return top 10 opportunities
            
        except Exception as e:
            self.logger.error(f"Error identifying opportunities: {e}")
            return []

    def _find_underserved_niches(
        self,
        target_org: OrganizationProfile,
        market_data: List[Dict],
        competitors: List[CompetitorProfile]
    ) -> List[MarketOpportunity]:
        """Find underserved market niches."""
        opportunities = []
        
        # Analyze focus area combinations
        target_areas = set(getattr(target_org, 'focus_areas', []))
        competitor_areas = set()
        for comp in competitors:
            competitor_areas.update(comp.primary_focus_areas)
        
        # Find areas where target org has presence but competitors are weak
        underserved_areas = target_areas - competitor_areas
        
        for area in underserved_areas:
            # Calculate opportunity metrics
            relevant_grants = [
                record for record in market_data
                if area in record.get('grant', {}).get('focus_areas', [])
            ]
            
            if relevant_grants:
                total_value = sum(
                    record.get('grant', {}).get('amount_typical', 0)
                    for record in relevant_grants
                )
                
                # Low competition = higher success probability
                competition_count = len([
                    comp for comp in competitors
                    if area in comp.primary_focus_areas
                ])
                
                if competition_count < 2:  # Low competition threshold
                    opportunities.append(MarketOpportunity(
                        opportunity_id=f"niche_{area}_{datetime.now().strftime('%Y%m%d')}",
                        opportunity_type="underserved_niche",
                        description=f"Underserved niche in {area} with limited competition",
                        estimated_value=total_value / len(relevant_grants),
                        competition_level="Low",
                        success_probability=0.7,
                        key_requirements=[f"Expertise in {area}", "Quality proposal"],
                        similar_organizations=[],
                        recommended_strategy=f"Focus on {area} specialization",
                        timeline="3-6 months"
                    ))
        
        return opportunities

    def _find_emerging_funders(self, market_data: List[Dict]) -> List[MarketOpportunity]:
        """Identify emerging funders with less competition."""
        opportunities = []
        
        # Analyze funder activity over time
        funder_timeline = defaultdict(list)
        for record in market_data:
            if record.get('submission_date'):
                try:
                    date = datetime.fromisoformat(str(record['submission_date']))
                    funder = record.get('funder', 'Unknown')
                    funder_timeline[funder].append(date)
                except:
                    pass
        
        # Identify funders with recent activity increase
        recent_cutoff = datetime.now() - timedelta(days=365)
        for funder, dates in funder_timeline.items():
            recent_activity = len([d for d in dates if d > recent_cutoff])
            total_activity = len(dates)
            
            if recent_activity >= 3 and recent_activity / total_activity > 0.5:
                # This funder is showing increased activity
                funder_grants = [
                    record for record in market_data
                    if record.get('funder') == funder
                ]
                
                avg_grant_size = np.mean([
                    record.get('grant', {}).get('amount_typical', 0)
                    for record in funder_grants
                ])
                
                if avg_grant_size > 0:
                    opportunities.append(MarketOpportunity(
                        opportunity_id=f"funder_{funder.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}",
                        opportunity_type="emerging_funder",
                        description=f"Emerging funder: {funder} showing increased activity",
                        estimated_value=avg_grant_size,
                        competition_level="Medium",
                        success_probability=0.6,
                        key_requirements=["Research funder priorities", "Tailor application"],
                        similar_organizations=[],
                        recommended_strategy="Early engagement with emerging funder",
                        timeline="6-12 months"
                    ))
        
        return opportunities[:3]  # Limit to top 3 emerging funders

    def _find_gap_opportunities(
        self,
        target_org: OrganizationProfile,
        competitors: List[CompetitorProfile]
    ) -> List[MarketOpportunity]:
        """Find opportunities where competitors are weak."""
        opportunities = []
        
        target_areas = set(getattr(target_org, 'focus_areas', []))
        
        # Analyze competitor weaknesses
        for comp in competitors[:5]:  # Focus on top 5 competitors
            comp_areas = set(comp.primary_focus_areas)
            
            # Find gaps in competitor's focus areas that align with target
            gaps = target_areas - comp_areas
            
            if gaps and comp.success_rate < 0.5:  # Competitor is struggling
                for gap_area in gaps:
                    opportunities.append(MarketOpportunity(
                        opportunity_id=f"gap_{gap_area}_{comp.organization_id}_{datetime.now().strftime('%Y%m%d')}",
                        opportunity_type="gap_analysis",
                        description=f"Gap in {gap_area} where {comp.organization_name} is weak",
                        estimated_value=comp.avg_grant_size,
                        competition_level="Medium",
                        success_probability=0.65,
                        key_requirements=[f"Strength in {gap_area}", "Strategic positioning"],
                        similar_organizations=[comp.organization_name],
                        recommended_strategy=f"Capitalize on competitor weakness in {gap_area}",
                        timeline="6-9 months"
                    ))
        
        return opportunities

    def _generate_strategic_recommendations(
        self,
        target_org: OrganizationProfile,
        competitors: List[CompetitorProfile],
        opportunities: List[MarketOpportunity]
    ) -> List[Dict[str, str]]:
        """Generate strategic recommendations based on analysis."""
        recommendations = []
        
        # Recommendation based on top competitors
        if competitors:
            top_competitor = competitors[0]
            recommendations.append({
                'type': 'competitive_positioning',
                'title': 'Learn from Top Performer',
                'description': f"Study {top_competitor.organization_name}'s success strategies: {', '.join(top_competitor.success_strategies)}",
                'priority': 'High',
                'timeline': '1-3 months'
            })
        
        # Recommendation based on opportunities
        if opportunities:
            top_opportunity = opportunities[0]
            recommendations.append({
                'type': 'opportunity_pursuit',
                'title': 'Pursue High-Value Opportunity',
                'description': f"Focus on {top_opportunity.description} with estimated value of ${top_opportunity.estimated_value:,.0f}",
                'priority': 'High',
                'timeline': top_opportunity.timeline
            })
        
        # Diversification recommendation
        target_areas = getattr(target_org, 'focus_areas', [])
        if len(target_areas) < 3:
            recommendations.append({
                'type': 'diversification',
                'title': 'Expand Focus Areas',
                'description': 'Consider expanding to additional focus areas to increase funding opportunities',
                'priority': 'Medium',
                'timeline': '6-12 months'
            })
        
        # Relationship building recommendation
        if competitors:
            common_funders = set()
            for comp in competitors[:3]:
                common_funders.update(comp.funding_sources)
            
            if common_funders:
                recommendations.append({
                    'type': 'relationship_building',
                    'title': 'Build Funder Relationships',
                    'description': f"Develop relationships with key funders: {', '.join(list(common_funders)[:3])}",
                    'priority': 'Medium',
                    'timeline': '3-6 months'
                })
        
        return recommendations

    def _analyze_competitive_positioning(
        self,
        target_org: OrganizationProfile,
        competitors: List[CompetitorProfile]
    ) -> Dict[str, Any]:
        """Analyze target organization's competitive position."""
        if not competitors:
            return {}
        
        positioning = {
            'market_rank': 'Unknown',
            'strengths': [],
            'weaknesses': [],
            'differentiation_opportunities': [],
            'competitive_score': 0.5
        }
        
        # For now, provide a basic analysis
        # In a real implementation, this would use target org's historical data
        
        target_areas = set(getattr(target_org, 'focus_areas', []))
        
        # Identify potential strengths
        unique_areas = target_areas - set().union(
            *[set(comp.primary_focus_areas) for comp in competitors]
        )
        if unique_areas:
            positioning['strengths'].append(f"Unique focus on {', '.join(unique_areas)}")
        
        # Identify potential weaknesses
        common_areas = set().intersection(
            *[set(comp.primary_focus_areas) for comp in competitors[:3]]
        )
        overlap = target_areas & common_areas
        if overlap:
            positioning['weaknesses'].append(f"High competition in {', '.join(overlap)}")
        
        # Differentiation opportunities
        if len(target_areas) > 3:
            positioning['differentiation_opportunities'].append(
                "Multi-disciplinary approach across diverse focus areas"
            )
        
        return positioning

    def _analyze_market_trends(self, market_data: List[Dict]) -> Dict[str, Any]:
        """Analyze market trends over time."""
        trends = {
            'funding_trends': {},
            'popular_areas': [],
            'emerging_themes': [],
            'seasonal_patterns': {}
        }
        
        if not market_data:
            return trends
        
        # Analyze trends by year
        yearly_data = defaultdict(lambda: {'count': 0, 'funding': 0})
        focus_area_trends = defaultdict(lambda: defaultdict(int))
        
        for record in market_data:
            if record.get('submission_date'):
                try:
                    date = datetime.fromisoformat(str(record['submission_date']))
                    year = date.year
                    
                    yearly_data[year]['count'] += 1
                    yearly_data[year]['funding'] += record.get('grant', {}).get('amount_typical', 0)
                    
                    # Track focus area trends
                    for area in record.get('grant', {}).get('focus_areas', []):
                        focus_area_trends[year][area] += 1
                        
                except:
                    pass
        
        # Calculate year-over-year growth
        years = sorted(yearly_data.keys())
        if len(years) >= 2:
            latest_year = years[-1]
            previous_year = years[-2]
            
            count_growth = (
                (yearly_data[latest_year]['count'] - yearly_data[previous_year]['count']) /
                yearly_data[previous_year]['count'] * 100
                if yearly_data[previous_year]['count'] > 0 else 0
            )
            
            trends['funding_trends'] = {
                'year_over_year_growth': f"{count_growth:.1f}%",
                'latest_year_grants': yearly_data[latest_year]['count'],
                'total_funding_latest': yearly_data[latest_year]['funding']
            }
        
        return trends

    def export_competitive_analysis(
        self,
        analysis_results: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """Export competitive analysis results to JSON."""
        try:
            if output_path:
                export_path = output_path
            else:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_path = str(self.data_dir / f"competitive_analysis_{timestamp}.json")
            
            # Add metadata
            export_data = {
                'analysis_results': analysis_results,
                'generated_at': datetime.now().isoformat(),
                'analysis_type': 'competitive_landscape',
                'version': '1.0'
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Competitive analysis exported to {export_path}")
            return export_path
            
        except Exception as e:
            self.logger.error(f"Error exporting analysis: {e}")
            return ""
