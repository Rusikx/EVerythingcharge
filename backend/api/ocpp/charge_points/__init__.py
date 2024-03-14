import asyncio
import uuid

from ocpp.charge_point import ChargePoint as cp
from ocpp.messages import create_route_map
from propan import apply_types, Context

from core.annotations import Settings, TasksExchange, AMQPHeaders


class ChargePoint(cp):
    """
    Using 'this' instead of 'self':
    https://github.com/Lancetnik/FastDepends/issues/37#issuecomment-1854732858
    """

    @apply_types
    def __init__(
            this,
            charge_point_id: str,
            settings: Settings,
            response_queues=Context()
    ):
        this.id = charge_point_id
        this._call_lock = asyncio.Lock()
        this._unique_id_generator = uuid.uuid4
        this._response_queue = response_queues[this.id]
        this._response_timeout = settings.RESPONSE_TIMEOUT
        this.route_map = create_route_map(this)

    @apply_types
    async def _send(
            this,
            payload,
            exchange: TasksExchange,
            amqp_headers: AMQPHeaders,
            broker=Context()
    ):
        await broker.publish(
            payload,
            exchange=exchange,
            routing_key="",
            content_type="text/plain",
            headers=amqp_headers
        )

    async def start(this):
        pass