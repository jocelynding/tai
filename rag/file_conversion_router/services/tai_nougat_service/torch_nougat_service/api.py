from pathlib import Path

from ..config_nougat.nougat_config import NougatConfig
from . import run_nougat


def convert_pdf_to_mmd(input_pdf_path: Path, output_dir_path: Path) -> None:
    config = NougatConfig(
        pdf_paths=[input_pdf_path],
        output_dir=output_dir_path,
    )
    run_nougat(config)
