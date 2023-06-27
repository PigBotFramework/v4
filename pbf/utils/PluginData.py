import json

from ..model.PluginSettingsModel import PluginSettingsModel


class PluginData:
    pluginName: str = None

    def __init__(self, pluginName: str) -> None:
        self.pluginName = pluginName

    def get(self, key: str, *args, **kwargs):
        return json.loads(PluginSettingsModel(package_name=self.pluginName, key=key)._get('value', *args, **kwargs))

    def set(self, key: str, value):
        return PluginSettingsModel(package_name=self.pluginName, key=key)._set(value=json.dumps(value))

    def delete(self, key: str):
        PluginSettingsModel(package_name=self.pluginName, key=key)._delete()
