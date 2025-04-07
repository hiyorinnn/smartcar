FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=5008
ENV STRIPE_API_KEY=sk_test_51R7XLM4Jm41usPZBwNr5slG3GHhThtJ4LLHe9MpwsXxnzIT2c11AKYoHGLvO0KwxCEGztfwuI3ozrQ0mAiqJMcM400uwoLUqju
ENV STRIPE_WEBHOOK_SECRET=whsec_2dWJNk3ZJZ7xtTzl0qpVZAShENq4OJws
ENV rental_composite_URL=http://rental-composite:5007/api/v1
ENV booking_log_URL=http://booking_log:5006/api/booking


EXPOSE 5008

CMD ["python", "app.py"]