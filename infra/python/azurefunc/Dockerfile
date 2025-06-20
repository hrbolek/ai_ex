# Vyber základní image s Azure Functions Python Workerem
FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Nastav pracovní adresář
WORKDIR /home/site/wwwroot

# Zkopíruj requirements a vše ostatní do image
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Zkopíruj zbytek aplikace (funkce, host.json, atd.)
COPY . .

# [volitelně] Pokud máš nějaké statické soubory, můžeš je zkopírovat taky
# COPY static ./static

# [volitelně] Pokud používáš application settings file, zkopíruj i ten
# COPY local.settings.json .

# Port 80 je default pro Azure Functions v kontejneru
EXPOSE 80

# Entrypoint je přednastaven v base image (nejčastěji "python -m azure_functions_worker")
