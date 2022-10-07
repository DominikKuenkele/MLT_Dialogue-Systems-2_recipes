class Template():
    PLACEHOLDER = '&generated'

    def __init__(self, template_file, target_file) -> None:
        self.template_file = template_file
        self.target_file = target_file
    
    def _get_stub(self) -> str:
        raise NotImplementedError("Please implement this method")
    
    def _cleanse_attribute(self, attribute) -> str:
        return attribute.replace(" ", "_")

    def generate_file(self) -> None:
        if self.template_file == '':
            generated = self._get_stub()
        else:
            with open(self.template_file, 'r') as f:
                template = f.read()
            generated = template.replace(self.PLACEHOLDER, self._get_stub())
        with open(self.target_file, 'w') as f:
            f.write(generated)
            