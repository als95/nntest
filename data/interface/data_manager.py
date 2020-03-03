import abc


class DataManager(__metaclass__=abc.ABCMeta):
    @abc.abstractmethod
    def load_data(self):
        pass

    @abc.abstractmethod
    def mutant_data(self, data):
        pass

    @abc.abstractmethod
    def get_train_data(self):
        pass

    @abc.abstractmethod
    def get_test_data(self):
        pass