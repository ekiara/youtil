"""
youtil.py
~~~~~~~~~~~~~~~~

Helper utilities for downloading and processing Youtube videos

# Example usage: ## TODO
- TODO: Add the ability to invoke on commandline and convert all files in current directory:
`python ./youtil.py --batch-convert`

"""
import datetime
import glob
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Union

import yt_dlp


class Youtil:
    def __init__(self):
        self.current_working_directory = os.getcwd()

    def get_new_filename(self, filename: str, fmt: str) -> str:
        """Cleans up an file name to make it more consistent and script friendly.

        Args:
          filename: The file name to clean up.

        Returns:
          A cleaned-up file name.
        """
        new_filename: str = filename
        replacements = {
            "(Official Video)": "",
            "[Official Music Video]": "",
            "(Official Music Video)": "",
            "(Official Live Video)": "",
            " Part ": "-",
            " (Interlude) ": "-interlude-",
            " (Feat. ": "-feat-",
            " (feat. ": "-feat-",
            " feat. ": "-feat-",
            " ft. ": "-feat-",
            " w⧸ ": "-with-",
            " & ": "-and-",
            " + ": "-and-",
        }
        for old_text, new_text in replacements.items():
            new_filename = new_filename.replace(old_text, new_text)

        # Remove extra spaces and punctuation.
        new_filename = re.sub(r" +", " ", new_filename)
        new_filename = new_filename.strip()
        new_filename = new_filename.replace(",", "-")
        new_filename = new_filename.replace("(", "")
        new_filename = new_filename.replace(")", "")
        new_filename = new_filename.replace("[", "")
        new_filename = new_filename.replace("]", "")
        new_filename = new_filename.replace(" - ", "-")
        new_filename = new_filename.replace(" – ", "-")
        new_filename = new_filename.replace(" ", "")

        # Fixing Youtube video code
        new_filename = (
            new_filename[:-16].strip().lower().replace(" ", "-")
            + "__"
            + new_filename[-16:]
        )

        # Replace file extension with new extension determined
        # by `fmt` attribute provided to this method (i.e. "mp3")
        base_filename = os.path.splitext(new_filename)[0]
        new_filename = ".".join([base_filename, fmt])

        return new_filename

    def convert_to_mp3(self, filename: str) -> Dict[str, Union[str, bool, None]]:
        """Convert a file to and mp3

        Args:
          filename: The file name to convert

        Returns:
          A result dictionary with details of the converted file

        If conversion fails then "successfully_converted" is False
        and "error_code" is the error that occured.

        If conversion is successful then "successfully_converted" is True
        and "error_code" is None

        If converted file path already exists then skip and return the
        error message: CONVERTED_FILE_PATH_ALREADY_EXISTS

        Error messages:
        CONVERTED_FILE_PATH_ALREADY_EXISTS
        SOURCE_FILE_DOES_NOT_EXIST
        FILESYSTEM_ERROR (NO SPACE ON DISK?)
        """
        new_filename = self.get_new_filename(filename=filename, fmt="mp3")
        successfully_converted = True
        error_code = None

        # Run ffmpeg conversion
        command_string = (
            f'ffmpeg -i "{filename}" -vn -ab 128k -ar 44100 -y "{new_filename}"'
        )
        subprocess.run([command_string], shell=True)

        output: Dict[str, Union[str, bool, None]] = {
            "original_filename": filename,
            "new_filename": new_filename,
            "successfully_converted": successfully_converted,
            "error_code": error_code,
        }

        return output

    def batch_convert_to_mp3(
        self, filename_list: List[str]
    ) -> List[Dict[str, Union[str, bool, None]]]:
        """Batch convert multiple files to mp3

        Args:
          filename_list: List of file names to convert

        Returns:
          A list of dictionaries with details of each converted file
        """
        output = []
        for filename in filename_list:
            result = self.convert_to_mp3(filename)
            output.append(result)

        return output

    def download_video(self, url) -> Dict[str, int]:
        """Use the yt-dlp tool to download videos from Youtube

        Args:
          filename_list: List of file names to convert

        Returns:
          A result dictionary in the format below:
          ```
            {
              "url": url,
              "filename": "filename",
              "filesize": "filesize",
              "title": "title",
              "fulltitle": "fulltitle",
              "youtube_id": "youtube_id",
              "duration": "duration",
              "timestamp": "timestamp",
            }
          ```
        """
        yd_opts = {
            "format": "best",
            "get_info": True,
        }
        with yt_dlp.YoutubeDL(yd_opts) as yd:
            video_info: Optional[Dict[str, Any]] = yd.extract_info(url, download=True)

        now = datetime.datetime.now()
        timestamp = now.timestamp()
        output = {}
        if video_info:
            youtube_id = video_info["id"]
            filename_search_string = f"*{youtube_id}*"
            filename = glob.glob(filename_search_string)[0]
            output = {
                "url": url,
                "filename": filename,
                "filesize": video_info["filesize_approx"],
                "title": video_info["title"],
                "fulltitle": video_info["fulltitle"],
                "youtube_id": youtube_id,
                "duration": video_info["duration"],
                "timestamp": timestamp,
            }

        return output

    def batch_download_video(self, url_list: List[str]) -> List[Dict[str, int]]:
        """Batch download multiple videos from Youtube

        Args:
          url_list: List of Youtube video URLs

        Returns:
          A list of result dictionaries with details of each download in the
          format returned by the .download_video() method.
        """
        output = []
        for url in url_list:
            result = self.download_video(url=url)
            output.append(result)

        return output


if __name__ == "__main__":
    yt = Youtil()
    download_output = yt.download_video(url="https://www.youtube.com/watch?v=UYIAfiVGluk")
    print(download_output)
    convert_output = yt.convert_to_mp3(download_output["filename"])
    print(convert_output)
