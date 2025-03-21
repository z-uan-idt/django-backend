import datetime
from datetime import timedelta
from typing import Optional, Union, Tuple
from dateutil.relativedelta import relativedelta
import pytz


"""
Cách sử dụng:

# Lấy thời gian hiện tại và định dạng
now = DatetimeHelper.get_now()
formatted_date = DatetimeHelper.format_date(now, preview=True)  # 07/03/2025
formatted_time = DatetimeHelper.format_time(now)  # 15:30:45
formatted_datetime = DatetimeHelper.format_datetime(now, preview=True)  # 07/03/2025 15:30:45

# Phân tích chuỗi ngày tháng
date_obj = DatetimeHelper.parse_date("07/03/2025", preview=True)
datetime_obj = DatetimeHelper.parse_datetime("07/03/2025 15:30:45", preview=True)

# Tính toán với ngày tháng
tomorrow = DatetimeHelper.add_days(DatetimeHelper.get_today(), 1)
next_month = DatetimeHelper.add_months(DatetimeHelper.get_today(), 1)
next_year = DatetimeHelper.add_years(DatetimeHelper.get_today(), 1)

# Làm việc với tháng và năm
first_day, last_day = DatetimeHelper.get_start_end_of_month()
year_start, year_end = DatetimeHelper.get_start_end_of_year(2025)

# Tiện ích khác
age = DatetimeHelper.get_age(DatetimeHelper.parse_date("01/01/1990", preview=True))
day_name = DatetimeHelper.get_day_of_week_name(DatetimeHelper.get_today())  # Thứ Sáu
is_weekend = DatetimeHelper.is_weekend(DatetimeHelper.get_today())  # False
"""


