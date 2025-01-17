from typing import Any

from loguru import logger
from ocpp.routing import on
from ocpp.v16 import call_result
from ocpp.v16.enums import Action, RegistrationStatus
from propan import apply_types, Depends

from api.web.charge_points import get_charge_point_service
from api.web.charge_points.views import UpdateChargePointPayloadView
from core.utils import get_formatted_utc, get_settings


class BootNotificationScenario:

    @apply_types
    @on(Action.BootNotification)
    async def on_boot_notification(
            self_,
            utc_datetime: str = Depends(get_formatted_utc),
            charge_point_vendor=Depends(lambda charge_point_vendor: charge_point_vendor),
            charge_point_model=Depends(lambda charge_point_model: charge_point_model),
            service: Any = Depends(get_charge_point_service),
            settings: Any = Depends(get_settings),
            **kwargs
    ):
        logger.info(
            f"Accepted '{Action.BootNotification}' "
            f"(charge_point_vendor={charge_point_vendor}, "
            f"charge_point_model={charge_point_model}, "
            f"charge_point_id={self_.id}, "
            f"kwargs={kwargs})"
        )
        payload = UpdateChargePointPayloadView(
            model=charge_point_model,
            vendor=charge_point_vendor
        )
        await service.update_charge_point(
            charge_point_id=self_.id,
            payload=payload.dict(exclude_unset=True)
        )
        return call_result.BootNotificationPayload(
            current_time=utc_datetime,
            interval=settings.HEARTBEAT_INTERVAL,
            status=RegistrationStatus.accepted,
        )
