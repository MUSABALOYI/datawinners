from unittest import TestCase
from django.contrib.auth.models import User
from mangrove.datastore.database import DatabaseManager
from mock import Mock, patch
from accountmanagement.models import NGOUserProfile
from alldata.views import  get_project_info
from project.models import Project, ProjectState

class TestViews(TestCase):
    def test_get_correct_web_submission_link(self):
        request = Mock()
        request.user = Mock(spec = User)
        manager = Mock(spec = DatabaseManager)
        manager.database = dict()
        raw_project = dict(value = dict(_id = "pid", devices = ["sms", "web"],
                                        activity_report = ["no"],
                                        name = "Project Name",
                                        created = "2012-05-23T02:57:09.788294+00:00",
                                        project_type = "survey"))

        project = Project(project_type = "survey", entity_type = "clinic", state = ProjectState.ACTIVE)

        profile = Mock(spec = NGOUserProfile)

        questionnaire = Mock()
        questionnaire.form_code = "q01"


        with patch("datawinners.project.models.Project.load") as get_project:
            get_project.return_value = project
            with patch.object(DatabaseManager, "get") as db_manager:
                db_manager.return_value = questionnaire
                with patch("django.contrib.auth.models.User.get_profile") as get_profile:
                    get_profile.return_value = profile
                    profile.reporter = False
                    user = User()
                    project_info = get_project_info(manager, raw_project, user)
                    self.assertEqual(project_info["web_submission_link"], "/project/testquestionnaire/pid/")
