FROM python:3.10.12-alpine

RUN adduser -D swist

WORKDIR /home/swist

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY templates templates
COPY api_requests.py config.py swist_web.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP swist_web.py

RUN chown -R swist:swist ./
USER swist

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]