FROM python:3.9

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip \
    && pip install wheel \
    && pip --no-cache-dir install -r requirements.txt 


EXPOSE 80
ENV NAME venv

#CMD ["celery", "-A", "app.celery" , "worker","-c" , "4"]
#ENTRYPOINT ["gunicorn" , "-w" , "4" , "-b", "0.0.0.0:5000" , "-t" , "900" , "app:app"]
#python -m pip install --upgrade pip