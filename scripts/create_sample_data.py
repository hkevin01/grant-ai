#!/usr/bin/env python3
"""
Sample data generation script for Grant AI application.
Creates sample predictive grants and enhanced past grants data.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from grant_ai.models.enhanced_past_grant import (
    EnhancedPastGrant,
    create_enhanced_sample_past_grants,
)
from grant_ai.models.predictive_grant import (
    PredictiveGrant,
    PredictiveGrantDatabase,
    PredictiveStatus,
    create_sample_predictive_grants,
)


def create_sample_data():
    """Create and save sample data for both tabs."""
    print("🔄 Creating sample data...")
    
    # Create predictive grants sample data
    print("📊 Creating predictive grants...")
    predictive_db = PredictiveGrantDatabase()
    sample_predictive_grants = create_sample_predictive_grants()
    
    for grant in sample_predictive_grants:
        predictive_db.add_grant(grant)
    
    print(f"✅ Created {len(sample_predictive_grants)} predictive grants")
    
    # Create enhanced past grants sample data
    print("📚 Creating enhanced past grants...")
    sample_past_grants = create_enhanced_sample_past_grants()
    
    print(f"✅ Created {len(sample_past_grants)} enhanced past grants")
    
    # Create sample document directories (for demo purposes)
    data_dir = project_root / "data" / "sample_documents"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample documents
    for grant in sample_past_grants:
        for document in grant.documents:
            # Create a simple text file for each document
            doc_path = data_dir / f"{document.name.replace(' ', '_')}.txt"
            with open(doc_path, 'w') as f:
                f.write(f"Sample document for grant: {grant.title}\n")
                f.write(f"Document type: {document.document_type.value}\n")
                f.write(f"Description: {document.description}\n")
                f.write("\nThis is a sample document for demonstration purposes.\n")
            
            # Update document path to the actual created file
            document.file_path = str(doc_path)
    
    print(f"📁 Created sample documents in {data_dir}")
    
    print("🎉 Sample data creation complete!")
    return sample_predictive_grants, sample_past_grants


if __name__ == "__main__":
    create_sample_data()
