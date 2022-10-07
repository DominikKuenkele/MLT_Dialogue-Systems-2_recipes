from Template import Template

class Ontology(Template):
    def __init__(self, template_file, target_file) -> None:
        super().__init__(template_file, target_file)
        self.tags = []
    
    def add_individual(self, name, sort) -> None:
        self.tags.append(f'  <individual name="{self._cleanse_attribute(name)}" sort="{self._cleanse_attribute(sort)}"/>')

    def add_action(self, name) -> None:
        self.tags.append(f'  <action name="{self._cleanse_attribute(name)}"/>')

    def _get_stub(self) -> str:
        return '\n'.join(self.tags)
