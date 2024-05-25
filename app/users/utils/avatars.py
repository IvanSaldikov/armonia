from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image
from users.models import User


class AvatarUtils:
    """Class for working with Avatars"""

    _size_avatar_small = (200, 200)
    _size_avatar_big = (600, 600)

    @classmethod
    def make_thumb_for_avatar_big(cls, instance: User):
        cls._make_thumb_for_image(instance=instance, is_big_avatar=True)

    @classmethod
    def make_thumb_for_avatar_small(cls, instance: User):
        cls._make_thumb_for_image(instance=instance, is_big_avatar=False)

    @classmethod
    def _make_thumb_for_image(cls, instance: User, is_big_avatar: bool):
        file = instance.avatar_big if is_big_avatar else instance.avatar_small
        size = cls._size_avatar_big if is_big_avatar else cls._size_avatar_small
        image = Image.open(file)
        image.thumbnail(size, Image.Resampling.LANCZOS)
        thumb_io = BytesIO()
        image.save(thumb_io, image.format, quality=80)
        file.save(file.name, ContentFile(thumb_io.getvalue()), save=False)
