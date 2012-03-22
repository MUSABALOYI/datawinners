# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mangrove.contrib.deletion import ENTITY_DELETION_FORM_CODE

from mangrove.datastore.datadict import get_datadict_type_by_slug,\
    create_datadict_type
from mangrove.datastore.entity import get_by_short_code_include_voided
from mangrove.errors import MangroveException
from mangrove.form_model.field import TextField, HierarchyField, GeoCodeField, TelephoneNumberField
from mangrove.form_model.form_model import FormModel, NAME_FIELD,\
    NAME_FIELD_CODE, LOCATION_TYPE_FIELD_NAME, LOCATION_TYPE_FIELD_CODE,\
    GEO_CODE, MOBILE_NUMBER_FIELD, MOBILE_NUMBER_FIELD_CODE,\
    SHORT_CODE_FIELD, REGISTRATION_FORM_CODE,\
    ENTITY_TYPE_FIELD_CODE, GEO_CODE_FIELD_NAME, SHORT_CODE, REPORTER
from mangrove.form_model.validation import TextLengthConstraint,\
    RegexConstraint
from mangrove.transport.player.player import WebPlayer
from mangrove.utils.types import is_empty, is_sequence
import re
from mangrove.errors.MangroveException import NumberNotRegisteredException,\
    DataObjectNotFound
from mangrove.transport.reporter import find_reporter_entity
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _, get_language
from datawinners.accountmanagement.models import Organization,\
    DataSenderOnTrialAccount
from datawinners.location.LocationTree import get_location_tree
from mangrove.transport import Request, TransportInfo
from datawinners.messageprovider.message_handler import\
    get_success_msg_for_registration_using
from datawinners.location.LocationTree import get_location_hierarchy
from datawinners.utils import get_organization

FIRSTNAME_FIELD = "firstname"
FIRSTNAME_FIELD_CODE = "f"

def remove_hyphens(telephone_number):
    return re.sub('[- \(\)+]', '', smart_unicode(telephone_number))


def unique(dbm, telephone_number):
    telephone_number = remove_hyphens(telephone_number)
    try:
        find_reporter_entity(dbm, telephone_number)
    except NumberNotRegisteredException:
        return True
    return False


def _get_or_create_data_dict(dbm, name, slug, primitive_type, description=None):
    try:
        ddtype = get_datadict_type_by_slug(dbm, slug)
    except DataObjectNotFound:
        ddtype = create_datadict_type(dbm=dbm, name=name, slug=slug,
            primitive_type=primitive_type, description=description)
    return ddtype


def _create_constraints_for_mobile_number():
    mobile_number_length = TextLengthConstraint(max=15)
    mobile_number_pattern = RegexConstraint(reg='^[0-9]+$')
    mobile_constraints = [mobile_number_length, mobile_number_pattern]
    return mobile_constraints


def _generate_form_code(manager, prefix, rank=''):
    form_code = "%s%s" % (prefix, rank)
    rows = manager.load_all_rows_in_view("questionnaire", key=form_code)
    if len(rows) > 0:
        rank = 1 if rank is '' else rank + 1
        form_code = _generate_form_code(manager, prefix, rank)
    return form_code


def _create_registration_form(manager, entity_name=None, form_code=None, entity_type=None, language='en'):
    code_generator = question_code_generator()
    location_type = _get_or_create_data_dict(manager, name='Location Type', slug='location', primitive_type='string')
    geo_code_type = _get_or_create_data_dict(manager, name='GeoCode Type', slug='geo_code', primitive_type='geocode')
    name_type = _get_or_create_data_dict(manager, name='Name', slug='name', primitive_type='string')
    mobile_number_type = _get_or_create_data_dict(manager, name='Mobile Number Type', slug='mobile_number',
        primitive_type='string')

    question1 = TextField(name=FIRSTNAME_FIELD, code=code_generator.next(),
        label=_("What is the %(entity_type)s's first name?") % {'entity_type': entity_name},
        defaultValue="some default value", language=language, ddtype=name_type,
        instruction=_("Enter a %(entity_type)s first name") % {'entity_type': entity_name})

    question2 = TextField(name=NAME_FIELD, code=code_generator.next(),
        label=_("What is the %(entity_type)s's last name?") % {'entity_type': entity_name},
        defaultValue="some default value", language=language, ddtype=name_type,
        instruction=_("Enter a %(entity_type)s last name") % {'entity_type': entity_name})
    question3 = HierarchyField(name=LOCATION_TYPE_FIELD_NAME, code=code_generator.next(),
        label=_("What is the %(entity_type)s's location?") % {'entity_type': entity_name},
        language=language, ddtype=location_type, instruction=unicode(_("Enter a region, district, or commune")))
    question4 = GeoCodeField(name=GEO_CODE_FIELD_NAME, code=code_generator.next(),
        label=_("What is the %(entity_type)s's GPS co-ordinates?") % {'entity_type': entity_name},
        language=language, ddtype=geo_code_type,
        instruction=unicode(_("Answer must be GPS co-ordinates in the following format: xx.xxxx,yy.yyyy Example: -18.1324,27.6547 ")))
    question5 = TelephoneNumberField(name=MOBILE_NUMBER_FIELD, code=code_generator.next(),
        label=_("What is the %(entity_type)s's mobile telephone number?") % {'entity_type': entity_name},
        defaultValue="some default value", language=language, ddtype=mobile_number_type,
        instruction=_(
            "Enter the (%(entity_type)s)'s number with the country code and telephone number. Example: 261333745269") % {
            'entity_type': entity_name}, constraints=(
            _create_constraints_for_mobile_number()))
    question6 = TextField(name=SHORT_CODE_FIELD, code=code_generator.next(),
        label=_("What is the %(entity_type)s's Unique ID Number?") % {'entity_type': entity_name},
        defaultValue="some default value", language=language, ddtype=name_type,
        instruction=unicode(_("Enter an id, or allow us to generate it")),
        entity_question_flag=True,
        constraints=[TextLengthConstraint(max=12)], required=False)
    questions = [question1, question2, question3, question4, question5, question6]

    form_model = FormModel(manager, name=entity_name, form_code=form_code, fields=questions, is_registration_model=True,
        entity_type=entity_type, language=language)
    return form_model


