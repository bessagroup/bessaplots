import logging

import matplotlib.pyplot as plt

import bessaplots  # noqa

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_style():
    # Print available styles to debug if needed
    # logger.info(f"Available styles: {plt.style.available}")

    # Check if 'bessaplots' is available
    if "bessaplots" not in plt.style.available:
        logger.error("Style 'bessaplots' not found in plt.style.available")
        return False

    # Use the style
    try:
        plt.style.use("bessaplots")
        logger.info("Successfully applied style 'bessaplots'")
    except Exception as e:
        logger.error(f"Failed to use style 'bessaplots': {e}")
        return False

    # Check settings
    figsize = plt.rcParams["figure.figsize"]
    bbox = plt.rcParams["savefig.bbox"]

    logger.info(f"figure.figsize: {figsize}")
    logger.info(f"savefig.bbox: {bbox}")

    expected_figsize = [3.3, 2.5]
    expected_bbox = "tight"

    if figsize != expected_figsize:
        logger.error(
            f"Mismatch in figure.figsize: expected {expected_figsize}, "
            f"got {figsize}"
        )
        return False

    if bbox != expected_bbox:
        logger.error(
            f"Mismatch in savefig.bbox: expected {expected_bbox}, got {bbox}"
        )
        return False

    logger.info("Verification passed!")
    return True


if __name__ == "__main__":
    import sys

    success = verify_style()
    sys.exit(0 if success else 1)
