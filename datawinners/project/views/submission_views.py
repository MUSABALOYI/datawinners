from collections import OrderedDict
from copy import deepcopy
from django.utils.translation import ugettext_lazy as _
import json
import datetime
import logging
from string import capitalize
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext
from mangrove.form_model.field import SelectField
from mangrove.transport.player.new_players import WebPlayerV2
from alldata.helper import get_visibility_settings_for
from datawinners.accountmanagement.views import session_not_expired
from datawinners.custom_report_router.report_router import ReportRouter
from datawinners.utils import get_organization
from mangrove.form_model.form_model import get_form_model_by_code, FormModel

from mangrove.utils.json_codecs import encode_json

from datawinners.accountmanagement.views import is_datasender
from datawinners.main.utils import get_database_manager
from datawinners.accountmanagement.views import is_not_expired
from project import helper
from project.ExcelHeader import  ExcelFileSubmissionHeader
from project.data_sender_helper import get_data_sender
from project.export_to_excel import _prepare_export_data, _create_excel_response
from project.helper import SUBMISSION_DATE_FORMAT_FOR_SUBMISSION
from project.models import Project
from project.survey_response_list import SurveyResponseList
from project.submission_list_for_excel import SurveyResponseForExcel
from project.utils import    project_info
from project.Header import SubmissionsPageHeader
from project.analysis_result import AnalysisResult
from datawinners.activitylog.models import UserActivityLog
from datawinners.project.views.views import XLS_TUPLE_FORMAT
from datawinners.common.constant import   DELETED_DATA_SUBMISSION, EDITED_DATA_SUBMISSION
from datawinners.project.submission_utils.submission_formatter import SubmissionFormatter
from datawinners.project.views.utils import get_form_context
from project.submission_form import SubmissionForm
from mangrove.transport.repository.survey_responses import get_survey_response_by_id
from mangrove.transport.contract.survey_response import SurveyResponse
from django.core.urlresolvers import reverse

performance_logger = logging.getLogger("performance")
websubmission_logger = logging.getLogger("websubmission")

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
# TODO : TW_BLR : should have separate view for ui and data
def index(request, project_id=None, questionnaire_code=None, tab="0"):
    manager = get_database_manager(request.user)

    form_model = get_form_model_by_code(manager, questionnaire_code)
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')
    org_id = helper.get_org_id_by_user(request.user)

    survey_responses = SurveyResponseList(form_model, manager, org_id, submission_type, filters, keyword)

    if request.method == 'GET':
        header = SubmissionsPageHeader(form_model)
        result_dict = {"header_list": header.header_list,
                       "header_name_list": repr(encode_json(header.header_list)),
                       "datasender_list": survey_responses.get_data_senders(),
                       "subject_list": survey_responses.get_subjects(),
                       "tab": tab
        }
        result_dict.update(project_info(request, manager, form_model, project_id, questionnaire_code))
        return render_to_response('project/results.html', result_dict, context_instance=RequestContext(request))

    if request.method == 'POST':
        field_values = SubmissionFormatter().get_formatted_values_for_list(survey_responses.get_raw_values())
        analysis_result = AnalysisResult(field_values, survey_responses.get_analysis_statistics(),
            survey_responses.get_data_senders(), survey_responses.get_subjects(),
            survey_responses.get_default_sort_order())
        performance_logger.info("Fetch %d survey_responses from couchdb." % len(analysis_result.field_values))
        return HttpResponse(encode_json({'data_list': analysis_result.field_values,
                                         "statistics_result": analysis_result.statistics_result}))


def delete(request, project_id):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    survey_response_ids = json.loads(request.POST.get('id_list'))

    received_times = []
    for survey_response_id in survey_response_ids:
        survey_response = SurveyResponse.get(manager, survey_response_id)
        received_times.append( datetime.datetime.strftime(survey_response.created, "%d/%m/%Y %X"))
        WebPlayerV2(manager).delete_survey_response(survey_response, websubmission_logger)

        if survey_response.data_record:
            ReportRouter().delete(get_organization(request).org_id, survey_response.form_code, survey_response.data_record.id)

    if len(received_times):
        UserActivityLog().log(request, action=DELETED_DATA_SUBMISSION, project=project.name,
            detail=json.dumps({"Date Received": "[%s]" % ", ".join(received_times)}))
        response = encode_json({'success_message': ugettext("The selected records have been deleted"), 'success': True})
    else: response = encode_json({'error_message': ugettext("No records deleted"), 'success': False})
    
    return HttpResponse(response)


def build_static_info_context(manager, org_id, survey_response):
    form_ui_model = OrderedDict()
    static_content = {'Data Sender': get_data_sender(manager, org_id, survey_response),
                      'Source': capitalize(
                          survey_response.channel) if survey_response.channel == 'web' else survey_response.channel.upper(),
                      'Submission Date': survey_response.created.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)
    }

    form_ui_model.update({'static_content': static_content})
    form_ui_model.update({'is_edit': True})
    form_ui_model.update({
        'status': ugettext('Success') if survey_response.status else ugettext(
            'Error') + '. ' + survey_response.errors, })
    return form_ui_model


