import abc

from data.interface.data_manager import DataManager


class ModelManager(metaclass=abc.ABCMeta):
    def __init__(self, data_manager: DataManager, model_name):
        self.model = None
        self.data_manager = data_manager
        self.model_name = model_name

    @abc.abstractmethod
    def get_layer_name(self, index):
        pass

    @abc.abstractmethod
    def get_layer(self, index):
        pass

    @abc.abstractmethod
    def get_all_layer(self):
        pass

    @abc.abstractmethod
    def train_model(self):
        pass

    @abc.abstractmethod
    def test_model(self):
        pass

    @abc.abstractmethod
    def get_intermediate_output(self, layer, data):
        pass

    @abc.abstractmethod
    def load_model(self):
        pass

    @abc.abstractmethod
    def get_prob(self, data):
        pass

    @abc.abstractmethod
    def get_lstm_layer(self):
        pass

    @abc.abstractmethod
    def get_fc_layer(self):
        pass
