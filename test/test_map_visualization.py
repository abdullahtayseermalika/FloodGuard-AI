
import tempfile
from pathlib import Path

from src.map_visualization import create_flood_map


def main():
    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "test_map.html"

        result = create_flood_map(
            output_html=output_path,
        )

        assert result.exists()
        assert result.stat().st_size > 0

        html = result.read_text(encoding="utf-8")
        assert "Eastern Odisha study area" in html
        assert "OpenStreetMap" in html

    print("PASS: Interactive map HTML generated")
    print("PASS: Study-area marker included")
    print("NOTE: No flood polygons are shown in this test.")


if __name__ == "__main__":
    main()
