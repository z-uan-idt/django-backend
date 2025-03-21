from django.core.exceptions import ValidationError


class ImageHelper:
    image_extension = ["jpg", "jpeg", "png", "gif", "webp"]
    image_format_mapping = {
        "JPEG": ".jpg",
        "JPG": ".jpg",
        "PNG": ".png",
        "GIF": ".gif",
        "WEBP": ".webp",
    }

    @staticmethod
    def get_image_format(original_format: str, default=".jpg"):
        return ImageHelper.image_format_mapping.get(original_format, default)

    @staticmethod
    def create_thumbnail(image_file, size=(150, 150)):
        """Tạo thumbnail giữ nguyên định dạng gốc"""
        from PIL import Image
        from io import BytesIO
        from django.core.files.base import ContentFile

        # Mở file hình ảnh
        img = Image.open(image_file)

        # Lưu định dạng gốc
        original_format = img.format

        # Xử lý animation cho GIF hoặc WebP
        is_animated = getattr(img, "is_animated", False)

        # Chuyển sang RGB nếu cần, giữ lại alpha nếu có
        if img.mode == "RGBA":
            # Có alpha channel, giữ nguyên
            pass
        elif img.mode not in ("L", "RGB"):
            img = img.convert("RGB")

        # Resize hình ảnh
        img.thumbnail(size, Image.Resampling.LANCZOS)

        output = BytesIO()

        # Lưu với định dạng gốc
        if original_format == "JPEG" or original_format == "JPG":
            img.save(output, format="JPEG", quality=85)
        elif original_format == "PNG":
            img.save(output, format="PNG", optimize=True)
        elif original_format == "GIF":
            # Nếu là GIF động, xử lý đặc biệt
            if is_animated:
                # Giữ frame đầu tiên
                img.save(output, format="GIF")
            else:
                img.save(output, format="GIF")
        elif original_format == "WEBP":
            # WebP cần thư viện Pillow mới hơn
            img.save(output, format="WEBP", quality=85)
        else:
            # Fallback sang JPEG nếu không xác định được
            img.save(output, format="JPEG", quality=85)

        output.seek(0)
        return ContentFile(output.getvalue())

    @staticmethod
    def model_validate_image(fieldfile_obj):
        """Kiểm tra file có phải là hình ảnh hợp lệ không"""
        filesize = fieldfile_obj.size
        megabyte_limit = 5.0
        if filesize > megabyte_limit * 1024 * 1024:
            raise ValidationError(f"Kích thước tối đa cho phép là {megabyte_limit}MB")

        import imghdr

        valid_image_types = ["jpeg", "jpg", "png", "gif", "bmp", "webp"]
        file_type = imghdr.what(fieldfile_obj)
        if file_type not in valid_image_types:
            raise ValidationError("File tải lên không phải là hình ảnh hợp lệ.")
