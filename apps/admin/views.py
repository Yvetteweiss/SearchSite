from django.shortcuts import render
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.conf import settings

from scrapyd_api import ScrapydAPI
SCRAPYD_URL = settings.SCRAPYD_URL
PROJECT_NAME = settings.SCRAPY_PROJECT_NAME
scrapyd = ScrapydAPI(SCRAPYD_URL)

import json

from . import models, apscheduler

scheduler = apscheduler.scheduler
scheduler = apscheduler.init_scheduler(scheduler)


def index(request):
    return render(request, 'admin/index.html')


def jobs(request):
    spider_jobs = scrapyd.list_jobs(PROJECT_NAME)
    pending = spider_jobs['pending']
    running = spider_jobs['running']
    finished = spider_jobs['finished']
    for job in running:
        job['run_time'] = time_diff(job['start_time'])
        job['start_time'] = time_display(job['start_time'])
        job['log'] = log_url(job)
    for job in finished:
        job['run_time'] = time_diff(job['start_time'], job['end_time'])
        job['start_time'] = time_display(job['start_time'])
        job['end_time'] = time_display(job['end_time'])
        job['log'] = log_url(job)
    context = {
        'pending': pending,
        'running': running,
        'finished': finished,
    }
    return render(request, 'admin/jobs.html', context=context)


def cancel_job(request):
    pass


def configurations(request):
    spider_configurations = models.Configuration.objects.all()
    context = {
        'spider_configurations': spider_configurations
    }
    return render(request, 'admin/configurations.html', context=context)


class AddConfigurationView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'admin/configurations_add.html')

    def post(self, request, *args, **kwargs):
        spider_name = request.POST.get('spider-name')
        spider_allowed_domains = request.POST.get('spider-allowed-domains').replace('\n', '')
        spider_start_urls = request.POST.get('spider-start-urls').replace('\n', '')
        spider_closespider_timeout = request.POST.get('spider-closespider-timeout')
        spider_concurrent_items = request.POST.get('spider-concurrent-items')
        spider_concurrent_requests = request.POST.get('spider-concurrent-requests')
        spider_concurrent_requests_per_ip = request.POST.get('spider-concurrent-requests-per-ip')
        spider_cookies_enabled = request.POST.get('spider-cookies-enabled')
        spider_depth_limit = request.POST.get('spider-depth-limit')
        spider_download_timeout = request.POST.get('spider-download-timeout')
        spider_interval = request.POST.get('spider-interval')
        spider_auto_run = request.POST.get('spider-auto-run')
        conf = {
            'allowed_domains': spider_allowed_domains.split('\n'),
            'start_urls': spider_start_urls.split('\n'),
        }
        custom_settings = {
            'CLOSESPIDER_TIMEOUT': int(spider_closespider_timeout),
            'CONCURRENT_ITEMS': int(spider_concurrent_items),
            'CONCURRENT_REQUESTS': int(spider_concurrent_requests),
            'CONCURRENT_REQUESTS_PER_IP': int(spider_concurrent_requests_per_ip),
            'COOKIES_ENABLED': True if int(spider_cookies_enabled) else False,
            'DEPTH_LIMIT': int(spider_depth_limit),
            'DOWNLOAD_TIMEOUT': int(spider_download_timeout),
        }
        exsists = models.Configuration.objects.filter(name=spider_name).exists()
        if exsists:
            spider_configuration = models.Configuration.objects.get(name=spider_name)
            context = {
                'created': False,
                'exists': True,
                'action': 'create',
                'spider_configuration': spider_configuration,
            }
        else:
            spider_configuration = models.Configuration.objects.create(name=spider_name,
                                                                       conf=json.dumps(conf),
                                                                       custom_settings=json.dumps(custom_settings),
                                                                       interval=int(spider_interval),
                                                                       auto_run=int(spider_auto_run))
            apscheduler.save_job_from_instance(scheduler, spider_configuration)
            context = {
                'created': True,
                'exists': True,
                'action': 'create',
                'spider_configuration': spider_configuration,
            }
        return render(request, 'admin/configurations_detail.html', context=context)


