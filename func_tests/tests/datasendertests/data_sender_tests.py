from framework.base_test import BaseTest
from framework.utils.data_fetcher import fetch_, from_
from pages.datasenderpage.data_sender_page import DataSenderPage
from pages.loginpage.login_page import LoginPage
from pages.websubmissionpage.web_submission_page import WebSubmissionPage
from testdata.test_data import DATA_WINNER_LOGIN_PAGE
from tests.addsubjecttests.add_subject_data import VALID_DATA, SUCCESS_MSG
from tests.datasendertests.data_sender_data import PAGE_TITLE, SECTION_TITLE, SUBJECT_TYPE
from tests.logintests.login_data import DATA_SENDER_CREDENTIALS
from tests.websubmissiontests.web_submission_data import DEFAULT_ORG_DATA, PROJECT_NAME, VALID_ANSWERS

class DataSenderTest(BaseTest):

    def submission_data(self, web_submission_page):
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS)
        web_submission_page.submit_answers()

    def go_to_data_sender_page(self):
        self.driver.go_to(DATA_WINNER_LOGIN_PAGE)
        login_page = LoginPage(self.driver)
        login_page.login_with(DATA_SENDER_CREDENTIALS)
        data_sender_page = DataSenderPage(self.driver)
        return data_sender_page

    def test_send_in_data_to_a_project(self):
        data_sender_page = self.go_to_data_sender_page()
        web_submission_page = data_sender_page.send_in_data()
        self.assertEquals(web_submission_page.get_title(), PAGE_TITLE)
        self.assertEquals(web_submission_page.get_section_title(), SECTION_TITLE)
        self.assertEquals(web_submission_page.get_project_name(), fetch_(PROJECT_NAME, from_(DEFAULT_ORG_DATA)))
        self.submission_data(web_submission_page)
        self.assertEqual(web_submission_page.get_errors(),[])

    def test_go_back_to_project_list_from_data_submission_page(self):
        data_sender_page = self.go_to_data_sender_page()
        web_submission_page = data_sender_page.send_in_data()
        web_submission_page.go_back_to_project_list()
        data_sender_page = DataSenderPage(self.driver)
        self.assertIsNotNone(data_sender_page.get_project_list())

    def test_cancel_data_submission(self):
        data_sender_page = self.go_to_data_sender_page()
        web_submission_page = data_sender_page.send_in_data()
        web_submission_page.fill_questionnaire_with(VALID_ANSWERS)
        warning_dialog = web_submission_page.cancel_submission()
        warning_dialog.cancel()
        web_submission_page = WebSubmissionPage(self.driver)
        self.assertEquals(web_submission_page.get_project_name(), fetch_(PROJECT_NAME, from_(DEFAULT_ORG_DATA)))
        warning_dialog = web_submission_page.cancel_submission()
        warning_dialog.confirm()
        data_sender_page = DataSenderPage(self.driver)
        self.assertIsNotNone(data_sender_page.get_project_list())

    def test_register_subject(self):
        data_sender_page = self.go_to_data_sender_page()
        add_subject_page = data_sender_page.register_subject()
        self.assertEquals(add_subject_page.get_title(), PAGE_TITLE)
        self.assertEquals(add_subject_page.get_section_title(), SECTION_TITLE)
        self.assertEquals(add_subject_page.get_subject_type(), SUBJECT_TYPE)
        add_subject_page.add_subject_with(VALID_DATA)
        add_subject_page.submit_subject()
        message = fetch_(SUCCESS_MSG, from_(VALID_DATA))
        self.assertRegexpMatches(add_subject_page.get_flash_message(), message)


    def test_go_back_to_project_list_from_register_subject_page(self):
        data_sender_page = self.go_to_data_sender_page()
        add_subject_page = data_sender_page.register_subject()
        add_subject_page.go_back_to_project_list()
        data_sender_page = DataSenderPage(self.driver)
        self.assertIsNotNone(data_sender_page.get_project_list())
