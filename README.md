# MQTT Experiment

Just wanted to play around with mqtt before proposing a solution to a friend.

## Overview

- Mosquitto MQTT broker running in Docker with TLS/SSL security
- Python publisher and subscriber scripts with mutual TLS authentication
- Automated certificate generation and deployment
- Message persistence and delivery guarantees
- venv setup
- Docker Compose deployment

## Requirements

- Docker and Docker Compose
- Python 3.7+
- OpenSSL (for certificate generation) (only tested on MacOS)
- Git (for cloning this repository)

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/moebaca/mqtt-experiment.git
cd mqtt-experiment
```

### 2. Run the setup script

The easiest way to get started is to use the included setup script which handles everything automatically:

```bash
# Make the script executable
chmod +x setup.sh

# Run the setup
./setup.sh
```

### 3. Run the subscriber

In one terminal (with the virtual environment activated):

```bash
python scripts/subscriber.py
```

### 4. Run the publisher

In another terminal (with the virtual environment activated):

```bash
python scripts/publisher.py
```

You should see messages being published by the publisher and received by the subscriber over a secure, encrypted connection.

## Command-Line Options

Both scripts support various command-line arguments:

```bash
python scripts/subscriber.py --help
python scripts/publisher.py --help
```

## Development and Testing

To run tests locally:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/
```

To format and lint the code locally:

```bash
# Run black
black scripts/

# Run flake8
flake8 scripts/
```

## Troubleshooting

### Checking Broker Logs

If you encounter connection issues, check the broker logs:

```bash
docker-compose logs mosquitto
```

## License

[MIT License](LICENSE)