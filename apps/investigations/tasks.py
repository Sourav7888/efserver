from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Investigation


def get_investigations_status():
    """
    Get all the investigations status
    :return:
    """
    investigations = Investigation.objects.all()
    total_investigations = investigations.count()
    closed_investigations = investigations.filter(closed=True).count()
    in_monitoring_investigations = investigations.filter(in_approval=True).count()
    open_investigations = investigations.filter(
        investigation_investigator__isnull=True
    ).count()
    on_going_investigations = investigations.filter(
        closed=False, in_approval=False, investigation_investigator__isnull=False
    ).count()

    # return all data
    return {
        "total_investigations": total_investigations,
        "closed_investigations": closed_investigations,
        "in_monitoring_investigations": in_monitoring_investigations,
        "open_investigations": open_investigations,
        "on_going_investigations": on_going_investigations,
    }


@shared_task
def send_email(subject, from_email, to_email):

    context = get_investigations_status()

    msg_html = render_to_string("daily_report.html", {"context": context})
    msg_txt = render_to_string("daily_report.txt", {"context": context})
    send_mail(subject, msg_txt, from_email, to_email, html_message=msg_html)
