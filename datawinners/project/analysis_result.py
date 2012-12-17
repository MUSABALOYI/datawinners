from mangrove.utils.json_codecs import encode_json

class AnalysisResult(object):
    def __init__(self, header, field_values, statistics_result, data_sender_list, subject_list, default_sort_order):
        self._header = header
        self._field_values = field_values
        self._statistics_result = statistics_result
        self._data_sender_list = data_sender_list
        self._subject_list = subject_list
        self._default_sort_order = default_sort_order

    @property
    def analysis_result_dict(self):
        return {"datasender_list": self._data_sender_list,
                "default_sort_order": repr(encode_json(self._default_sort_order)),
                "header_list": self._header.header_list,
                "header_name_list": repr(encode_json(self._header.header_list)),
                "header_type_list": repr(encode_json(self._header.header_type_list)),
                "subject_list": self._subject_list,
                "data_list": repr(encode_json(self._field_values)),
                "statistics_result": repr(encode_json(self._statistics_result))}

    @property
    def statistics_result(self):
        return self._statistics_result

    @property
    def field_values(self):
        return self._field_values