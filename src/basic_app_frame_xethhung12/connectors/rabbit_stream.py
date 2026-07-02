import asyncio
from rstream import (
    AMQPMessage,
    Consumer,
    ConsumerOffsetSpecification,
    OffsetSpecification,
    OffsetNotFound,
    MessageContext,
    OffsetType,
    Producer
)
import ssl
import os

host=os.environ.get('STREAM_HOST')
user=os.environ.get('STREAM_USER')
password=os.environ.get('STREAM_PASSWORD')
port=int(os.environ.get('STREAM_PORT'))
vhost=os.environ.get('STREAM_VHOST')


def get_ssl_context():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    return ssl_context


def get_producer(
    host: str,
    user: str,
    password: str,
    port: int,
    vhost: str
):
    return Producer(host=host,port=port, username=user, password=password, vhost=vhost, ssl_context=get_ssl_context())

def get_consumer(
    host: str,
    user: str,
    password: str,
    port: int,
    vhost: str
)->Consumer:
    return Consumer(host=host, username=user, password=password, port=port, vhost=vhost, ssl_context=get_ssl_context())

async def run_worker(client, stream_name, consumer_name, callback):
    try:
        last_offset = await client.query_offset(stream_name, consumer_name)
        start_at = OffsetSpecification(3, last_offset + 1)
        print(f"Resuming {consumer_name} at {last_offset + 1}")
    except Exception:
        start_at = OffsetSpecification(0)
        print(f"Starting {consumer_name} from the beginning")

    offset_spec = ConsumerOffsetSpecification(consumer_name, start_at)
    await client.subscribe(stream_name, callback, offset_spec)
    print(f"Worker {consumer_name} is now running...")
