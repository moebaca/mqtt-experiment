#!/usr/bin/env python3
"""
MQTT Subscriber with TLS/SSL Certificate Authentication
-------------------------------------------------------
A secure MQTT subscriber that receives messages from a specified topic
using TLS/SSL encryption and certificate-based authentication.
"""
import paho.mqtt.client as mqtt
import random
import json
import argparse
import logging
import os
import ssl
from datetime import datetime

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MQTT-Subscriber")

# Default MQTT broker settings
DEFAULT_BROKER = "localhost"
DEFAULT_PORT = 8883  # Standard MQTT TLS port
DEFAULT_TOPIC = "kobayashi/signals/test"


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="MQTT Subscriber with TLS/SSL")
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
        help=f"MQTT topic to subscribe to (default: {DEFAULT_TOPIC})",
    )
    parser.add_argument(
        "--ca-cert",
        default=os.path.join("certs", "ca", "ca.crt"),
        help="Path to CA certificate file",
    )
    parser.add_argument(
        "--cert",
        default=os.path.join("certs", "clients", "subscriber.crt"),
        help="Path to client certificate file",
    )
    parser.add_argument(
        "--key",
        default=os.path.join("certs", "clients", "subscriber.key"),
        help="Path to client key file",
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser.parse_args()


def on_connect(client, userdata, flags, reason_code, properties=None):
    """Callback when the client connects to the broker."""
    if reason_code == 0:
        logger.info(f"Connected to MQTT Broker: {userdata['broker']} using TLS/SSL")
        # Subscribe to the topic upon successful connection
        client.subscribe(userdata["topic"], qos=1)
        logger.info(f"Subscribed to topic: {userdata['topic']}")
    else:
        logger.error(f"Failed to connect, return code: {reason_code}")


def on_subscribe(client, userdata, mid, reason_code_list=None, properties=None):
    """Callback when client subscribes to a topic."""
    logger.debug(f"Subscribed with message ID: {mid}")
    if reason_code_list:
        for idx, reason_code in enumerate(reason_code_list):
            if reason_code != 0:
                logger.warning(
                    f"Failed to subscribe to topic #{idx}, reason code: {reason_code}"
                )


def on_message(client, userdata, msg):
    """Callback when a message is received."""
    try:
        payload_str = msg.payload.decode("utf-8")

        message = json.loads(payload_str)

        # Get current time for latency calculation
        receive_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.info(f"\n--- New Message Received on {msg.topic} ---")
        logger.info(f"Message ID: {message['message_id']}")
        logger.info(f"Message timestamp: {message['timestamp']}")
        logger.info(f"Received at: {receive_time}")
        logger.info(f"Value: {message['value']}")
        logger.info(f"Status: {message['status']}")

        if message["status"] == "red":
            logger.warning("ALERT: Red status detected!")

    except json.JSONDecodeError:
        logger.error("Error decoding JSON message")
        logger.debug(f"Raw message: {payload_str}")
    except KeyError as e:
        logger.error(f"Missing expected key in message: {e}")
        logger.debug(f"Message content: {message}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        logger.debug(f"Raw message: {msg.payload}")


def on_disconnect(client, userdata, reason_code, properties=None):
    """Callback when the client disconnects from the broker."""
    if reason_code == 0:
        logger.info("Disconnected successfully")
    else:
        logger.warning(f"Unexpected disconnection, reason code: {reason_code}")


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
    client_id = f"kobayashi-subscriber-{random.randint(0, 1000)}"

    # Store topic in userdata for access in callbacks
    userdata = {"topic": args.topic, "broker": args.broker}

    # Create a client instance with version 2 callback API
    client = mqtt.Client(
        client_id=client_id,
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        userdata=userdata,
    )

    # Set callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_disconnect = on_disconnect

    logger.info("Setting up TLS/SSL with certificate authentication")
    try:
        client.tls_set(
            ca_certs=args.ca_cert,
            certfile=args.cert,
            keyfile=args.key,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLS,
            ciphers=None,
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

    # Start the loop to process received messages
    logger.info("Waiting for messages. Press Ctrl+C to exit.")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        logger.info("\nSubscriber terminated by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        try:
            client.disconnect()
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")
            pass
        logger.info("Disconnected from broker")

    return 0


if __name__ == "__main__":
    exit(main())
