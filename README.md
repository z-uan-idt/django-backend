# Pharma Go Backend

## Installation
### 1. Clone project
### 2. Tạo và kích hoạt virtual environment
> Yêu cầu python nhỏ hơn hoặc bằng 3.9.x

```bash
python -m venv venv
source venv/bin/activate  # Trên macOS/Linux
venv\Scripts\activate  # Trên Windows
```
### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```
### 4. Cấu hình môi trường
Sao chép file `.env.local` thành `.env` và chỉnh sửa giá trị nếu cần.
```bash
cp .env.local .env
```
### 5. Celery
```
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
celery -A config flower --port=????
```