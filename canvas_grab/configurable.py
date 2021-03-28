class Configurable(object):
    def to_config(self):
        """Serialize self to dict

        Returns:
            dict: serialized configuration
        """
        return {}

    def from_config(self, config):
        """Deserialize a dict to self

        Args:
            config (dict): configuration to deserialize
        """
        pass

class Interactable(object):
    def interact(self):
        """Get configuration from user input
        """
        pass
