import os
import time
import typing

import httpx
from django.conf import settings
from rest_framework import status

from services.stdiff.exceptions import PresetAlreadyExists

if typing.TYPE_CHECKING:
    from PIL import Image

from config.logger import get_module_logger

logger = get_module_logger("stdiff_service")


class StDiff:
    url = "https://stdiff.io"

    def __init__(self):
        api_key = os.environ.get('ARMONIA_STDIFF_API_KEY', None)
        if not api_key:
            raise Exception("No API Key for STDIFF was set in STDIFF_API_KEY env variable")
        self.headers = {'Token': api_key}

    def create_copy_of_preset(self, preset_name_to_copy: str, new_preset_name: str, new_prompt: str) -> dict | None:
        data = {
            "preset_name": preset_name_to_copy,
            "new_preset_name": new_preset_name,
            "new_prompt": new_prompt,
            }
        try:
            ret = self._make_request(uri="/api/presets/copy/", params=data, post_or_get="post")
            return ret
        except Exception as e:
            if "already exists" in str(e):
                raise PresetAlreadyExists
            return None

    def run_preset2image(self,
                         preset_name_to_run: str,
                         seed: str = None,
                         country: str = None,
                         ) -> str:
        data = {
            "preset_name": preset_name_to_run,
            "seed": seed,
            "country": country,
            }
        ret = self._make_request(uri="/api/preset2image", params=data, post_or_get="post")
        return ret["task_id"]

    def wait_until_image_generated_and_get_image_url(self,
                                                     task_id: str,
                                                     ) -> str | None:
        data = {
            "task_id": task_id,
            }
        i = 0
        while i <= 300:
            logger.info(f"Getting image status for {task_id=}. Iteration #: {i + 1}")
            ret = self._make_request(uri="/api/preset2image", params=data, post_or_get="get")
            image_url = ret["image_url"]
            logger.info(f"Image URL for {task_id=}: {image_url}")
            if image_url:
                logger.info(f"Returning image URL for {task_id=}: {image_url}")
                return image_url
            sleep_time_secs = 10
            logger.info(f"Sleeping for {sleep_time_secs} seconds to get Image URL for {task_id=}...")
            time.sleep(sleep_time_secs)
            i += 1
            if settings.DEBUG:
                return None

    def download_image_based_on_url(self, image_url: str) -> "Image":
        from io import BytesIO
        resp = httpx.get(image_url, params={}, headers=self.headers)
        return BytesIO(resp.content)

    def _make_request(self,
                      uri: str,
                      params: dict,
                      post_or_get: str = "get",
                      expected_status_code: int = status.HTTP_200_OK,
                      ) -> dict:
        url = f'{self.url}{uri}'
        if post_or_get.lower() == "get":
            r = httpx.get(url, params=params, headers=self.headers)
        else:
            r = httpx.post(url, data=params, headers=self.headers)
        if r.status_code != expected_status_code:
            raise Exception(f"Error while trying to make a request to url {url}: {str(r.text)}")
        return r.json()
