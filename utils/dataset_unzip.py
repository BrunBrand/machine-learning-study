from pathlib import Path
import pandas as pd
import requests
import os
import zipfile
from typing import List, Dict, Union


def download_dataset(url, dest_dir: Union[str, Path], file_name) -> Path:
    dest_dir = Path(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    output_path = dest_dir / file_name

    if os.path.exists(output_path):
        print(f"dataset already exists at {output_path}")
        return Path(output_path)

    try:
        with requests.get(url, stream=True, allow_redirects=True) as r:
            r.raise_for_status()

            total_size = int(r.headers.get("content-length", 0))
            block_size = 8192

            with open(output_path, "wb") as f:
                downloaded_size = 0
                for chunk in r.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress_percent = (
                            (downloaded_size / total_size) * 100 if total_size else 0
                        )
                        print(f"\rDownloaed ({progress_percent:.2f}%)", end="")

            print(f"\nSuccessfully downloaded '{file_name}' to '{output_path}'.")
    except requests.exceptions.RequestException as e:
        print(f"Error during download: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return Path(output_path)


def unzip_dataset(
    file_path, contents: List[str] | None = None
) -> Dict[str, pd.DataFrame]:
    dataframes = {}
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            zip_contents = zf.namelist()
            contents = contents if contents else zip_contents
            for content in contents:
                if content in zip_contents:
                    with zf.open(content) as f_zf:
                        dataframes[content] = pd.read_csv(f_zf)
    except zipfile.BadZipFile:
        print(f"Erro: {file_path} not valid ZIP file or corrupted")
    except Exception as e:
        print(f"An error occurred: {e}")
    return dataframes


def dataset_info_from_zip(file_path) -> List[str]:
    with zipfile.ZipFile(file_path, "r") as zf:
        return zf.namelist()
