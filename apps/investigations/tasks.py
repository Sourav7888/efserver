from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from core.models import UserInfo
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
def send_daily_report(to_email: list[str]):
    subject = "Automated Report: High Consumption Investigations"
    template_name = "daily_report"
    from_email = "info@enerfrog-workstation.ca"

    context = get_investigations_status()
    msg_html = render_to_string(f"{template_name}.html", {"context": context})
    msg_txt = render_to_string(f"{template_name}.txt", {"context": context})

    send_mail(subject, msg_txt, from_email, to_email, html_message=msg_html)


@shared_task
def send_created_investigation(info: dict[str, str]):

    subject = "New High Consumption Investigations Request"
    template_name = "created_report"
    from_email = "info@enerfrog-workstation.ca"

    to_email = list(
        UserInfo.objects.filter(is_investigator=True)
        .exclude(user__email="")
        .values_list("user__email", flat=True)
    )

    msg_html = render_to_string(f"{template_name}.html", {"context": info})
    msg_txt = render_to_string(f"{template_name}.txt", {"context": info})

    send_mail(subject, msg_txt, from_email, to_email, html_message=msg_html)
