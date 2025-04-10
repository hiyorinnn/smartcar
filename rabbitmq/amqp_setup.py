#!/usr/bin/env python3

"""
A script that only needs to be executed at the start after the rabbitMQ container is started up. It will create the exchange
smartcar_topic with the queues Notification and Testbed.
- Notification is the queue which the notification microservice listens to
- Testbed is a spare queue to collect all messages for testing purposes

We created a container of this file so that docker compose up will run this script, but it can be stopped as soon as the 
script is run.
"""

import pika

amqp_host = "host.docker.internal"
amqp_port = 5672
exchange_name = "smartcar_topic"
exchange_type = "topic"


def create_exchange(hostname, port, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    # connect to the broker
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    print("Open channel")
    channel = connection.channel()

    # Set up the exchange if the exchange doesn't exist
    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, exchange_type=exchange_type, durable=True
    )
    # 'durable' makes the exchange survive broker restarts

    return channel


def create_queue(channel, exchange_name, queue_name, routing_key):
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts

    # bind the queue to the exchange via the routing_key
    channel.queue_bind(
        exchange=exchange_name, queue=queue_name, routing_key=routing_key
    )


channel = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Notification",
    routing_key="*.notif",
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Testbed",
    routing_key="#",
)
