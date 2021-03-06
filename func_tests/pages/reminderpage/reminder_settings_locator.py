# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from framework.utils.common_utils import *


# By default every locator should be CSS
# Abbr:
# TB - Text Box
# CB - Check Box
# RB - Radio Button
# BTN - Button
# DD - Drop Down
# LINK - Links
# LABEL - Label
# TA - Text Area

# variable to access locators
LOCATOR = "locator"
BY = "by"

FREQUENCY_PERIOD_DD = by_css("select#id_frequency_period")
DAYS_OF_WEEK_DD = by_css("select#id_deadline_week")
DAYS_OF_MONTH_DD = by_css("select#id_deadline_month")
WEEK_DEADLINE_TYPE_DD = by_css("select#id_deadline_type_week")
MONTH_DEADLINE_TYPE_DD = by_css("select#id_deadline_type_month")
DEADLINE_EXAMPLE_LABEL = by_css("div#deadline_example")

BEFORE_DEADLINE_REMINDER_CB = by_css("input#id_should_send_reminders_before_deadline")
NUMBER_OF_DAYS_BEFORE_DEADLINE_TB = by_css("input#id_number_of_days_before_deadline")
BEFORE_DEADLINE_REMINDER_TB = by_css("textarea#id_reminder_text_before_deadline")

ON_DEADLINE_REMINDER_CB = by_css("input#id_should_send_reminders_on_deadline")
ON_DEADLINE_REMINDER_TB = by_css("textarea#id_reminder_text_on_deadline")

AFTER_DEADLINE_REMINDER_CB = by_css("input#id_should_send_reminders_after_deadline")
NUMBER_OF_DAYS_AFTER_DEADLINE_TB = by_css("input#id_number_of_days_after_deadline")
AFTER_DEADLINE_REMINDER_TB = by_css("textarea#id_reminder_text_after_deadline")

ONLY_DATASENDERS_NOT_SUBMITTED_CB = by_css("input#id_whom_to_send_message")
SAVE_BUTTON = by_css("input[value='Save']")

SUCCESS_MESSAGE_LABEL = by_xpath("//div[@class='success-message-box reminder-success']")
SMS_TEXT_COUNTER = "counter_for_reminder_%s_deadline"