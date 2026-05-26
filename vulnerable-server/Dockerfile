FROM python:3.13.7

# Setarea unui director de lucru
WORKDIR /app  

# Copierea dependintelor
COPY server/requirements.txt /app/server/requirements.txt  

# Instalarea dependindelor copiate anterior
RUN pip install --no-cache-dir -r /app/server/requirements.txt

# Copiem restul proiectului in container
COPY . /app

# Expunerea portului pe care ruleaza Flask
EXPOSE 5000

# Rularea aplicatiei
CMD ["python", "server/app.py"]
