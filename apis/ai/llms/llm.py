from .constants import MAX_RETRIES


# Define an abstract LLMProvider class
class LLMProvider:
    def __init__(self):
        self.temperature = 0
        self.max_retries = MAX_RETRIES

    def get_property(self, property_name):
        return getattr(self, property_name, "Property Not Found")
