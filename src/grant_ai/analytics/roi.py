"""ROI analytics and reporting for Grant Research AI."""

import logging

logger = logging.getLogger(__name__)

def track_roi(grant_id: str, amount_awarded: float, amount_requested: float) -> dict:
    """Track ROI for a grant application."""
    try:
        roi = (amount_awarded / amount_requested) if amount_requested else 0.0
        logger.info("ROI tracked for grant %s: %.2f", grant_id, roi)
        return {"grant_id": grant_id, "roi": roi}
    except Exception as e:
        logger.error("ROI tracking failed for grant %s: %s", grant_id, e, exc_info=True)
        return {"grant_id": grant_id, "roi": 0.0, "error": str(e)}

# TODO: Implement ROI visualization and export