class EditConfigurationView(View):
    def get(self, request, *args, **kwargs):
        spider_name = request.GET.get('name')
        exists = models.Configuration.objects.filter(name=spider_name)
        if exists:
            spider_configuration = models.Configuration.objects.get(name=spider_name)
            spider_conf = json.loads(spider_configuration.conf)
            context = {
                'exists': True,
                'spider_name': spider_configuration.name,
                'spider_allowed_domains': '\n'.join(spider_conf['allowed_domains']),
                'spider_start_urls': '\n'.join(spider_conf['start_urls']),
                'spider_custom_settings': json.loads(spider_configuration.custom_settings),
                'spider_interval': spider_configuration.interval,
                'spider_auto_run': spider_configuration.auto_run,
            }
        else:
            context = {
                'exists': False,
            }
        return render(request, 'admin/configurations_edit.html', context=context)

    def post(self, request, *args, **kwargs):
        spider_name = request.POST.get('spider-name')
        spider_allowed_domains = request.POST.get('spider-allowed-domains').replace('\r', '')
        spider_start_urls = request.POST.get('spider-start-urls').replace('\r', '')
        spider_closespider_timeout = request.POST.get('spider-closespider-timeout')
        spider_concurrent_items = request.POST.get('spider-concurrent-items')
        spider_concurrent_requests = request.POST.get('spider-concurrent-requests')
        spider_concurrent_requests_per_ip = request.POST.get('spider-concurrent-requests-per-ip')
        spider_cookies_enabled = request.POST.get('spider-cookies-enabled')
        spider_depth_limit = request.POST.get('spider-depth-limit')
        spider_download_timeout = request.POST.get('spider-download-timeout')
        spider_interval = request.POST.get('spider-interval')
        spider_auto_run = request.POST.get('spider-auto-run')
        conf = {
            'allowed_domains': spider_allowed_domains.split('\n'),
            'start_urls': spider_start_urls.split('\n'),
        }
        custom_settings = {
            'CLOSESPIDER_TIMEOUT': int(spider_closespider_timeout),
            'CONCURRENT_ITEMS': int(spider_concurrent_items),
            'CONCURRENT_REQUESTS': int(spider_concurrent_requests),
            'CONCURRENT_REQUESTS_PER_IP': int(spider_concurrent_requests_per_ip),
            'COOKIES_ENABLED': True if int(spider_cookies_enabled) else False,
            'DEPTH_LIMIT': int(spider_depth_limit),
            'DOWNLOAD_TIMEOUT': int(spider_download_timeout),
        }
        q = models.Configuration.objects.filter(name=spider_name)
        if q.exists():
            q.update(conf=json.dumps(conf),
                     custom_settings=json.dumps(custom_settings),
                     interval=int(spider_interval),
                     auto_run=int(spider_auto_run))
            spider_configuration = models.Configuration.objects.get(name=spider_name)
            apscheduler.save_job_from_instance(scheduler, spider_configuration)
            context = {
                'exists': True,
                'action': 'edit',
                'spider_configuration': spider_configuration,
            }
        else:
            context = {
                'exists': False,
                'action': 'edit',
                'spider_configuration': None,
            }
        return render(request, 'admin/configurations_detail.html', context=context)


@require_POST
def configurations_delete(request):
    spider_name = request.POST.get('spider-name')
    exists = models.Configuration.objects.filter(name=spider_name).exists()
    if exists:
        spider_configuration = models.Configuration.objects.get(name=spider_name)
        apscheduler.delete_job_from_instance(scheduler, spider_configuration)
        models.Configuration.objects.filter(name=spider_name).delete()
        context = {
            'message': 'Delete a configuration succesfully...'
        }
    else:
        context = {
            'message': 'Failed to delete a configuration'
        }
    return render(request, 'admin/index.html', context=context)


@require_GET
def configurations_detail(request):
    spider_name = request.GET.get('name')
    exists = models.Configuration.objects.filter(name=spider_name).exists()
    if exists:
        spider_configuration = models.Configuration.objects.get(name=spider_name)
        context = {
            'created': False,
            'exists': True,
            'action': 'query',
            'spider_configuration': spider_configuration
        }
    else:
        context = {
            'created': False,
            'exists': False,
            'action': 'query',
            'query_name': spider_name,
        }
    return render(request, 'admin/configurations_detail.html', context=context)


def log_url(job):
    return '/'.join([SCRAPYD_URL, 'logs', PROJECT_NAME, job['spider'], job['id']+'.log'])


import pytz
def time_display(string):
    import datetime
    dt = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def time_diff(start_time, end_time=None):
    import datetime
    start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
    if end_time:
        end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S.%f')
    else:
        end_time = datetime.datetime.now()
    run_time = end_time - start_time
    run_total_seconds = int(run_time.total_seconds())
    run_hour = run_total_seconds // (60*60)
    run_minute = (run_total_seconds - run_hour*(60*60)) // 60
    run_second = run_total_seconds % 60
    return '%02d:%02d:%02d' % (run_hour, run_minute, run_second)
