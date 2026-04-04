import asyncio
from concurrent.futures import ThreadPoolExecutor

from asgiref.sync import sync_to_async

from .models import Car, CarReviewLog


_task_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='car-review-log')


def enqueue_pending_review_log(car_id):
    _task_executor.submit(_run_pending_review_log_task, car_id)


def _run_pending_review_log_task(car_id):
    asyncio.run(create_pending_review_log(car_id))


async def create_pending_review_log(car_id):
    car = await sync_to_async(
        lambda: Car.objects.select_related('owner').get(pk=car_id),
        thread_sensitive=True,
    )()

    already_logged = await sync_to_async(
        lambda: CarReviewLog.objects.filter(
            car_id=car_id,
            status=CarReviewLog.StatusChoices.PENDING_REVIEW,
        ).exists(),
        thread_sensitive=True,
    )()

    if already_logged:
        return

    await sync_to_async(
        CarReviewLog.objects.create,
        thread_sensitive=True,
    )(
        car=car,
        submitted_by=car.owner,
        status=CarReviewLog.StatusChoices.PENDING_REVIEW,
        message='Обявата е изпратена за модераторско одобрение.',
    )
