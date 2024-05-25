import pathlib
import random
from typing import TYPE_CHECKING

from common.consts import FilesStorage
from django.conf import settings
from django.core.files.storage import storages
from django.template.defaultfilters import filesizeformat
from rest_framework.exceptions import ValidationError
from users.consts import AvatarType

if TYPE_CHECKING:
    from users.models import User


class UploadUtils:
    # 2.5MB - 2621440
    # 5MB - 5242880
    # 10MB - 10485760
    # 20MB - 20971520
    # 50MB - 5242880
    # 100MB 104857600
    # 250MB - 214958080
    # 500MB - 429916160
    MAX_UPLOAD_SIZE = "5242880"

    SUPPORTED_IMG_FILE_EXTENSIONS = [
        ".png",
        ".jpg",
        ".jpeg",
    ]
    SUPPORTED_SOLUTION_FILE_EXTENSIONS = [
        ".png",
        ".jpg",
        ".jpeg",
        ".pdf",
        ".zip",
        ".rar",
    ]

    @classmethod
    def _get_image_path_for_user_avatars(
        cls, instance: "User", filename: str, user_avatar_type: AvatarType
    ):
        file_ext = cls.get_file_extension(filename)
        return "img/users_avatars/{}/{}/{}{}".format(
            str(instance.uuid),
            user_avatar_type.value,
            str(random.randint(3, 999999999999)),
            file_ext,
        )

    @classmethod
    def get_image_path_for_user_avatars_big(cls, instance: "User", filename: str):
        return cls._get_image_path_for_user_avatars(
            instance=instance, filename=filename, user_avatar_type=AvatarType.BIG
        )

    @classmethod
    def get_image_path_for_user_avatars_small(cls, instance: "User", filename: str):
        return cls._get_image_path_for_user_avatars(
            instance=instance, filename=filename, user_avatar_type=AvatarType.SMALL
        )

    @staticmethod
    def get_file_extension(filename: str):
        return pathlib.Path(filename).suffix

    @staticmethod
    def validate_solution_file_max_size(value):
        max_file_size = UploadUtils.MAX_UPLOAD_SIZE
        if value.size > int(max_file_size):
            raise ValidationError(
                f"File too large. Size should not exceed {filesizeformat(max_file_size)}."
            )

    @staticmethod
    def select_storage():
        return (
            storages[FilesStorage.MINIO.value]
            if settings.DEBUG
            else storages[FilesStorage.GOOGLE.value]
        )
