# 1. 가볍고 안정적인 베이스 이미지
FROM python:3.9-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. requirements 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# 4. 전체 프로젝트 복사 (.pt, .json 포함)
COPY . .

# 5. PYTHONPATH 설정
ENV PYTHONPATH=/app

# 6. 포트 설정
EXPOSE 8000

# 7. 실행 명령어 
CMD ["uvicorn", "polite_back.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info"]
