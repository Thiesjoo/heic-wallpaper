from django.test import TestCase
from wallpaper.services.s3_service import allowed_file, determine_type_from_extension, ALLOWED_EXTENSIONS
from wallpaper.models import WallpaperType

class WallpaperServiceTests(TestCase):
    def test_allowed_file(self):
        self.assertTrue(allowed_file("test.png"))
        self.assertTrue(allowed_file("test.jpg"))
        self.assertTrue(allowed_file("test.jpeg"))
        self.assertTrue(allowed_file("test.heic"))
        self.assertTrue(allowed_file("test.heif"))
        self.assertFalse(allowed_file("test.gif"))
        self.assertFalse(allowed_file("test.txt"))

    def test_determine_type_from_extension(self):
        self.assertEqual(determine_type_from_extension("heic"), WallpaperType.TIME_BASED)
        self.assertEqual(determine_type_from_extension("heif"), WallpaperType.TIME_BASED)
        self.assertEqual(determine_type_from_extension("png"), WallpaperType.GENERIC)
        self.assertEqual(determine_type_from_extension("jpg"), WallpaperType.GENERIC)

    def test_allowed_extensions_mapping(self):
        # heic files should be allowed with image/heic or image/heif
        self.assertIn("image/heic", ALLOWED_EXTENSIONS["heic"])
        self.assertIn("image/heif", ALLOWED_EXTENSIONS["heic"])
        # heif files should be allowed with image/heic or image/heif
        self.assertIn("image/heic", ALLOWED_EXTENSIONS["heif"])
        self.assertIn("image/heif", ALLOWED_EXTENSIONS["heif"])
