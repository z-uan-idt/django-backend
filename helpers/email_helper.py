from typing import List, Optional, Dict, Union, Any

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class EmailHelper:
    """
    Lớp hỗ trợ gửi email trong Django.
    Cung cấp các phương thức để gửi email văn bản thuần túy, email HTML, và email có đính kèm.
    Hỗ trợ đầy đủ nội dung tiếng Việt với mã hóa UTF-8.
    """

    @staticmethod
    def send_email(
        subject: str,
        recipients: List[str],
        message: str,
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Union[str, bytes]]]] = None,
        html_message: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Gửi email với các tham số được cung cấp.

        Tham số:
            subject: Tiêu đề email
            recipients: Danh sách địa chỉ email người nhận
            message: Nội dung tin nhắn dạng văn bản thuần túy
            from_email: Địa chỉ email người gửi (mặc định là settings.DEFAULT_FROM_EMAIL)
            cc: Danh sách địa chỉ email CC
            bcc: Danh sách địa chỉ email BCC
            reply_to: Danh sách địa chỉ email Reply-To
            attachments: Danh sách các từ điển chứa thông tin đính kèm
                Mỗi từ điển nên có:
                - 'filename': Tên file
                - 'content': Nội dung file dạng bytes hoặc chuỗi
                - 'mimetype': Loại MIME của file đính kèm (tùy chọn)
            html_message: Phiên bản HTML của tin nhắn (tùy chọn)
            fail_silently: Có nên bỏ qua lỗi khi gửi hay không

        Trả về:
            bool: True nếu email được gửi thành công, False nếu không

        Ví dụ:
            ```
            EmailHelper.send_email(
                subject="Chào mừng bạn đến với nền tảng của chúng tôi",
                recipients=["user@example.com"],
                message="Chào mừng bạn đến với nền tảng của chúng tôi!",
                html_message="<h1>Chào mừng</h1><p>Chào mừng bạn đến với nền tảng của chúng tôi!</p>",
                attachments=[{
                    'filename': 'tailieu.pdf',
                    'content': pdf_content,
                    'mimetype': 'application/pdf'
                }]
            )
            ```
        """

        if from_email is None:
            from_email = getattr(
                settings,
                "DEFAULT_FROM_EMAIL",
                getattr(settings, "EMAIL_HOST_USER", "noreply@example.com"),
            )

        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipients,
            cc=cc or [],
            bcc=bcc or [],
            reply_to=reply_to or [],
        )

        if html_message:
            email.attach_alternative(html_message, "text/html")

        if attachments:
            for attachment in attachments:
                filename = attachment.get("filename")
                content = attachment.get("content")
                mimetype = attachment.get("mimetype")

                if filename and content:
                    if isinstance(content, str):
                        content = content.encode("utf-8")

                    if mimetype:
                        email.attach(filename, content, mimetype)
                    else:
                        email.attach(filename, content)

        try:
            sent = email.send(fail_silently=fail_silently)
            if sent:
                print(f"Đã gửi email thành công tới {', '.join(recipients)}")
            else:
                print(f"Không thể gửi email tới {', '.join(recipients)}")
            return sent > 0
        except Exception as e:
            print(f"Lỗi khi gửi email: {str(e)}")
            if not fail_silently:
                raise
            return False

    @classmethod
    def send_template_email(
        cls,
        subject: str,
        recipients: List[str],
        template_name: str,
        context: Dict[str, Any],
        from_email: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        reply_to: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Union[str, bytes]]]] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Gửi email sử dụng template Django.

        Tham số:
            subject: Tiêu đề email
            recipients: Danh sách địa chỉ email người nhận
            template_name: Tên của template sử dụng (không có phần mở rộng)
            context: Từ điển các biến context cho template
            from_email: Địa chỉ email người gửi
            cc: Danh sách địa chỉ email CC
            bcc: Danh sách địa chỉ email BCC
            reply_to: Danh sách địa chỉ email Reply-To
            attachments: Danh sách các từ điển chứa thông tin đính kèm
            fail_silently: Có nên bỏ qua lỗi khi gửi hay không

        Trả về:
            bool: True nếu email được gửi thành công, False nếu không

        Lưu ý:
            Phương thức này tìm kiếm template ở các vị trí sau:
            - templates/emails/{template_name}.html cho phiên bản HTML
            - templates/emails/{template_name}.txt cho phiên bản văn bản

        Ví dụ:
            ```
            EmailHelper.send_template_email(
                subject="Chào mừng đến với nền tảng của chúng tôi",
                recipients=["user@example.com"],
                template_name="welcome_email",
                context={"username": "nguyen_van_a", "account_url": "https://example.com/account"}
            )
            ```
        """
        try:
            html_message = None
            try:
                html_message = render_to_string(f"emails/{template_name}.html", context)
            except Exception as e:
                print(f"Không tìm thấy template HTML hoặc lỗi khi render: {str(e)}")

            try:
                text_message = render_to_string(f"emails/{template_name}.txt", context)
            except Exception:
                if html_message:
                    text_message = strip_tags(html_message)
                else:
                    raise ValueError("Không thể render cả template HTML và văn bản")

            return cls.send_email(
                subject=subject,
                recipients=recipients,
                message=text_message,
                from_email=from_email,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
                attachments=attachments,
                html_message=html_message,
                fail_silently=fail_silently,
            )
        except Exception as e:
            print(f"Lỗi khi gửi email template: {str(e)}")
            if not fail_silently:
                raise
            return False

    @classmethod
    def send_mass_emails(
        cls, email_messages: List[Dict[str, Any]], fail_silently: bool = False
    ) -> int:
        """
        Gửi nhiều email một cách hiệu quả sử dụng một kết nối duy nhất.

        Tham số:
            email_messages: Danh sách các từ điển chứa thông tin email, Mỗi từ điển nên có các tham số giống như phương thức send_email
            fail_silently: Có nên bỏ qua lỗi khi gửi hay không

        Trả về:
            int: Số lượng email đã gửi thành công

        Ví dụ:
            ```
            EmailHelper.send_mass_emails([
                {
                    'subject': 'Chào mừng Người dùng 1',
                    'recipients': ['user1@example.com'],
                    'message': 'Chào mừng bạn đến với nền tảng của chúng tôi, Người dùng 1!'
                },
                {
                    'subject': 'Chào mừng Người dùng 2',
                    'recipients': ['user2@example.com'],
                    'message': 'Chào mừng bạn đến với nền tảng của chúng tôi, Người dùng 2!'
                }
            ])
            ```
        """
        connection = get_connection(fail_silently=fail_silently)

        try:
            connection.open()
            sent_count = 0

            for email_data in email_messages:
                subject = email_data.get("subject", "")
                recipients = email_data.get("recipients", [])
                message = email_data.get("message", "")
                from_email = email_data.get("from_email")
                cc = email_data.get("cc")
                bcc = email_data.get("bcc")
                reply_to = email_data.get("reply_to")
                attachments = email_data.get("attachments")
                html_message = email_data.get("html_message")

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=recipients,
                    cc=cc or [],
                    bcc=bcc or [],
                    reply_to=reply_to or [],
                    connection=connection,
                )

                if html_message:
                    email.attach_alternative(html_message, "text/html")

                if attachments:
                    for attachment in attachments:
                        filename = attachment.get("filename")
                        content = attachment.get("content")
                        mimetype = attachment.get("mimetype")

                        if filename and content:
                            if isinstance(content, str):
                                content = content.encode("utf-8")

                            if mimetype:
                                email.attach(filename, content, mimetype)
                            else:
                                email.attach(filename, content)

                email_sent = email.send(fail_silently=True)
                sent_count += email_sent

                if email_sent:
                    print(f"Đã gửi email thành công tới {', '.join(recipients)}")
                else:
                    print(f"Không thể gửi email tới {', '.join(recipients)}")

            return sent_count
        except Exception as e:
            print(f"Lỗi khi gửi hàng loạt email: {str(e)}")
            if not fail_silently:
                raise
            return 0
        finally:
            connection.close()

    @classmethod
    def send_password_reset_email(
        cls,
        to_email: str,
        reset_url: str,
        username: str,
        full_name: Optional[str] = None,
        fail_silently: bool = False,
    ) -> bool:
        """
        Gửi email đặt lại mật khẩu cho người dùng.

        Tham số:
            to_email: Địa chỉ email người nhận
            reset_url: URL đặt lại mật khẩu
            username: Tên đăng nhập của người dùng
            full_name: Họ tên đầy đủ của người dùng (tùy chọn)
            fail_silently: Có nên bỏ qua lỗi khi gửi hay không

        Trả về:
            bool: True nếu email được gửi thành công, False nếu không
        """
        context = {
            "reset_url": reset_url,
            "username": username,
            "full_name": full_name or username,
            "valid_hours": getattr(settings, "PASSWORD_RESET_TIMEOUT_HOURS", 24),
        }

        return cls.send_template_email(
            subject="Yêu cầu đặt lại mật khẩu",
            recipients=[to_email],
            template_name="password_reset",
            context=context,
            fail_silently=fail_silently,
        )

    @classmethod
    def test_email_connection(cls) -> bool:
        """
        Kiểm tra cài đặt kết nối email.

        Trả về:
            bool: True nếu kết nối thành công, False nếu không
        """
        try:
            connection = get_connection()
            connection.open()
            connection.close()
            print("Kiểm tra kết nối email thành công")
            return True
        except Exception as e:
            print(f"Kiểm tra kết nối email thất bại: {str(e)}")
            return False
