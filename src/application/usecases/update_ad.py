from src.application.exceptions import AdNotFoundError, ForbiddenError
from src.application.ports.uow import UnitOfWork
from src.application.ports.usecases import UpdateAdPort
from src.domain.entities import Ad


class UpdateAd(UpdateAdPort):
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        ad_id: int,
        user_id: int,
        title: str | None,
        description: str | None,
        price: int | None,
        category: str | None,
        city: str | None,
    ) -> Ad:
        async with self._uow as uow:
            ad = await uow.ads.get_by_id(ad_id)

            if ad is None or ad.status == "archived":
                raise AdNotFoundError(f"Ad {ad_id} not found")

            if ad.user_id != user_id:
                raise ForbiddenError("You cannot edit this ad")

            ad.edit(
                title=title or ad.title,
                description=description or ad.description,
                price=price or ad.price,
                category=category or ad.category,
                city=city or ad.city,
            )

            await uow.ads.save(ad)

            await uow.outbox.add(event_type="ad.updated", payload=dict(ad_id=ad.id))

            await uow.commit()

            return ad
