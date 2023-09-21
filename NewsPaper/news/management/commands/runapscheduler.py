import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from ...models import Category, CategorySubscribers, Post
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    category_list = Category.objects.all()
    date = datetime.today() - timedelta(days=6)
    posts = Post.objects.filter(timePost__gt=date)
    for c in Category.objects.all():
        post_list = posts.filter(category=c)
        if post_list:
            subscribers = c.subscribers.all()
            context = {
                'posts': post_list,
                'category': c,
            }
            for s in subscribers:
                context['subscriber'] = s
                html_content = render_to_string('week_mail.html', context)

                msg = EmailMultiAlternatives(
                    subject=f'Вы подписаны на новости из категории {c}',
                    from_email='kuchinsk93@yandex.ru',
                    to=[f'{s.email}'],
                )
                msg.attach_alternative(html_content, "text/html")  # добавляем html

                msg.send()
                print(f'отправлено на почту {s.email}')


# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(week="1"),
            # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
