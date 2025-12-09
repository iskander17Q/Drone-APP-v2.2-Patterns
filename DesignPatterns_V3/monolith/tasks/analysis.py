from celery.utils.log import get_task_logger

from ..app.services import get_analysis_service
from ..celery_app import celery_app
from .report import generate_report_task

logger = get_task_logger(__name__)


@celery_app.task(name="analysis.run", bind=True, max_retries=1)
def run_analysis_task(self, run_id: str, auto_report: bool = False):
    service = get_analysis_service()
    try:
        run = service.perform_run(run_id)
        logger.info("Analysis run %s completed", run.id)
        if auto_report:
            generate_report_task.delay(run.id)
        return {"run_id": run.id, "status": run.status}
    except Exception as exc:  # pylint: disable=broad-except
        service.mark_failed(run_id, str(exc))
        logger.exception("Analysis run %s failed: %s", run_id, exc)
        raise exc

