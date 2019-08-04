from django.conf import settings

from scrapyd_api import ScrapydAPI
SCRAPYD_URL = settings.SCRAPYD_URL
PROJECT_NAME = settings.SCRAPY_PROJECT_NAME
scrapyd = ScrapydAPI(SCRAPYD_URL)

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
scheduler = BackgroundScheduler()


def spider_job_generator(instance):
    import json
    spider_configuration = instance
    conf = spider_configuration.conf
    custom_settings = json.loads(spider_configuration.custom_settings)
    spider_jobid = scrapyd.schedule(PROJECT_NAME, 'demo', settings=custom_settings, conf=conf)
    print(spider_jobid, 'is running...')


def init_scheduler(scheduler):
    try:
        scheduler.add_jobstore(DjangoJobStore(), "default")
        scheduler.remove_all_jobs()

        from . import models
        spider_configurations = models.Configuration.objects.all()
        for instance in spider_configurations:
            save_job_from_instance(scheduler, instance)

        register_events(scheduler)
        scheduler.start()
    except Exception as e:
        print(e)
        scheduler.shutdown()
    return scheduler


def save_job_from_instance(scheduler, instance):
    if instance.auto_run:
        scheduler.add_job(spider_job_generator, "interval", id=instance.name, seconds=instance.interval,
                          coalesce=True, replace_existing=True, misfire_grace_time=30,
                          kwargs={'instance': instance})
        return instance.name, True
    else:
        delete_job_from_instance(scheduler, instance)
        return instance.name, False


def delete_job_from_instance(scheduler, instance):
    try:
        scheduler.remove_job(job_id=instance.name)
        return instance.name, True
    except Exception as e:
        print(e)
        return instance.name, False

