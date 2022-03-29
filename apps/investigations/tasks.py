from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from core.models import Customer, Facility, UserInfo
from .models import Investigation
from django.db.models import Q
from datetime import datetime as dt

# @TODO: Test
def get_investigations_status():
    """
    Get all the investigations status
    :return:
    """
    investigations = Investigation.objects.all()
    total_investigations = investigations.count()
    closed_investigations = investigations.filter(closed=True).count()
    in_monitoring_investigations = investigations.filter(
        in_approval=True, closed=False
    ).count()
    open_investigations = investigations.filter(
        investigation_investigator__isnull=True, closed=False
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

    # @TODO: Some user email include none when sent
    to_email = list(
        UserInfo.objects.filter(
            investigation_authorization__is_investigator=True,
            access_level="ENERFROG_STAFF",
        )
        .exclude(user__email="")
        .values_list("user__email", flat=True)
    )

    msg_html = render_to_string(f"{template_name}.html", {"context": info})
    msg_txt = render_to_string(f"{template_name}.txt", {"context": info})

    send_mail(subject, msg_txt, from_email, to_email, html_message=msg_html)


def query_hc_investigation_report(info: dict[str, str]):
    """
    Query all data required for hc investigation report
    """
    customer = Customer.objects.get(customer_name=info["customer"])
    facility = Facility.objects.filter(division__customer=customer).select_related(
        "division"
    )
    investigations = Investigation.objects.filter(
        facility__in=facility, investigation_date=info["investigation_date"]
    ).select_related("facility")

    # Generic ones
    total = investigations.count()
    on_going = investigations.filter(in_approval=False).count()
    in_monitoring = investigations.filter(in_approval=True).count()

    # Cost Avoidance
    cost = sum(
        [
            k.investigation_metadata["cost_increase"]
            for k in investigations.filter(
                Q(investigation_metadata__isnull=False)
                & ~Q(investigation_metadata={})
                & Q(investigation_metadata__has_key="cost_increase")
            )
        ]
    )

    # Date
    date = dt.strptime(info["investigation_date"], "%Y-%m-%d").strftime("%B, %Y")

    return {
        "customer": customer.customer_name,
        "total": total,
        "on_going": on_going,
        "in_monitoring": in_monitoring,
        "cost": "${:,}".format(round(cost, 2)),
        "investigation_date": date,
    }


@shared_task
def send_hc_investigation_report(info: dict[str, str]):
    subject = "Monthly High Consumption Report"
    template_name = "investigation_report"
    from_email = "info@enerfrog-workstation.ca"
    to_email = info["recipients"]

    context = query_hc_investigation_report(info)

    msg_html = render_to_string(f"{template_name}.html", {"context": context})
    msg_txt = render_to_string(f"{template_name}.txt", {"context": context})

    send_mail(subject, msg_txt, from_email, to_email, html_message=msg_html)
