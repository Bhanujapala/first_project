FROM python:3.11-slim

WORKDIR /app

COPY module3_genai/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY module3_genai ./module3_genai

ENV MOCK_LLM=1

EXPOSE 7860

CMD ["uvicorn", "module3_genai.main:app", "--host", "0.0.0.0", "--port", "7860"]