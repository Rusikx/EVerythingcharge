from typing import Dict

from ocpp.v16.enums import ChargePointStatus
from ocpp.v201.enums import ConnectorStatusType
from propan import apply_types, Context
from sqlalchemy import select, update

from api.web.charge_points.models import ChargePoint
from api.web.charge_points.views import CreateChargPointPayloadView
from api.web.exceptions import NotFound


@apply_types
async def create_charge_point(
        network_id: str,
        data: CreateChargPointPayloadView,
        session=Context()
) -> ChargePoint:
    data.network_id = network_id
    data.status = {
        "1.6": ChargePointStatus.unavailable,
        "2.0.1": ConnectorStatusType.unavailable
    }[data.ocpp_version]
    charge_point = ChargePoint(**data.dict())
    session.add(charge_point)
    return charge_point


@apply_types
async def update_charge_point(
        charge_point_id: str,
        payload: Dict,
        session=Context()
):
    await session.execute(
        update(ChargePoint) \
            .where(ChargePoint.id == charge_point_id) \
            .values(**payload)
    )


@apply_types
async def get_charge_point(charge_point_id: str, session=Context()) -> ChargePoint | None:
    query = select(ChargePoint).where(ChargePoint.id == charge_point_id)
    result = await session.execute(query)
    charge_point = result.scalars().first()
    return charge_point


@apply_types
async def get_charge_point_or_404(charge_point_id) -> ChargePoint:
    charge_point = await get_charge_point(charge_point_id)
    if not charge_point:
        raise NotFound(detail=f"The charge point with id: '{charge_point_id}' has not found.")
    return charge_point
