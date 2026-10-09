
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def save_ndwi_preview(ndwi, output_path):
    """
    Save an NDWI preview image.

    This displays the index only; it does not prove that
    any pixel is floodwater.
    """
    ndwi = np.asarray(ndwi, dtype=np.float32)

    if ndwi.ndim != 2:
        raise ValueError("NDWI must be a two-dimensional array.")

    if not np.isfinite(ndwi).any():
        raise ValueError("NDWI contains no valid pixels.")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(ndwi, cmap="BrBG", vmin=-1, vmax=1)
    ax.set_title("NDWI Preview — Preliminary Water Index")
    ax.set_axis_off()
    fig.colorbar(image, ax=ax, label="NDWI")
    fig.tight_layout()
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return output_path