def create_registration_form(manager, entity_name):
    if is_sequence(entity_name):
        entity_name = entity_name[0]
    prefix = entity_name.lower()[:3]
    form_code = _generate_form_code(manager, prefix)
    form_model = _create_registration_form(manager, entity_name, form_code, [entity_name], language=get_language())
    form_model.save()
    return form_model


def _associate_data_sender_to_project(dbm, project, project_id, response):
    project = project.load(dbm.database, project_id)
    project.data_senders.append(response.short_code)
    project.save(dbm)


def get_country_appended_location(location_hierarchy, country):
    return location_hierarchy + "," + country if location_hierarchy is not None else None


def _get_data(form_data, country):
    #TODO need to refactor this code. The master dictionary should be maintained by the registration form model
    mapper = {'telephone_number': MOBILE_NUMBER_FIELD_CODE, 'geo_code': GEO_CODE, 'Name': NAME_FIELD_CODE,
              'location': LOCATION_TYPE_FIELD_CODE}
    data = dict()
    data[mapper['telephone_number']] = form_data.get('telephone_number')
    data[mapper['location']] = get_country_appended_location(form_data.get('location'), country)
    data[mapper['geo_code']] = form_data.get('geo_code')
    data[mapper['Name']] = form_data.get('first_name')
    data['form_code'] = REGISTRATION_FORM_CODE
    data[ENTITY_TYPE_FIELD_CODE] = 'Reporter'
    return data


def _add_data_sender_to_trial_organization(telephone_number, org_id):
    data_sender = DataSenderOnTrialAccount.objects.model(mobile_number=telephone_number,
        organization=Organization.objects.get(org_id=org_id))
    data_sender.save()


def process_create_datasender_form(dbm, form, org_id, project):
    message = None
    if form.is_valid():
        telephone_number = form.cleaned_data["telephone_number"]
        if not unique(dbm, telephone_number):
            form._errors['telephone_number'] = form.error_class(
                [(u"Sorry, the telephone number %s has already been registered") % (telephone_number,)])
            return message

        organization = Organization.objects.get(org_id=org_id)
        if organization.in_trial_mode:
            if DataSenderOnTrialAccount.objects.filter(mobile_number=telephone_number).exists():
                form._errors['telephone_number'] = form.error_class(
                    [(u"Sorry, this number has already been used for a different DataWinners trial account.")])
                return message
            else:
                _add_data_sender_to_trial_organization(telephone_number, org_id)

        try:
            web_player = WebPlayer(dbm, location_tree=get_location_tree(), get_location_hierarchy=get_location_hierarchy)
            response = web_player.accept(Request(message=_get_data(form.cleaned_data, organization.country),
                transportInfo=TransportInfo(transport='web', source='web', destination='mangrove')))
            message = get_success_msg_for_registration_using(response, "web")
            project_id = form.cleaned_data["project_id"]
            if not is_empty(project_id):
                _associate_data_sender_to_project(dbm, project, project_id, response)
        except MangroveException as exception:
            message = exception.message

    return message


def question_code_generator():
    i = 1
    while 1:
        code = 'q' + str(i)
        yield code
        i += 1


def delete_entity_instance(manager, all_ids, entity_type, transport_info):
    web_player = WebPlayer(manager)
    for entity_id in all_ids:
        message = {ENTITY_TYPE_FIELD_CODE: entity_type,
                   SHORT_CODE: entity_id,
                   'form_code': ENTITY_DELETION_FORM_CODE}
        mangrove_request = Request(message, transport_info)
        web_player.accept(mangrove_request)

def delete_datasender_for_trial_mode(manager, all_ids, entity_type):
    for entity_id in all_ids:
        entity_to_be_deleted = get_by_short_code_include_voided(manager, entity_id, [entity_type])
        DataSenderOnTrialAccount.objects.get(mobile_number=entity_to_be_deleted.value(MOBILE_NUMBER_FIELD)).delete()

