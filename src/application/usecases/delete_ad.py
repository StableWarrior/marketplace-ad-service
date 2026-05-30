from src.application.exceptions import AdNotFoundError, ForbiddenError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import DeleteAdPort


class DeleteAd(DeleteAdPort):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, ad_id: int, user_id: int) -> None:
        async with self._uow as uow:
            ad = await uow.ads.get_by_id(ad_id)

            if ad is None or ad.status == "archived":
                raise AdNotFoundError(f"Ad {ad_id} not found")

            if ad.user_id != user_id:
                raise ForbiddenError("You can't delete this ad")

            ad.archive()

            await uow.ads.save(ad)

            await uow.outbox.add(event_type="ad.deleted", payload=dict(ad_id=ad.id))

            await uow.commit()