@login_required(login_url='/login')
@session_not_expired
@is_not_expired
def edit(request, project_id, survey_response_id, tab=0):
    manager = get_database_manager(request.user)
    project = Project.load(manager.database, project_id)
    questionnaire_form_model = FormModel.get(manager, project.qid)
    SurveyResponseForm = SubmissionForm.create(manager, project, questionnaire_form_model)

    disable_link_class, hide_link_class = get_visibility_settings_for(request.user)
    survey_response = get_survey_response_by_id(manager, survey_response_id)
    back_link = reverse(index, kwargs={"project_id":project_id, "questionnaire_code": questionnaire_form_model.form_code, "tab":tab})
    form_ui_model = build_static_info_context(manager, get_organization(request).org_id, survey_response)
    form_ui_model.update({"back_link": back_link})
    if request.method == 'GET':
        survey_response_form = SurveyResponseForm()
        survey_response_form.initial_values(survey_response.values)
        form_ui_model.update(get_form_context(questionnaire_form_model.form_code, project, survey_response_form,
            manager, hide_link_class, disable_link_class))
        form_ui_model.update({"redirect_url": request.path_info})

        return render_to_response("project/web_questionnaire.html", form_ui_model,
            context_instance=RequestContext(request))

    if request.method == 'POST':
        original_survey_response = survey_response.copy()
        is_errored_before_edit = True if survey_response.errors != '' else False
        survey_response_form = SurveyResponseForm(data=request.POST)
        form_ui_model.update(get_form_context(questionnaire_form_model.form_code, project, survey_response_form,
            manager, hide_link_class, disable_link_class))
        form_ui_model.update({"redirect_url": request.POST.get("redirect_url")})
        if not survey_response_form.is_valid():
            error_message = _("Please check your answers below for errors.")
            form_ui_model.update({'error_message': error_message})
            return render_to_response("project/web_questionnaire.html", form_ui_model,
                context_instance=RequestContext(request))

        created_request = helper.create_request(survey_response_form, request.user.username)
        response = WebPlayerV2(manager).edit_survey_response(created_request, survey_response, websubmission_logger)
        if response.success:
            ReportRouter().route(get_organization(request).org_id, response)
            success_message = _("Your changes have been saved.")
            form_ui_model.update({'success_message': success_message})
            _update_static_info_block_status(form_ui_model, is_errored_before_edit)
            log_edit_action(original_survey_response, survey_response, request, project.name, questionnaire_form_model)
            return HttpResponseRedirect(request.POST.get("redirect_url"))
        else:
            survey_response_form._errors = helper.errors_to_list(response.errors, questionnaire_form_model.fields)
        return render_to_response("project/web_questionnaire.html", form_ui_model,
            context_instance=RequestContext(request))


def log_edit_action(old_survey_response, new_survey_response, request, project_name, form_model):
    differences = new_survey_response.differs_from(old_survey_response)
    diff_dict = {}
    changed_answers = deepcopy(differences.changed_answers)
    if differences.changed_answers:
        for key, value in differences.changed_answers.iteritems():
            question_field = form_model._get_field_by_code(key)
            question_label = question_field.label
            #replacing question code with actual question text
            changed_answers[question_label] = changed_answers.pop(key)
            #relace option with value for choice field
            if isinstance(question_field,SelectField):
                changed_answers[question_label] = get_option_value_for_field(value,question_field)

        diff_dict.update({'changed_answers': changed_answers})
    diff_dict.update({'received_on': differences.created.strftime(SUBMISSION_DATE_FORMAT_FOR_SUBMISSION)})
    diff_dict.update({'status_changed': differences.status_changed})
    activity_log = UserActivityLog()
    activity_log.log(request, project=project_name, action=EDITED_DATA_SUBMISSION, detail=json.dumps(diff_dict))


def get_choice_list(diff_value, question_field):
    #TODO change the method name formatted_field_value_for_excel
    prev_choice_values = question_field.formatted_field_values_for_excel(diff_value)
    return prev_choice_values


def get_option_value_for_field(diff_value, question_field):

    prev_choice_values = get_choice_list(diff_value["old"], question_field)

    reslt_dict = {"old" : ', '.join(prev_choice_values) if prev_choice_values else diff_value["old"],
                  "new" : ', '.join(get_choice_list(diff_value["new"],question_field))}

    return reslt_dict

@login_required(login_url='/login')
@session_not_expired
@is_datasender
@is_not_expired
# TODO : no test
def export(request):
    project_name = request.POST.get(u"project_name")
    submission_type = request.GET.get('type')
    filters = request.POST
    keyword = request.POST.get('keyword', '')

    user = helper.get_org_id_by_user(request.user)
    manager = get_database_manager(request.user)
    questionnaire_code = request.POST.get('questionnaire_code')
    form_model = get_form_model_by_code(manager, questionnaire_code)

    submission_list = SurveyResponseForExcel(form_model, manager, user, submission_type, filters, keyword)
    formatted_values = SubmissionFormatter().get_formatted_values_for_list(submission_list.get_raw_values(),
        tuple_format=XLS_TUPLE_FORMAT)
    header_list = ExcelFileSubmissionHeader(form_model).header_list
    exported_data, file_name = _prepare_export_data(submission_type, project_name, header_list, formatted_values)
    return _create_excel_response(exported_data, file_name)

def _update_static_info_block_status(form_model_ui, is_errored_before_edit):
    if is_errored_before_edit:
        form_model_ui.update({'is_error_to_success': is_errored_before_edit})
        form_model_ui['status'] = ugettext('Success')
