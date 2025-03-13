#!/usr/bin/env python3
"""
MQTT Publisher with TLS/SSL Certificate Authentication
------------------------------------------------------
A secure MQTT publisher that sends messages to a specified topic
using TLS/SSL encryption and certificate-based authentication.
"""
import paho.mqtt.client as mqtt
import time
import json
import random
import argparse
import logging
import os
import ssl

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MQTT-Publisher")

# Default MQTT broker settings
DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 8883  # Standard MQTT TLS port
DEFAULT_TOPIC = "kobayashi/signals/test"
DEFAULT_INTERVAL = 10  # seconds


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MQTT Publisher with TLS/SSL")
    parser.add_argument(
        "--broker",
        default=DEFAULT_BROKER,
        help=f"MQTT broker address (default: {DEFAULT_BROKER})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help=f"MQTT broker port (default: {DEFAULT_PORT})",
    )
    parser.add_argument(
        "--topic",
        default=DEFAULT_TOPIC,
        help=f"MQTT topic to publish to (default: {DEFAULT_TOPIC})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL,
        help=f"Publish interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    parser.add_argument(
        "--ca-cert",
        default=os.path.join("certs", "ca", "ca.crt"),
        help="Path to CA certificate file",
    )
    parser.add_argument(
        "--cert",
        default=os.path.join("certs", "clients", "publisher.crt"),
        help="Path to client certificate file",
    )
    parser.add_argument(
        "--key",
        default=os.path.join("certs", "clients", "publisher.key"),
        help="Path to client key file",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def on_connect(client, userdata, flags, reason_code, properties=None):
    """Callback when the client connects to the broker."""
    if reason_code == 0:
        logger.info(f"Connected to MQTT Broker: {userdata['broker']} using TLS/SSL")
    else:
        logger.error(f"Failed to connect, return code: {reason_code}")


def on_publish(client, userdata, mid, reason_code=None, properties=None):
    """Callback when a message is published."""
    logger.debug(f"Message {mid} published successfully")


def on_disconnect(client, userdata, reason_code, properties=None):
    """Callback when the client disconnects from the broker."""
    if reason_code == 0:
        logger.info("Disconnected successfully")
    else:
        logger.warning(f"Unexpected disconnection, reason code: {reason_code}")


def create_sample_message(message_count):
    """Create a sample message with random values."""
    return {
        "message_id": message_count,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "value": random.randint(0, 100),
        "status": random.choice(["green", "yellow", "red"]),
    }


def check_cert_files(ca_cert, client_cert, client_key):
    """Check if certificate files exist and are readable."""
    for cert_file in [ca_cert, client_cert, client_key]:
        if not os.path.isfile(cert_file):
            logger.error(f"Certificate file not found: {cert_file}")
            return False
        if not os.access(cert_file, os.R_OK):
            logger.error(f"Certificate file not readable: {cert_file}")
            return False
    return True


def main():
    """Main function."""
    args = parse_arguments()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if not check_cert_files(args.ca_cert, args.cert, args.key):
        return 1

    # Create a client ID with a random component
    client_id = f"kobayashi-publisher-{random.randint(0, 1000)}"

    # Create a client instance with version 2 callback API
    client = mqtt.Client(
        client_id=client_id,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        userdata={"broker": args.broker},
    )

    # Set callbacks
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    logger.info("Setting up TLS/SSL with certificate authentication")
    try:
        client.tls_set(
            ca_certs=args.ca_cert,
            certfile=args.cert,
            keyfile=args.key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None,  # defaults
        )
    except Exception as e:
        logger.error(f"Failed to set up TLS: {e}")
        return 1

    logger.info(f"Connecting to secure broker {args.broker}:{args.port}...")
    try:
        client.connect(args.broker, args.port)
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return 1

    # Start the MQTT loop in a non-blocking way
    client.loop_start()

    try:
        # Publish messages at regular intervals
        message_count = 0
        while True:
            message_count += 1

            message = create_sample_message(message_count)

            payload = json.dumps(message)

            # Publish message with QoS 1 for reliability
            result = client.publish(args.topic, payload, qos=1)

            # Check if the message was published
            status = result[0]
            if status == 0:
                logger.info(f"Sent message: {payload}")
            else:
                logger.error(f"Failed to send message with status {status}")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logger.info("Publisher terminated by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        try:
            client.loop_stop()
            client.disconnect()
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            pass
        logger.info("Disconnected from broker")

    return 0


if __name__ == "__main__":
    exit(main())
