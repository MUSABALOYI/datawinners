# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.broadcastSMSpage.broadcast_sms_page import BroadcastSmsPage
from pages.dataanalysispage.data_analysis_page import DataAnalysisPage
from pages.lightbox.light_box_page import LightBox
from pages.projectdatasenderspage.project_data_senders_page import ProjectDataSendersPage
from pages.projectoverviewpage.project_overview_locator import *
from pages.page import Page
from pages.questionnairetabpage.questionnaire_tab_page import QuestionnaireTabPage
from pages.reminderpage.all_reminder_page import AllReminderPage
from pages.smstesterlightbox.sms_tester_light_box_page import SMSTesterLightBoxPage


class ProjectOverviewPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_data_page(self):
        self.driver.find(DATA_TAB).click()
        return DataAnalysisPage(self.driver)

    def navigate_to_datasenders_page(self):
        self.driver.find(DATASENDERS_TAB).click()
        return ProjectDataSendersPage(self.driver)

    def navigate_to_reminder_page(self):
        self.driver.find(MESSAGES_AND_REMINDERS_TAB).click()
        return AllReminderPage(self.driver)

    def navigate_to_data_page(self):
        self.driver.find(DATA_TAB).click()
        return DataAnalysisPage(self.driver)

    def navigate_to_edit_project_page(self):
        self.driver.find(PROJECT_EDIT_LINK).click()
        from pages.createprojectpage.create_project_page import CreateProjectPage
        return CreateProjectPage(self.driver)

    def open_activate_project_light_box(self):
        self.driver.find(ACTIVATE_PROJECT_LINK).click()
        return LightBox(self.driver)

    def get_status_of_the_project(self):
        return self.driver.find(PROJECT_STATUS_LABEL).text

    def open_sms_tester_light_box(self):
        self.driver.find(TEST_QUESTIONNAIRE_LINK).click()
        return SMSTesterLightBoxPage(self.driver)

    def navigate_send_message_tab(self):
        self.driver.find(SEND_MESSAGE_TAB).click()
        return BroadcastSmsPage(self.driver)

    def open_sms_questionnaire_preview(self):
        self.driver.find(by_css(".sms_questionnaire")).click()
        return LightBox(self.driver)

    def navigate_to_questionnaire_tab(self):
        self.driver.find(QUESTIONNAIRE_TAB).click()
        return QuestionnaireTabPage(self.driver)

    def get_project_title(self):
        return self.driver.find(PROJECT_TITLE_LOCATOR).text.lower()