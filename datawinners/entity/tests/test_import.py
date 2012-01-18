# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8
from mock import Mock

from mangrove.utils.test_utils.mangrove_test_case import MangroveTestCase
from mangrove.bootstrap import initializer
from mangrove.datastore.queries import get_entity_count_for_type

from datawinners.entity.import_data import import_data

class TestImport(MangroveTestCase):
    def setUp(self):
        MangroveTestCase.setUp(self)
        self.csv_data = """
"form_code","t","n","l","g","d","s","m"
"REG","reporter","Aàman Farafangana ","Farafangana ","-21.8  46.8333","This is a Clinic in near to Farafangana ","r1",987654328
"REG","reporter","Reporter1 Fianarantsoa ","mahajanga ","-20.45  45.1","C'est une clinique à Fianarantsoa","r2",987654329
"REG","reporter","Reporter2 Maintirano ","Maintirano ","-18.05  44.0333","This is a reporter in Maintirano ","r3",987654333
"REG","reporter","Reporter3 Mananjary ","Mananjary ","-21.2  48.3667","This is a reporter in Mananjary ","r4",987654334
"""
        self.csv_data_without_short_code = """
"form_code","t","n","l","g","d","m"
"REG","reporter","Aàman Farafangana ","Farafangana ","-21.8  46.8333","This is a Clinic in near to Farafangana ",987654328
"REG","reporter","Reporter1 Fianarantsoa ","mahajanga ","-20.45  45.1","C'est une clinique à Fianarantsoa",987654329
"REG","reporter","Reporter2 Maintirano ","Maintirano ","-18.05  44.0333","This is a reporter in Maintirano ",987654333
"REG","reporter","Reporter3 Mananjary ","Mananjary ","-21.2  48.3667","This is a reporter in Mananjary ",987654334
"""
        initializer.run(self.manager)

    def tearDown(self):
        MangroveTestCase.tearDown(self)

    def test_should_import_data_senders(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_data
        error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                         manager=self.manager)
        self.assertEqual(4, get_entity_count_for_type(self.manager, entity_type="reporter"))
        self.assertEqual(4, len(imported_entities))
        self.assertEqual('reporter', imported_entities["r1"])
        self.assertEqual('reporter', imported_entities["r2"])
        self.assertEqual('reporter', imported_entities["r3"])
        self.assertEqual('reporter', imported_entities["r4"])

    def test_should_generate_short_code_and_import_data_senders_if_short_code_is_not_given(self):
        file_name = "reporters.csv"
        request = Mock()
        request.GET = {'qqfile': file_name}
        request.raw_post_data = self.csv_data_without_short_code
        error_message, failure_imports, success_message, imported_entities = import_data(request=request,
                                                                                         manager=self.manager)
        self.assertEqual(4, get_entity_count_for_type(self.manager, entity_type="reporter"))
        self.assertEqual(4, len(imported_entities))
        self.assertEqual('reporter', imported_entities["rep1"])
        self.assertEqual('reporter', imported_entities["rep2"])
        self.assertEqual('reporter', imported_entities["rep3"])
        self.assertEqual('reporter', imported_entities["rep4"])
        