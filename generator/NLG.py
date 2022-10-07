from Template import Template

class NLG(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.matches = []
    
    def add_request(self, action, utterance) -> None:
        self._add_match(f'request({self._cleanse_attribute(action)})', utterance)

    def add_action_completion(self, action, status, utterance) -> None:
        self._add_match(f'report(action_status({self._cleanse_attribute(action)}, {status}))', utterance)

    def _add_match(self, match, utterance) -> None:
        self.matches.append(f'''    {{
        "match": "{match}",
        "utterance": "{utterance}"
    }}''')

    def _get_stub(self) -> str:
        return ',\n'.join(self.matches)
