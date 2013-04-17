from datawinners.messageprovider.tests.test_message_handler import THANKS
from tests.smstestertests.sms_tester_data import SENDER, RECEIVER, SMS

QCODE = 'qcode'
ANSWER = 'answer'
TYPE = "type"
SELECT = "select"
TEXT = "text"
CHECKBOX = "checkbox"


EDITED_ANSWERS = [
    {QCODE: 'q1', ANSWER: 'Test (wp02)', TYPE: SELECT},
    {QCODE: 'q2', ANSWER: '25.12.2013', TYPE: TEXT},
    {QCODE: 'q3', ANSWER: '8', TYPE: TEXT},
    {QCODE: 'q4', ANSWER: '24.12.2012', TYPE: TEXT},
    {QCODE: 'q5', ANSWER: 'LIGHT YELLOW', TYPE: SELECT},
    {QCODE: 'q6', ANSWER: 'admin1', TYPE: TEXT},
    {QCODE: 'q7', ANSWER: ['a'], TYPE: CHECKBOX},
    {QCODE: 'q8', ANSWER: '-18 27', TYPE: TEXT},
    ]


def get_sms_data_with_questionnaire_code(questionnaire_code):
    return {SENDER: "919049008976",
            RECEIVER: '919880734937',
            SMS: questionnaire_code+" wp01 25.12.2010 5 24.12.2010 a admin c 12,12",
            'message': THANKS + u" q1: wp01 q2: 25.12.2010 q3: 5 q4: 24.12.2010 q5: LIGHT RED q6: admin q7: Chlorobia q8: 12.0, 12.0"}
