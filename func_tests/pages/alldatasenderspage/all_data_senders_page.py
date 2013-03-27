# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from pages.adddatasenderspage.add_data_senders_page import AddDataSenderPage
from pages.alldatasenderspage.all_data_senders_locator import *
from pages.page import Page
from tests.alldatasenderstests.all_data_sender_data import *


class AllDataSendersPage(Page):
    def __init__(self, driver):
        Page.__init__(self, driver)

    def navigate_to_add_a_data_sender_page(self):
        """
        Function to navigate to add a data sender page of the website

        Return create project page
         """
        self.driver.find(ADD_A_DATA_SENDER_LINK).click()
        return AddDataSenderPage(self.driver)

    def select_a_data_sender_by_mobile(self, data_sender_mobile):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_MOBILE_XPATH % data_sender_mobile)).click()

    def select_a_data_sender_by_id(self, data_sender_id):
        """
        Function to select a data sender on all data sender page
         """
        self.driver.find(by_xpath(DATA_SENDER_CHECK_BOX_BY_UID_XPATH % data_sender_id)).click()

    def select_project(self, project_name):
        """
        Function to select a project on all data sender page
         """
        self.driver.find(by_xpath(PROJECT_CB_XPATH % project_name)).click()

    def select_projects(self, project_names):
        """
        Function to select multiple projects on all data sender page

        Args:
        project_names is list of all the projects

         """
        for project_name in project_names:
            self.select_project(project_name)

    def click_confirm(self, wait=False):
        """
        Function to confirm the association/dissociation with projects on all data sender page
         """
        self.driver.find(CONFIRM_BUTTON).click()
        if wait:
            self.driver.wait_until_modal_dismissed(20)

    def click_cancel(self):
        """
        Function to cancel the association/dissociation with projects on all data sender page
         """
        self.driver.find(CANCEL_LINK).click()

    def click_delete(self, wait=False):
        """
        Function to cancel the association/dissociation with projects on all data sender page
        """
        self.driver.find(DELETE_BUTTON).click()
        if wait:
            self.driver.wait_until_modal_dismissed(7)


    def associate_data_sender(self):
            """
            Function to associate data sender with project
             """
            option_to_select = ASSOCIATE
            self.perform_datasender_action(option_to_select)

    def select_edit_action(self):
            """
            Function to associate data sender with project
             """
            option_to_select = EDIT
            self.perform_datasender_action(option_to_select)

    def perform_datasender_action(self, action_to_be_performed):
        self.driver.find(ACTION_DROP_DOWN).click()
        option = self.driver.find_visible_element(by_id(action_to_be_performed))
        option.click()

    def dissociate_data_sender(self):
        """
        Function to dissociate data sender with project
         """
        option_to_select = DISSOCIATE
        self.perform_datasender_action(option_to_select)

    def get_success_message(self):
        """
        Function to fetch the success message from success label
         """
        return self.driver.find(SUCCESS_MESSAGE_LABEL).text

    def get_delete_success_message(self):

        """
        Function to fetch the success message for delete data sender
        """
        return self.driver.find(DELETE_SUCCESS_MESSAGE).text

    def get_error_message(self):
        """
        Function to fetch the error message from success label
         """
        return self.driver.find(ERROR_MESSAGE_LABEL).text

    def get_project_names(self, data_sender_id):
        """
        Function to fetch the associated project names from the all data senders page
         """
        return self.driver.find(by_xpath(PROJECT_NAME_LABEL_XPATH % data_sender_id)).text

    def get_uid(self, data_sender_mobile):
        """
        Function to fetch the mobile number from the all data senders page
         """
        return self.driver.find(by_xpath(UID_LABEL_BY_MOBILE_XPATH % data_sender_mobile)).text

    def delete_data_sender(self):
        """"
        Function to delete datasender """
        option_to_select = DELETE
        self.perform_datasender_action(option_to_select)

    def check_links(self):
        self.driver.is_element_present(IMPORT_LINK)
        self.driver.is_element_present(ADD_A_DATA_SENDER_LINK)

    def check_sms_device_by_id(self, data_sender_id):
        return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 9)))

    def check_web_device_by_id(self, data_sender_id):
        return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 10)))

    def check_smart_phone_device_by_id(self, data_sender_id):
        return self.driver.is_element_present(by_xpath(DATA_SENDER_DEVICES % (data_sender_id, 11)))

    def open_import_lightbox(self):
        from pages.adddatasenderspage.add_data_senders_locator import OPEN_IMPORT_DIALOG_LINK
        from pages.lightbox.import_datasender_light_box_page import ImportDatasenderLightBox
        self.driver.find(OPEN_IMPORT_DIALOG_LINK).click()
        return ImportDatasenderLightBox(self.driver)

    def get_data_sender_email_by_mobile_number(self, data_sender_mobile):
        return self.driver.find(by_xpath(DATA_SENDER_EMAIL_TD_BY_MOBILE_XPATH % data_sender_mobile)).text

    def select_all_datasender_user(self):
        self.driver.find(CHECK_ALL_DS_USER).click()

    def click_checkall_checkbox(self):
        self.driver.find(CHECKALL_DS_CB).click()

    def get_datasenders_count(self):
        return len(self.driver.find(ALL_DS_ROWS).find_elements(by="tag name", value="tr"))

    def get_checked_datasenders_count(self):
        return len(self.driver.find(ALL_DS_ROWS).find_elements(by="css selector", value="tr td:first-child input[checked]"))

    def click_action_button(self):
        self.driver.find(ACTION_DROP_DOWN).click()

    def is_none_selected_shown(self):
        return self.driver.find(NONE_SELECTED_LOCATOR).is_displayed()

    def actions_menu_shown(self):
        return self.driver.find(ACTION_MENU).is_displayed()

    def is_edit_enabled(self):
        css_class = self.driver.find(EDIT_LI_LOCATOR).get_attribute("class")
        return css_class.find("disabled") < 0

    def is_checkall_checked(self):
        return self.driver.find(CHECKALL_DS_CB).get_attribute("checked") == "true"