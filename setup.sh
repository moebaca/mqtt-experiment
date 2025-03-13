#!/bin/bash
# Comprehensive setup script for MQTT project with TLS/SSL certificate authentication
# This script sets up the entire environment and configures secure certificate-based authentication

# Set up colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up MQTT Project with TLS/SSL Certificate Authentication...${NC}"

# Check for Docker
echo -e "\n${YELLOW}Checking for Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install Docker and try again.${NC}"
    exit 1
else
    echo -e "${GREEN}Docker is installed.${NC}"
fi

# Check for Docker Compose
echo -e "\n${YELLOW}Checking for Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Please install Docker Compose and try again.${NC}"
    exit 1
else
    echo -e "${GREEN}Docker Compose is installed.${NC}"
fi

# Check for Python
echo -e "\n${YELLOW}Checking for Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 not found. Please install Python 3 and try again.${NC}"
    exit 1
else
    echo -e "${GREEN}Python $(python3 --version) is installed.${NC}"
fi

# Check for OpenSSL
echo -e "\n${YELLOW}Checking for OpenSSL...${NC}"
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}OpenSSL not found. Please install OpenSSL and try again.${NC}"
    exit 1
else
    echo -e "${GREEN}OpenSSL $(openssl version) is installed.${NC}"
fi

# Check for mosquitto.conf
echo -e "\n${YELLOW}Checking for Mosquitto configuration...${NC}"
if [ ! -f mosquitto/config/mosquitto.conf ]; then
    echo -e "${RED}mosquitto/config/mosquitto.conf not found.${NC}"
    echo -e "${RED}Please ensure this file exists before running setup.${NC}"
    exit 1
else
    echo -e "${GREEN}Mosquitto configuration file found.${NC}"
fi

# Create required directories
echo -e "\n${YELLOW}Creating directories...${NC}"
mkdir -p mosquitto/data mosquitto/log certs/ca certs/broker certs/clients
echo -e "${GREEN}Directories created.${NC}"

# Generate certificates
echo -e "\n${BLUE}Generating TLS/SSL certificates...${NC}"

# Generate Certificate Authority (CA) key and certificate
echo -e "${YELLOW}Generating Certificate Authority (CA)...${NC}"
openssl genrsa -out certs/ca/ca.key 2048
openssl req -new -x509 -days 365 -key certs/ca/ca.key -out certs/ca/ca.crt -subj "/CN=MQTT CA"

# Generate broker key and certificate signing request (CSR)
echo -e "${YELLOW}Generating broker certificates...${NC}"
openssl genrsa -out certs/broker/broker.key 2048
openssl req -new -key certs/broker/broker.key -out certs/broker/broker.csr -subj "/CN=localhost"

# Sign the broker certificate with the CA
openssl x509 -req -in certs/broker/broker.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key \
  -CAcreateserial -out certs/broker/broker.crt -days 365

# Generate client certificates for publisher and subscriber
echo -e "${YELLOW}Generating client certificates...${NC}"
# Publisher certificates
openssl genrsa -out certs/clients/publisher.key 2048
openssl req -new -key certs/clients/publisher.key -out certs/clients/publisher.csr -subj "/CN=publisher"
openssl x509 -req -in certs/clients/publisher.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key \
  -CAcreateserial -out certs/clients/publisher.crt -days 365

# Subscriber certificates
openssl genrsa -out certs/clients/subscriber.key 2048
openssl req -new -key certs/clients/subscriber.key -out certs/clients/subscriber.csr -subj "/CN=subscriber"
openssl x509 -req -in certs/clients/subscriber.csr -CA certs/ca/ca.crt -CAkey certs/ca/ca.key \
  -CAcreateserial -out certs/clients/subscriber.crt -days 365

# Set appropriate permissions
chmod 600 certs/ca/ca.key certs/broker/broker.key certs/clients/*.key
echo -e "${GREEN}Certificates generated successfully.${NC}"

# Make scripts executable
echo -e "\n${YELLOW}Making scripts executable...${NC}"
chmod +x scripts/publisher.py scripts/subscriber.py
echo -e "${GREEN}Scripts are now executable.${NC}"

# Set up Python virtual environment
echo -e "\n${YELLOW}Setting up Python virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}Virtual environment created.${NC}"

# Activate virtual environment and install dependencies
echo -e "\n${YELLOW}Activating virtual environment and installing dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed.${NC}"

# Start the MQTT broker
echo -e "\n${YELLOW}Starting MQTT broker with TLS/SSL...${NC}"
docker-compose up -d
echo -e "${GREEN}MQTT broker started.${NC}"

echo -e "\n${YELLOW}Setup Summary:${NC}"
echo -e "  * MQTT broker is running at:"
echo -e "    - localhost:1883 (standard MQTT, localhost only)"
echo -e "    - localhost:8883 (MQTT over TLS, with certificate authentication)"
echo -e "  * Certificate-based authentication is configured"
echo -e "  * Python virtual environment is set up with all dependencies"
echo -e "  * All necessary certificates have been generated in the 'certs' directory"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo -e "  1. In this terminal (virtual environment is already activated):"
echo -e "     ${GREEN}python scripts/subscriber.py${NC}"
echo -e "  2. In a new terminal:"
echo -e "     ${GREEN}source venv/bin/activate${NC}"
echo -e "     ${GREEN}python scripts/publisher.py${NC}"

echo -e "\n${GREEN}Setup complete!${NC}"