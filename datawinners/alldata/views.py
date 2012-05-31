from __builtin__ import dict
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.urlresolvers import reverse
from datawinners.accountmanagement.views import is_new_user, is_allowed_to_view_reports
from datawinners.alldata.helper import get_all_project_for_user, get_visibility_settings_for, get_page_heading, get_reports_list
from datawinners.settings import CRS_ORG_ID
from datawinners.main.utils import get_database_manager
from datawinners.project.models import ProjectState, Project
from datawinners.project.views import project_overview, project_data, project_results, web_questionnaire
from mangrove.form_model.form_model import FormModel
from datawinners.submission.models import DatawinnerLog
from datawinners.utils import get_organization
from datawinners.entity.views import create_subject
from datawinners.accountmanagement.views import is_not_expired

def get_crs_project_links():
    project_links = {'projects_link': reverse(index),
                     'reports_link': reverse(reports),
                     }
    return project_links


def get_project_analysis_and_log_link(project, project_id, questionnaire_code):
    analysis = log = "#"
    disabled = "disable_link"
    if project.state != ProjectState.INACTIVE:
        disabled = ""
        analysis = reverse(project_data, args = [project_id, questionnaire_code])
        log = reverse(project_results, args = [project_id, questionnaire_code])
    return analysis, disabled, log


def get_project_info(manager, raw_project, user):
    project_id = raw_project['value']['_id']
    project = Project.load(manager.database, project_id)
    questionnaire = manager.get(project['qid'], FormModel)
    questionnaire_code = questionnaire.form_code

    analysis, disabled, log = get_project_analysis_and_log_link(project, project_id, questionnaire_code)

    web_submission_link = reverse("web_questionnaire", args = [project_id])

    web_submission_link_disabled = 'disable_link'
    if 'web' in raw_project['value']['devices']:
        web_submission_link_disabled = ""

    create_subjects_link = ''
    if 'no' in raw_project['value']['activity_report']:
        create_subjects_link = reverse(create_subject, args = [project.entity_type])

    project_info = dict(name = raw_project['value']['name'],
                        created = raw_project['value']['created'],
                        type = raw_project['value']['project_type'],
                        link = (reverse(project_overview, args = [project_id])),
                        log = log, analysis = analysis, disabled = disabled,
                        web_submission_link = web_submission_link,
                        web_submission_link_disabled = web_submission_link_disabled,
                        create_subjects_link = create_subjects_link,
                        entity_type = project.entity_type)
    return project_info


def projects_index(request):
    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    page_heading = get_page_heading(request.user)

    project_list = []
    manager = get_database_manager(request.user)
    rows = get_all_project_for_user(request.user)
    for row in rows:
        project_list.append(get_project_info(manager, row, request.user))
    return disable_link_class, hide_link_class, page_heading, project_list


@login_required(login_url = '/login')
@is_new_user
@is_not_expired
def index(request):
    disable_link_class, hide_link_class, page_heading, project_list = projects_index(request)
    organization_id = get_organization(request).org_id
    if organization_id == CRS_ORG_ID and not request.user.get_profile().reporter:
        return render_to_response('alldata/index.html',
                {'projects': project_list, 'page_heading': page_heading, 'disable_link_class': disable_link_class,
                 'hide_link_class': hide_link_class, 'is_crs_user': True, 'project_links': get_crs_project_links()},
                                  context_instance = RequestContext(request))
    else:
        return render_to_response('alldata/index.html',
                {'projects': project_list, 'page_heading': page_heading, 'disable_link_class': disable_link_class,
                 'hide_link_class': hide_link_class, 'is_crs_user': False},
                                  context_instance = RequestContext(request))


@login_required(login_url = '/login')
@is_not_expired
def failed_submissions(request):
    logs = DatawinnerLog.objects.all()
    organization = get_organization(request)
    org_logs = [log for log in logs if log.organization == organization]
    return render_to_response('alldata/failed_submissions.html', {'logs': org_logs},
                              context_instance = RequestContext(request))


@login_required(login_url = '/login')
@is_not_expired
@is_allowed_to_view_reports
def reports(request):
    report_list = get_reports_list(get_organization(request).org_id,request.session.get('django_language','en'))
    response = render_to_response('alldata/reports_page.html',
            {'reports': report_list, 'page_heading': "All Data", 'project_links': get_crs_project_links()},
                                  context_instance = RequestContext(request))
    response.set_cookie('crs_session_id', request.COOKIES['sessionid'])
    return response

@login_required(login_url = '/login')
@is_not_expired
def smart_phone_instruction(request):
    return HttpResponse()
