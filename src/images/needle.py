import math
import io
import logging
from PIL import Image, ImageDraw

LOG = logging.getLogger("uvicorn")

RESIZE_FACTOR = 4
CACHED_BACKGROUND = Image.open("data/needle_background.png")
CACHED_BACKGROUND = CACHED_BACKGROUND.resize(
    (
        CACHED_BACKGROUND.width // RESIZE_FACTOR,
        CACHED_BACKGROUND.height // RESIZE_FACTOR,
    )
)
CACHED_NEEDLE = Image.open("data/needle.png")
CACHED_NEEDLE = CACHED_NEEDLE.resize(
    (CACHED_NEEDLE.width // RESIZE_FACTOR, CACHED_NEEDLE.height // RESIZE_FACTOR)
)

LOG.info(f"background image loaded, size: {CACHED_BACKGROUND.size}")


def get_text(abs_score):
    if abs_score <= 2:
        return "Lean "
    if abs_score <= 5:
        return "Likely "
    return "Very Likely"

def get_needle_into_buffer(net_score):
    buffer = io.BytesIO()
    abs_score = abs(net_score)
    scaling_factor = 0.0 + abs_score * 0.3 if abs_score < 4 else 1
    im = Image.alpha_composite(
        CACHED_BACKGROUND,
        CACHED_NEEDLE.rotate(
            180 * math.atan(net_score) / math.pi,
            center=(1500 // RESIZE_FACTOR, 1465 // RESIZE_FACTOR),
        ),
    )
    
    im.save(buffer, "png")
    buffer.seek(0)
    LOG.debug(f"Saved image to buffer, size: {im.size}")

    return buffer
