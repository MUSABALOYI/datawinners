from mangrove.form_model.form_model import FORM_CODE
from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase

from mangrove.utils.test_utils.submission_builder import SubmissionBuilder
from datawinners.project.survey_response_router import successful_survey_responses, undeleted_survey_responses

class TestGetSubmissions(MangroveTestCase):
    def setUp(self):
        super(TestGetSubmissions, self).setUp()
        self.submission_builder = SubmissionBuilder(self.manager)

    def test_should_get_successful_submissions(self):
        submissions = self.submission_builder.build_two_successful_submissions()
        self.submission_builder.build_two_error_submission()

        success_submissions = successful_survey_responses(self.manager, FORM_CODE)

        self.assertEqual(2, len(success_submissions))

        self._assertSubmissionsEqual(submissions, success_submissions)

    def test_should_get_undeleted_submissions(self):
        submissions = self.submission_builder.build_four_submissions()
        submissions[-1].void()
        submissions.remove(submissions[-1])

        expected_undeleted_submission = undeleted_survey_responses(self.manager, FORM_CODE)

        self.assertEqual(3, len(expected_undeleted_submission))

        self._assertSubmissionsEqual(expected_undeleted_submission, submissions)

    def _assertSubmissionsEqual(self, submission_list1, submission_list2):
        submission_list1_ids = map(lambda x: x.id, submission_list1)
        submission_list2_ids = map(lambda x: x.id, submission_list2)

        self.assertItemsEqual(submission_list1_ids, submission_list2_ids)
        