class DatetimeHelper:
    DATE_FORMAT = "%Y-%m-%d"
    PREVIEW_DATE_FORMAT = "%d/%m/%Y"
    TIME_FORMAT = "%H:%M:%S"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    PREVIEW_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
    PREVIEW_FULL_DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S.%f"

    @classmethod
    def get_now(cls, tz: str = "Asia/Ho_Chi_Minh") -> datetime.datetime:
        """
        Lấy thời gian hiện tại theo múi giờ 'Asia/Ho_Chi_Minh' hoặc múi giờ được chỉ định.

        Args:
            tz (str): Múi giờ. Mặc định là 'Asia/Ho_Chi_Minh'

        Returns:
            datetime.datetime: Thời gian hiện tại với múi giờ
        """
        return datetime.datetime.now(pytz.timezone(tz))

    @classmethod
    def get_today(cls, tz: str = "Asia/Ho_Chi_Minh") -> datetime.date:
        """
        Lấy ngày hiện tại theo múi giờ 'Asia/Ho_Chi_Minh' hoặc múi giờ được chỉ định.

        Args:
            tz (str): Múi giờ. Mặc định là 'Asia/Ho_Chi_Minh'

        Returns:
            datetime.date: Ngày hiện tại
        """
        return cls.get_now(tz).date()

    @classmethod
    def format_date(
        cls, date_obj: Union[datetime.date, datetime.datetime], preview: bool = False
    ) -> str:
        """
        Chuyển đổi đối tượng date/datetime thành chuỗi theo định dạng DATE_FORMAT hoặc PREVIEW_DATE_FORMAT.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime
            preview (bool): Nếu True, sử dụng PREVIEW_DATE_FORMAT (dd/mm/yyyy). Mặc định là False.

        Returns:
            str: Chuỗi ngày tháng đã được định dạng
        """
        date_format = cls.PREVIEW_DATE_FORMAT if preview else cls.DATE_FORMAT
        if isinstance(date_obj, datetime.datetime):
            return date_obj.strftime(date_format)
        return date_obj.strftime(date_format)

    @classmethod
    def format_time(cls, time_obj: Union[datetime.time, datetime.datetime]) -> str:
        """
        Chuyển đổi đối tượng time/datetime thành chuỗi theo định dạng TIME_FORMAT.

        Args:
            time_obj (Union[datetime.time, datetime.datetime]): Đối tượng time hoặc datetime

        Returns:
            str: Chuỗi thời gian đã được định dạng
        """
        if isinstance(time_obj, datetime.datetime):
            return time_obj.strftime(cls.TIME_FORMAT)
        return time_obj.strftime(cls.TIME_FORMAT)

    @classmethod
    def format_datetime(
        cls, datetime_obj: datetime.datetime, preview: bool = False, full: bool = False
    ) -> str:
        """
        Chuyển đổi đối tượng datetime thành chuỗi theo định dạng được chỉ định.

        Args:
            datetime_obj (datetime.datetime): Đối tượng datetime
            preview (bool): Nếu True, sử dụng PREVIEW_DATETIME_FORMAT. Mặc định là False.
            full (bool): Nếu True, sử dụng PREVIEW_FULL_DATETIME_FORMAT. Mặc định là False.

        Returns:
            str: Chuỗi ngày tháng đã được định dạng
        """
        if full and preview:
            return datetime_obj.strftime(cls.PREVIEW_FULL_DATETIME_FORMAT)
        elif preview:
            return datetime_obj.strftime(cls.PREVIEW_DATETIME_FORMAT)
        return datetime_obj.strftime(cls.DATETIME_FORMAT)

    @classmethod
    def parse_date(cls, date_str: str, preview: bool = False) -> datetime.date:
        """
        Chuyển đổi chuỗi ngày tháng thành đối tượng date.

        Args:
            date_str (str): Chuỗi ngày tháng
            preview (bool): Nếu True, sử dụng PREVIEW_DATE_FORMAT. Mặc định là False.

        Returns:
            datetime.date: Đối tượng date

        Raises:
            ValueError: Nếu chuỗi không đúng định dạng
        """
        date_format = cls.PREVIEW_DATE_FORMAT if preview else cls.DATE_FORMAT
        return datetime.datetime.strptime(date_str, date_format).date()

    @classmethod
    def parse_time(cls, time_str: str) -> datetime.time:
        """
        Chuyển đổi chuỗi thời gian thành đối tượng time.

        Args:
            time_str (str): Chuỗi thời gian

        Returns:
            datetime.time: Đối tượng time

        Raises:
            ValueError: Nếu chuỗi không đúng định dạng
        """
        return datetime.datetime.strptime(time_str, cls.TIME_FORMAT).time()

    @classmethod
    def parse_datetime(
        cls, datetime_str: str, preview: bool = False, full: bool = False
    ) -> datetime.datetime:
        """
        Chuyển đổi chuỗi ngày tháng thành đối tượng datetime.

        Args:
            datetime_str (str): Chuỗi ngày tháng
            preview (bool): Nếu True, sử dụng PREVIEW_DATETIME_FORMAT. Mặc định là False.
            full (bool): Nếu True, sử dụng PREVIEW_FULL_DATETIME_FORMAT. Mặc định là False.

        Returns:
            datetime.datetime: Đối tượng datetime

        Raises:
            ValueError: Nếu chuỗi không đúng định dạng
        """
        if full and preview:
            return datetime.datetime.strptime(
                datetime_str, cls.PREVIEW_FULL_DATETIME_FORMAT
            )
        elif preview:
            return datetime.datetime.strptime(datetime_str, cls.PREVIEW_DATETIME_FORMAT)
        return datetime.datetime.strptime(datetime_str, cls.DATETIME_FORMAT)

    @classmethod
    def add_days(
        cls, date_obj: Union[datetime.date, datetime.datetime], days: int
    ) -> Union[datetime.date, datetime.datetime]:
        """
        Thêm số ngày vào đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime
            days (int): Số ngày cần thêm (có thể âm)

        Returns:
            Union[datetime.date, datetime.datetime]: Đối tượng date/datetime mới
        """
        return date_obj + timedelta(days=days)

    @classmethod
    def add_months(
        cls, date_obj: Union[datetime.date, datetime.datetime], months: int
    ) -> Union[datetime.date, datetime.datetime]:
        """
        Thêm số tháng vào đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime
            months (int): Số tháng cần thêm (có thể âm)

        Returns:
            Union[datetime.date, datetime.datetime]: Đối tượng date/datetime mới
        """
        return date_obj + relativedelta(months=months)

    @classmethod
    def add_years(
        cls, date_obj: Union[datetime.date, datetime.datetime], years: int
    ) -> Union[datetime.date, datetime.datetime]:
        """
        Thêm số năm vào đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime
            years (int): Số năm cần thêm (có thể âm)

        Returns:
            Union[datetime.date, datetime.datetime]: Đối tượng date/datetime mới
        """
        return date_obj + relativedelta(years=years)

    @classmethod
    def get_first_day_of_month(
        cls, date_obj: Union[datetime.date, datetime.datetime]
    ) -> datetime.date:
        """
        Lấy ngày đầu tiên của tháng từ đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime

        Returns:
            datetime.date: Ngày đầu tiên của tháng
        """
        if isinstance(date_obj, datetime.datetime):
            return datetime.date(date_obj.year, date_obj.month, 1)
        return datetime.date(date_obj.year, date_obj.month, 1)

    @classmethod
    def get_last_day_of_month(
        cls, date_obj: Union[datetime.date, datetime.datetime]
    ) -> datetime.date:
        """
        Lấy ngày cuối cùng của tháng từ đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime

        Returns:
            datetime.date: Ngày cuối cùng của tháng
        """
        # Lấy ngày đầu tiên của tháng tiếp theo và trừ đi 1 ngày
        first_day_next_month = cls.get_first_day_of_month(cls.add_months(date_obj, 1))
        return cls.add_days(first_day_next_month, -1)

    @classmethod
    def get_start_end_of_month(
        cls, date_obj: Union[datetime.date, datetime.datetime, None] = None
    ) -> Tuple[datetime.date, datetime.date]:
        """
        Lấy ngày đầu tiên và ngày cuối cùng của tháng.

        Args:
            date_obj (Union[datetime.date, datetime.datetime, None]): Đối tượng date hoặc datetime. Mặc định là None (sử dụng ngày hiện tại).

        Returns:
            Tuple[datetime.date, datetime.date]: Ngày đầu tiên và ngày cuối cùng của tháng
        """
        if date_obj is None:
            date_obj = cls.get_today()

        start_date = cls.get_first_day_of_month(date_obj)
        end_date = cls.get_last_day_of_month(date_obj)

        return start_date, end_date

    @classmethod
    def get_start_end_of_year(
        cls, year: Optional[int] = None
    ) -> Tuple[datetime.date, datetime.date]:
        """
        Lấy ngày đầu tiên và ngày cuối cùng của năm.

        Args:
            year (Optional[int]): Năm cần lấy. Mặc định là None (sử dụng năm hiện tại).

        Returns:
            Tuple[datetime.date, datetime.date]: Ngày đầu tiên và ngày cuối cùng của năm
        """
        if year is None:
            year = cls.get_today().year

        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)

        return start_date, end_date

    @classmethod
    def is_weekend(cls, date_obj: Union[datetime.date, datetime.datetime]) -> bool:
        """
        Kiểm tra xem ngày có phải là cuối tuần (thứ 7 hoặc chủ nhật) không.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime

        Returns:
            bool: True nếu là cuối tuần, False nếu không phải
        """
        # 5 là thứ 7, 6 là chủ nhật
        return date_obj.weekday() >= 5

    @classmethod
    def date_range(
        cls,
        start_date: Union[datetime.date, datetime.datetime],
        end_date: Union[datetime.date, datetime.datetime],
    ) -> list:
        """
        Tạo danh sách các ngày từ start_date đến end_date.

        Args:
            start_date (Union[datetime.date, datetime.datetime]): Ngày bắt đầu
            end_date (Union[datetime.date, datetime.datetime]): Ngày kết thúc

        Returns:
            list: Danh sách các ngày
        """
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()

        delta = end_date - start_date
        return [start_date + timedelta(days=i) for i in range(delta.days + 1)]

    @classmethod
    def get_age(
        cls,
        birth_date: Union[datetime.date, datetime.datetime],
        reference_date: Union[datetime.date, datetime.datetime] = None,
    ) -> int:
        """
        Tính tuổi dựa trên ngày sinh và ngày tham chiếu.

        Args:
            birth_date (Union[datetime.date, datetime.datetime]): Ngày sinh
            reference_date (Union[datetime.date, datetime.datetime], optional): Ngày tham chiếu.
                                                                           Mặc định là None (sử dụng ngày hiện tại).

        Returns:
            int: Số tuổi
        """
        if reference_date is None:
            reference_date = cls.get_today()

        if isinstance(birth_date, datetime.datetime):
            birth_date = birth_date.date()
        if isinstance(reference_date, datetime.datetime):
            reference_date = reference_date.date()

        # Sử dụng relativedelta để tính chính xác tuổi
        rd = relativedelta(reference_date, birth_date)
        return rd.years

    @classmethod
    def get_quarter(
        cls, date_obj: Union[datetime.date, datetime.datetime] = None
    ) -> int:
        """
        Lấy quý của năm từ đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime], optional): Đối tượng date hoặc datetime.
                                                                     Mặc định là None (sử dụng ngày hiện tại).

        Returns:
            int: Quý (1-4)
        """
        if date_obj is None:
            date_obj = cls.get_today()

        month = date_obj.month
        return (month - 1) // 3 + 1

    @classmethod
    def get_start_end_of_quarter(
        cls, year: int = None, quarter: int = None
    ) -> Tuple[datetime.date, datetime.date]:
        """
        Lấy ngày đầu tiên và ngày cuối cùng của quý.

        Args:
            year (int, optional): Năm. Mặc định là None (sử dụng năm hiện tại).
            quarter (int, optional): Quý (1-4). Mặc định là None (sử dụng quý hiện tại).

        Returns:
            Tuple[datetime.date, datetime.date]: Ngày đầu tiên và ngày cuối cùng của quý
        """
        if year is None:
            today = cls.get_today()
            year = today.year

        if quarter is None:
            today = cls.get_today()
            quarter = cls.get_quarter(today)

        if not 1 <= quarter <= 4:
            raise ValueError("Quarter must be between 1 and 4")

        first_month_of_quarter = 3 * quarter - 2
        last_month_of_quarter = 3 * quarter

        start_date = datetime.date(year, first_month_of_quarter, 1)

        # Lấy ngày cuối cùng của tháng cuối quý
        if last_month_of_quarter == 12:
            end_date = datetime.date(year, 12, 31)
        else:
            end_date = datetime.date(year, last_month_of_quarter + 1, 1) - timedelta(
                days=1
            )

        return start_date, end_date

    @classmethod
    def get_day_of_week_name(
        cls, date_obj: Union[datetime.date, datetime.datetime], vietnamese: bool = True
    ) -> str:
        """
        Lấy tên thứ trong tuần từ đối tượng date/datetime.

        Args:
            date_obj (Union[datetime.date, datetime.datetime]): Đối tượng date hoặc datetime
            vietnamese (bool, optional): Nếu True, trả về tên tiếng Việt. Mặc định là True.

        Returns:
            str: Tên thứ trong tuần
        """
        weekday = date_obj.weekday()

        if vietnamese:
            day_names = [
                "Thứ Hai",
                "Thứ Ba",
                "Thứ Tư",
                "Thứ Năm",
                "Thứ Sáu",
                "Thứ Bảy",
                "Chủ Nhật",
            ]
        else:
            day_names = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]

        return day_names[weekday]

    @classmethod
    def get_month_name(cls, month: int, vietnamese: bool = True) -> str:
        """
        Lấy tên tháng từ số tháng.

        Args:
            month (int): Số tháng (1-12)
            vietnamese (bool, optional): Nếu True, trả về tên tiếng Việt. Mặc định là True.

        Returns:
            str: Tên tháng
        """
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1 and 12")

        if vietnamese:
            month_names = [
                "Tháng Một",
                "Tháng Hai",
                "Tháng Ba",
                "Tháng Tư",
                "Tháng Năm",
                "Tháng Sáu",
                "Tháng Bảy",
                "Tháng Tám",
                "Tháng Chín",
                "Tháng Mười",
                "Tháng Mười Một",
                "Tháng Mười Hai",
            ]
        else:
            month_names = [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ]

        return month_names[month - 1]

    @classmethod
    def date_diff_in_days(
        cls,
        start_date: Union[datetime.date, datetime.datetime],
        end_date: Union[datetime.date, datetime.datetime],
    ) -> int:
        """
        Tính số ngày giữa hai ngày.

        Args:
            start_date (Union[datetime.date, datetime.datetime]): Ngày bắt đầu
            end_date (Union[datetime.date, datetime.datetime]): Ngày kết thúc

        Returns:
            int: Số ngày
        """
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()

        delta = end_date - start_date
        return delta.days

    @classmethod
    def to_utc(
        cls, dt: datetime.datetime, from_tz: str = "Asia/Ho_Chi_Minh"
    ) -> datetime.datetime:
        """
        Chuyển đổi đối tượng datetime từ múi giờ cụ thể sang UTC.

        Args:
            dt (datetime.datetime): Đối tượng datetime cần chuyển đổi
            from_tz (str, optional): Múi giờ nguồn. Mặc định là 'Asia/Ho_Chi_Minh'.

        Returns:
            datetime.datetime: Đối tượng datetime đã chuyển đổi sang UTC
        """
        # Thêm thông tin timezone nếu dt là naive datetime
        if dt.tzinfo is None:
            dt = pytz.timezone(from_tz).localize(dt)

        return dt.astimezone(pytz.UTC)

    @classmethod
    def from_utc(
        cls, dt: datetime.datetime, to_tz: str = "Asia/Ho_Chi_Minh"
    ) -> datetime.datetime:
        """
        Chuyển đổi đối tượng datetime từ UTC sang múi giờ cụ thể.

        Args:
            dt (datetime.datetime): Đối tượng datetime UTC cần chuyển đổi
            to_tz (str, optional): Múi giờ đích. Mặc định là 'Asia/Ho_Chi_Minh'.

        Returns:
            datetime.datetime: Đối tượng datetime đã chuyển đổi sang múi giờ đích
        """
        # Thêm thông tin timezone UTC nếu dt là naive datetime
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)

        return dt.astimezone(pytz.timezone(to_tz))
