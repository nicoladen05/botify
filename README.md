# Installation
## Any OS
Install the dependencies.
```bash
pip install -r requirements.txt
```

Create a .env file with your bots token
```bash
echo BOT_TOKEN=[Your Token] > .env
```

## Docker
Build the image.
```bash
docker build . -t botify
```

Run the image normally or through docker-compose. Pass your bot token to the
container using the environment variable `BOT_TOKEN` .
