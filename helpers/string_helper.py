import re


def normalize_vietnamese_string(text):
    """
    Chuẩn hóa chuỗi tiếng Việt từ dạng Unicode escape sequences về dạng UTF-8 readable
    """
    if isinstance(text, str):
        # Nếu chuỗi đã ở dạng Unicode escape, chuyển về dạng UTF-8 readable
        try:
            # Thử decode từ Unicode escape nếu cần
            if "\\u" in text:
                # Xử lý trường hợp chuỗi đã bị escape
                text = text.encode("utf-8").decode("unicode_escape")
        except (UnicodeDecodeError, UnicodeEncodeError):
            # Nếu có lỗi, giữ nguyên chuỗi ban đầu
            pass

    return text


def unaccent_vn(text: str) -> str:
    if not isinstance(text, str):
        return text

    translation_table = str.maketrans(
        "áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựíìỉĩịýỳỷỹỵđ"
        "ÁÀẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÉÈẺẼẸÊẾỀỂỄỆÓÒỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÚÙỦŨỤƯỨỪỬỮỰÍÌỈĨỊÝỲỶỸỴĐ",
        "aaaaaaaaaaaaaaaaaeeeeeeeeeeeooooooooooooooooouuuuuuuuuuuiiiiiyyyyyd"
        "AAAAAAAAAAAAAAAAAEEEEEEEEEEEOOOOOOOOOOOOOOOOOUUUUUUUUUUUIIIIIYYYYYD",
    )
    return text.translate(translation_table)


def remove_vietnamese_tones(text: str) -> str:
    text = re.sub(r"[àáạảãâầấậẩẫăằắặẳẵ]", "a", text)
    text = re.sub(r"[èéẹẻẽêềếệểễ]", "e", text)
    text = re.sub(r"[ìíịỉĩ]", "i", text)
    text = re.sub(r"[òóọỏõôồốộổỗơờớợởỡ]", "o", text)
    text = re.sub(r"[ùúụủũưừứựửữ]", "u", text)
    text = re.sub(r"[ỳýỵỷỹ]", "y", text)
    text = re.sub(r"[đ]", "d", text)
    text = re.sub(r"[ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]", "A", text)
    text = re.sub(r"[ÈÉẸẺẼÊỀẾỆỂỄ]", "E", text)
    text = re.sub(r"[ÌÍỊỈĨ]", "I", text)
    text = re.sub(r"[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]", "O", text)
    text = re.sub(r"[ÙÚỤỦŨƯỪỨỰỬỮ]", "U", text)
    text = re.sub(r"[ỲÝỴỶỸ]", "Y", text)
    text = re.sub(r"[Đ]", "D", text)
    text = re.sub(r"[\u0300\u0301\u0303\u0309\u0323]", "", text)
    text = re.sub(r"[\u02C6\u0306\u031B]", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text.strip()
