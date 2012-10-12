# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

import unittest
from mock import Mock, patch
from datawinners.project import helper
from datawinners.project.views import _get_imports_subjects_post_url
from mangrove.datastore.database import  DatabaseManager
from mangrove.datastore.datadict import DataDictType
from mangrove.datastore.entity import Entity
from mangrove.errors.MangroveException import DataObjectNotFound, FormModelDoesNotExistsException
from mangrove.form_model.field import TextField, IntegerField, SelectField, DateField, GeoCodeField, Field
from mangrove.form_model.form_model import FormModel, FORM_CODE
from mangrove.form_model.validation import TextLengthConstraint, NumericRangeConstraint
from project.helper import get_data_sender, NOT_AVAILABLE
from project.tests.submission_log_data import  SUBMISSIONS


class TestHelper(unittest.TestCase):
    def setUp(self):
        self.patcher1 = patch("datawinners.project.helper.create_datadict_type")
        self.patcher2 = patch("datawinners.project.helper.get_datadict_type_by_slug")
        self.create_ddtype_mock = self.patcher1.start()
        self.get_datadict_type_by_slug_mock = self.patcher2.start()
        self.create_ddtype_mock.return_value = Mock(spec=DataDictType)
        self.get_datadict_type_by_slug_mock.side_effect = DataObjectNotFound("", "", "")
        self.dbm = Mock(spec=DatabaseManager)


    def tearDown(self):
        self.patcher1.stop()
        self.patcher2.stop()

    def test_should_return_code_title_tuple_list(self):
        ddtype = Mock(spec=DataDictType)
        question1 = TextField(label="entity_question", code="ID", name="What is associated entity",
            language="en", entity_question_flag=True, ddtype=ddtype)
        question2 = TextField(label="question1_Name", code="Q1", name="What is your name",
            defaultValue="some default value", language="eng", ddtype=ddtype)
        code_and_title = [(each_field.code, each_field.name)for each_field in [question1, question2]]
        self.assertEquals([("ID", "What is associated entity"), ("Q1", "What is your name")], code_and_title)

    def test_should_generate_unique_questionnaire_code(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()
        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()
        dbm = Mock(spec=DatabaseManager)

        form_code_mock.side_effect = FormModelDoesNotExistsException('')
        models_mock.count_projects.return_value = 0
        self.assertEqual(helper.generate_questionnaire_code(dbm), "001")

        models_mock.count_projects.return_value = 1
        self.assertEqual(helper.generate_questionnaire_code(dbm), "002")

        patcher.stop()
        patcher1.stop()

    def test_should_generate_next_questionnaire_code_if_code_already_exists(self):
        patcher = patch("datawinners.project.helper.models")
        models_mock = patcher.start()

        patcher1 = patch("datawinners.project.helper.get_form_model_by_code")
        form_code_mock = patcher1.start()

        dbm = Mock(spec=DatabaseManager)

        models_mock.count_projects.return_value = 1

        def expected_side_effect(*args, **kwargs):
            code = kwargs.get('code') or args[1]
            if code == "003":
                raise FormModelDoesNotExistsException('')
            if code == "002":
                return Mock(spec=FormModel)

        form_code_mock.side_effect = expected_side_effect

        self.assertEqual(helper.generate_questionnaire_code(dbm), "003")

        patcher.stop()
        patcher1.stop()

    def test_should_return_formatted_time_string(self):
        expected_val = "01-01-2011 00:00:00"
        self.assertEquals(expected_val, helper.get_formatted_time_string("01-01-2011 00:00:00"))

    def test_should_return_according_value_for_select_field_case_insensitively(self):
        ddtype = Mock(spec=DataDictType)
        single_select = SelectField(label="multiple_choice_question", code="q",
            options=[("red", "a"), ("yellow", "b"), ('green', "c")], name="What is your favourite colour",
            ddtype=ddtype)
        multiple_answer = SelectField(label="multiple_choice_question", code="q1", single_select_flag=False,
            options=[("value_of_a", "a"), ("value_of_b", "b"), ("value_of_c", 'c' ), ("d", "d"), ("e", "e"), ('f', "f"), ("g", "g"), ("h", "h"),
                     ('i', "i"), ("j", "j"), ("k", "k"), ('l', "l"), ("m", "m"), ("n", "n"), ('o', "o"),
                     ("p", "p"), ("q", "q"), ('r', "r"), ("s", "s"), ("t", "t"), ('u', "u"), ("v", "v"), ("w", "w"),
                     ('x', "x"), ("y", "y"), ("z", "z"), ("value_of_1a", '1a'), ("value_of_1b", "1b"), ("value_of_1c", "1c"), ('1d', "1d")],
            name="What is your favourite colour",
            ddtype=ddtype)
        values = dict({"q":"B", "q1":"b1A1c"})
        single_value = helper.get_according_value(values, single_select)
        multiple_value = helper.get_according_value(values, multiple_answer)
        self.assertEquals(single_value, "yellow")
        self.assertEqual(multiple_value, "value_of_b, value_of_1a, value_of_1c")

    def test_should_return_according_value_for_select_field(self):
        ddtype = Mock(spec=DataDictType)
        single_select = SelectField(label="multiple_choice_question", code="q",
                                options=[("red", "a"), ("yellow", "b"), ('green', "c")], name="What is your favourite colour",
                                ddtype=ddtype)
        multiple_answer = SelectField(label="multiple_choice_question", code="q1", single_select_flag=False,
                                options=[("value_of_a", "a"), ("value_of_b", "b"), ("value_of_c", 'c' ), ("d", "d"), ("e", "e"), ('f', "f"), ("g", "g"), ("h", "h"),
                                    ('i', "i"), ("j", "j"), ("k", "k"), ('l', "l"), ("m", "m"), ("n", "n"), ('o', "o"),
                                    ("p", "p"), ("q", "q"), ('r', "r"), ("s", "s"), ("t", "t"), ('u', "u"), ("v", "v"), ("w", "w"),
                                    ('x', "x"), ("y", "y"), ("z", "z"), ("value_of_1a", '1a'), ("value_of_1b", "1b"), ("value_of_1c", "1c"), ('1d', "1d")],
                                name="What is your favourite colour",
                                ddtype=ddtype)
        values = dict({"q":"b", "q1":"b1a1c"})
        single_value = helper.get_according_value(values, single_select)
        multiple_value = helper.get_according_value(values, multiple_answer)
        self.assertEqual(single_value, "yellow")
        self.assertEqual(multiple_value, "value_of_b, value_of_1a, value_of_1c")


    def _get_text_field(self, name, entity_question_flag=False):
        return TextField(name, "code", name, Mock(spec=DataDictType), entity_question_flag=entity_question_flag)

    def _get_form_fields(self):
        eid_field = Mock(spec=TextField)
        eid_field.code = "eid"
        eid_field.entity_question_flag = True
        eid_field.is_event_time_field = False

        na_field = Mock(spec=Field)
        na_field.code = "na"
        na_field.is_event_time_field = False

        fa_field = Mock(spec=Field)
        fa_field.code = "fa"
        fa_field.is_event_time_field = False

        rd_field = Mock(spec=DateField)
        rd_field.code = "rd"
        rd_field.is_event_time_field = True

        bg_field = Mock(spec=Field)
        bg_field.code = "bg"
        bg_field.is_event_time_field = False

        sy_field = Mock(spec=Field)
        sy_field.code = "sy"
        sy_field.is_event_time_field = False

        gps_field = Mock(spec=Field)
        gps_field.code = "gps"
        gps_field.is_event_time_field = False

        rm_field = Mock(spec=Field)
        rm_field.code = "rm"
        rm_field.is_event_time_field = False

        fields = [eid_field, na_field, fa_field, rd_field, bg_field, sy_field, gps_field, rm_field]
        return fields

    def _create_report_period_question(self, form_model):
        rd_field = Mock(spec=DateField)
        rd_field.code = "rd"
        rd_field.event_time_field_flag = True
        rd_field.date_format = "dd.mm.yyyy"
        form_model.event_time_question = rd_field

    def _prepare_submission_data(self, load_all_rows_in_view, get_data_sender, get_by_short_code, has_report_period_question):
        load_all_rows_in_view.return_value = SUBMISSIONS
        get_data_sender.return_value = ("Sender1", "rep1")
        entity = Mock(spec=Entity)
        get_by_short_code.return_value = entity
        entity.data = {"name": {"value": "realname"}}
        entity.short_code = "cli13"
        form_model = Mock(spec=FormModel)
        form_model.fields = self._get_form_fields()
        form_model.form_code = FORM_CODE
        form_model.entity_type = ["clinic"]
        if has_report_period_question:
            self._create_report_period_question(form_model)
        return form_model


class TestPreviewCreator(unittest.TestCase):
    def test_should_create_basic_fields_in_preview(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type,
            instruction="please write more tests")
        preview = helper.get_preview_for_field(field)
        self.assertEquals("What's in a name?", preview["description"])
        self.assertEquals("nam", preview["code"])
        self.assertEquals("text", preview["type"])
        self.assertEquals("please write more tests", preview["instruction"])


    def test_should_add_constraint_text_for_text_field_with_min(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraints = [TextLengthConstraint(min=10)]
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_with_max(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraints = [TextLengthConstraint(max=100)]
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_with_max_and_min(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        constraints = [TextLengthConstraint(min=10, max=100)]
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type, constraints=constraints)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Between 10 -- 100 characters", preview["constraints"])

    def test_should_add_constraint_text_for_text_field_without_constraint(self):
        type = DataDictType(Mock(DatabaseManager), name="Name type")
        field = TextField(name="What's in a name?", code="nam", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraints"])


    def test_should_add_constraint_text_for_numeric_field_with_min(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericRangeConstraint(min=10)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Minimum 10", preview["constraints"])
        self.assertEqual("integer", preview["type"])

    def test_should_add_constraint_text_for_numeric_field_with_max(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericRangeConstraint(max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("Upto 100", preview["constraints"])

    def test_should_add_constraint_text_for_numeric_field_with_max_and_min(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        constraint = NumericRangeConstraint(min=10, max=100)
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type, constraints=[constraint])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("10 -- 100", preview["constraints"])

    def test_should_add_constraint_text_for_numeric_field_without_constraint(self):
        type = DataDictType(Mock(DatabaseManager), name="age type")
        field = IntegerField(name="What's in the age?", code="nam", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("", preview["constraints"])

    def test_should_return_choices(self):
        type = DataDictType(Mock(DatabaseManager), name="color type")
        field = SelectField(name="What's the color?", code="nam", label="naam", ddtype=type,
            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")])
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select1", preview["type"])
        self.assertEqual([("Red", "a"), ("Green", "b"), ("Blue", "c")], preview["constraints"])

    def test_should_return_choices_type_as_select(self):
        type = DataDictType(Mock(DatabaseManager), name="color type")
        field = SelectField(name="What's the color?", code="nam", label="naam", ddtype=type,
            options=[("Red", "a"), ("Green", "b"), ("Blue", "c")], single_select_flag=False)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("select", preview["type"])

    def test_should_return_date_format(self):
        type = DataDictType(Mock(DatabaseManager), name="date type")
        field = DateField(name="What is the date?", code="dat", label="naam", ddtype=type, date_format="dd/mm/yyyy")
        preview = helper.get_preview_for_field(field)
        self.assertEqual("dd/mm/yyyy", preview["constraints"])

    def test_should_return_geocode_format(self):
        type = DataDictType(Mock(DatabaseManager), name="date type")
        field = GeoCodeField(name="What is the place?", code="dat", label="naam", ddtype=type)
        preview = helper.get_preview_for_field(field)
        self.assertEqual("xx.xxxx yy.yyyy", preview["constraints"])

    def test_should_make_project_post_url_for_import_subject_project_wizard(self):
        url = _get_imports_subjects_post_url('123')
        self.assertEqual("/entity/subject/import/?project_id=123", url)

    def test_should_make_the_post_url_for_import_subject_project_wizard(self):
        url = _get_imports_subjects_post_url()
        self.assertEqual("/entity/subject/import/", url)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_sms(self):
        dbm = Mock(spec=DatabaseManager)
        user = Mock()
        submission = Mock()
        submission.channel = 'sms'
        submission.source = '123321'
        with patch("project.helper.get_org_id_by_user") as get_org_id_by_user:
            get_org_id_by_user.return_value = "123"
            with patch.object(dbm, "load_all_rows_in_view") as load_all_rows_in_view:
                load_all_rows_in_view.return_value = []
                data_sender = get_data_sender( dbm, user, submission )
                self.assertEqual((NOT_AVAILABLE, None, '123321'), data_sender)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_web(self):
        dbm = Mock(spec=DatabaseManager)
        user = Mock()
        submission = Mock()
        submission.channel = 'web'
        submission.source = '123321'
        with patch("project.helper.get_org_id_by_user") as get_org_id_by_user:
            get_org_id_by_user.return_value = "123"
            data_sender = get_data_sender( dbm, user, submission )
            self.assertEqual((NOT_AVAILABLE, None, '123321'), data_sender)

    def test_should_return_N_A_when_the_data_sender_was_deleted_and_send_from_smart_phone(self):
        dbm = Mock(spec=DatabaseManager)
        user = Mock()
        submission = Mock()
        submission.test = False
        submission.channel = 'smartPhone'
        submission.source = '123321'
        with patch("project.helper.get_org_id_by_user") as get_org_id_by_user:
            get_org_id_by_user.return_value = "123"
            data_sender = get_data_sender( dbm, user, submission )
            self.assertEqual((NOT_AVAILABLE, None, '123321'), data_sender)

