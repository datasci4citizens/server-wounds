
FROM python

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN apt-get update && apt-get install -y libgl1



COPY . /code/

CMD ["python", "./citizens_project/manage.py", "runserver", "0.0.0.0:8000"]