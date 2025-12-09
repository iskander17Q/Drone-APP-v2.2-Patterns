from celery.utils.log import get_task_logger

from ..app.services import get_report_service
from ..celery_app import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="report.generate")
def generate_report_task(run_id: str):
    service = get_report_service()
    try:
        report = service.generate_for_run(run_id)
        logger.info("Report %s created for run %s", report.id, run_id)
        return {"report_id": report.id}
    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("Report generation failed for run %s: %s", run_id, exc)
        raise exc

