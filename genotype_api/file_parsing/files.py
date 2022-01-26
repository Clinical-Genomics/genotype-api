from pathlib import Path
from fastapi import HTTPException, status


def check_file(file_path: str, extension: str) -> Path:
    """Check file and file extension"""

    file_name: Path = Path(file_path)
    if not file_name.name.endswith(extension):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Please select a valid {extension} file for upload",
        )
    return file_name
