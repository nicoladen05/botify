FROM python:3.12.6

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt
RUN python3 -m pip uninstall discord.py -y
RUN python3 -m pip uninstall py-cord -y
RUN python3 -m pip install py-cord

WORKDIR /app
COPY . /app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "src/bot.py"]
