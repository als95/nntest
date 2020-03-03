from keras.layers import Dense, Input, LSTM
from keras.models import load_model
from keras.optimizers import Adadelta

from model.interface.model_manager import ModelManager
from before.utils import *


def root_mean_squared_error(y_true, y_pred):
    return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


class Temperature(ModelManager):
    def __init__(self, data_manager, model_name):
        self.model = None
        self.data_manager = data_manager
        self.model_name = model_name

        self.x_train, self.y_train = self.data_manager.get_train_data()
        self.x_test, self.y_test = self.data_manager.get_test_data()

    def get_intermediate_output(self, layer, data):
        intermediate_layer_model = Model(inputs=self.model.input,
                                         outputs=self.model.get_layer(layer.name).output)
        return self.__scale(intermediate_layer_model.predict(np.expand_dims(data, axis=0)))

    def load_model(self):
        self.model = load_model('models/' + self.model_name + '.h5',
                                custom_objects={'root_mean_squared_error': root_mean_squared_error})
        opt = Adadelta(lr=0.001)
        self.model.compile(optimizer=opt, loss='mean_squared_error', metrics=[root_mean_squared_error])
        self.model.summary()
        score = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        print(self.model_name + "'s score : %.8f" % score[1])

    def train_model(self):
        n_hidden = 64
        n_seq = 12
        n_input = 12
        n_output = 1
        iterations = 200
        batch_size = 32

        input_layer = Input(shape=(n_seq, n_input))

        lstm1 = LSTM(n_hidden, return_sequences=True)(input_layer)
        rnn_outputs = LSTM(n_hidden, activation='tanh')(lstm1)

        rnn_outputs = Dense(n_output * 4)(rnn_outputs)
        outputs = Dense(n_output, activation='linear')(rnn_outputs)

        self.model = Model(inputs=input_layer, outputs=outputs)

        opt = Adadelta(lr=0.001)
        self.model.compile(optimizer=opt, loss='mean_squared_error', metrics=[root_mean_squared_error])

        self.model.fit(x=self.x_train, y=self.y_train, validation_data=(self.x_test, self.y_test),
                       batch_size=batch_size, epochs=iterations, shuffle=True)
        self.model.save('models/' + self.model_name + '.h5')

    def test_model(self):
        pass

    def get_layer_name(self, index):
        layer_names = [l.name for l in self.model.layers]
        return layer_names[index]

    def get_layer(self, index):
        return self.model.layers[index]

    def get_prob(self, data):
        data = data[np.newaxis, :]
        prob = np.squeeze(self.model.predict(data))
        return prob

    # calculate the lstm hidden state and cell state manually (no dropout)
    # activation function is tanh
    def cal_hidden_state(self, test, layer_num, data_size=12):
        if layer_num == 0:
            acx = test
        else:
            acx = get_activations_single_layer(self.model, np.array([test]), self.get_layer_name(layer_num - 1))

        units = int(int(self.model.layers[layer_num].trainable_weights[0].shape[1]) / 4)
        # lstm_layer = model.layers[1]
        w = self.model.layers[layer_num].get_weights()[0]
        u = self.model.layers[layer_num].get_weights()[1]
        b = self.model.layers[layer_num].get_weights()[2]

        w_i = w[:, :units]
        w_f = w[:, units: units * 2]
        w_c = w[:, units * 2: units * 3]
        w_o = w[:, units * 3:]

        u_i = u[:, :units]
        u_f = u[:, units: units * 2]
        u_c = u[:, units * 2: units * 3]
        u_o = u[:, units * 3:]

        b_i = b[:units]
        b_f = b[units: units * 2]
        b_c = b[units * 2: units * 3]
        b_o = b[units * 3:]

        # calculate the hidden state value
        h_t = np.zeros((data_size, units))
        c_t = np.zeros((data_size, units))
        f_t = np.zeros((data_size, units))
        h_t0 = np.zeros((1, units))
        c_t0 = np.zeros((1, units))

        for i in range(0, data_size):
            f_gate = hard_sigmoid(np.dot(acx[i, :], w_f) + np.dot(h_t0, u_f) + b_f)
            i_gate = hard_sigmoid(np.dot(acx[i, :], w_i) + np.dot(h_t0, u_i) + b_i)
            o_gate = hard_sigmoid(np.dot(acx[i, :], w_o) + np.dot(h_t0, u_o) + b_o)
            new_c = np.tanh(np.dot(acx[i, :], w_c) + np.dot(h_t0, u_c) + b_c)
            c_t0 = f_gate * c_t0 + i_gate * new_c
            h_t0 = o_gate * np.tanh(c_t0)
            c_t[i, :] = c_t0
            h_t[i, :] = h_t0
            f_t[i, :] = f_gate

        return h_t, c_t, f_t