import os
import sys

sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts"))
)


def test_mqtt_modules_import():
    """Test that we can import the MQTT client modules."""
    from publisher import parse_arguments as pub_parse
    from subscriber import parse_arguments as sub_parse

    # Basic test to verify the modules can be imported
    assert callable(pub_parse)
    assert callable(sub_parse)


def test_publisher_argument_parsing():
    """Test the argument parsing in the publisher."""
    from publisher import parse_arguments
    import sys

    original_argv = sys.argv

    try:
        sys.argv = ["publisher.py", "--broker", "test-broker", "--port", "8883"]
        args = parse_arguments()
        assert args.broker == "test-broker"
        assert args.port == 8883
    finally:
        sys.argv = original_argv


def test_subscriber_argument_parsing():
    """Test the argument parsing in the subscriber."""
    from subscriber import parse_arguments
    import sys

    original_argv = sys.argv

    try:
        sys.argv = ["subscriber.py", "--broker", "test-broker", "--topic", "test/topic"]
        args = parse_arguments()
        assert args.broker == "test-broker"
        assert args.topic == "test/topic"
    finally:
        sys.argv = original_argv
