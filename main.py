import time
import argparse
import re

from data.mnist import MnistData
from data.mnist_mutant_callback import MnistMutantCallback
from model.mnist import Mnist
from test_nn import *
from model.temperature import Temperature
from data.normal_mutant_callback import NormalMutantCallback
from data.temerature import TemperatureData
from data.temperature_distribution import TemperatureDistribution


def main():
    parser = argparse.ArgumentParser(description='testing for neural network')
    parser.add_argument('--model', dest='model_name', default='temperature', help='')
    parser.add_argument('--seed', dest='seed_num', default='2000', help='')
    parser.add_argument('--threshold_nc', dest='threshold_tc', default='0', help='')
    parser.add_argument('--sec_kmnc', dest='sec_kmnc', default='1', help='')
    parser.add_argument('--threshold_cc', dest='threshold_cc', default='5', help='')
    parser.add_argument('--threshold_gc', dest='threshold_gc', default='0.705', help='')
    parser.add_argument('--symbols_sq', dest='symbols_sq', default='2', help='')
    parser.add_argument('--seq', dest='seq', default='[7,11]', help='')
    parser.add_argument('--size_tkc', dest='size_tkc', default='1', help='')
    parser.add_argument('--size_tkpc', dest='size_tkpc', default='1', help='')
    parser.add_argument('--fold_size', dest='fold_size', default='1', help='')
    parser.add_argument('--mode', dest='mode', default='test', help='')

    args = parser.parse_args()

    model_name = args.model_name
    seed = int(args.seed_num)
    threshold_tc = int(args.threshold_tc)
    sec_kmnc = int(args.sec_kmnc)
    threshold_cc = float(args.threshold_cc)
    threshold_gc = float(args.threshold_gc)
    symbols_sq = int(args.symbols_sq)
    seq = args.seq
    seq = re.findall(r"\d+\.?\d*", seq)
    size_tkc = int(args.size_tkc)
    size_tkpc = int(args.size_tkpc)
    fold_size = int(args.fold_size)
    mode = args.mode

    if 'temperature' in model_name:
        data_distribution = TemperatureDistribution()
        mutant_callback = NormalMutantCallback(data_distribution)
        data_manager = TemperatureData(mutant_callback)
        model_manager = Temperature(model_name)

        test = TestNN(data_manager, model_manager)

        if mode == 'train':
            test.train(fold_size)
        else:
            test.test(seed, threshold_tc, sec_kmnc, threshold_cc, threshold_gc, symbols_sq, seq, size_tkc, size_tkpc)
    elif 'mnist' in model_name:
        model_manager = Mnist(model_name)
        mutant_callback = MnistMutantCallback(model_manager)
        data_manager = MnistData(mutant_callback)

        test = TestNN(data_manager, model_manager)

        if mode == 'train':
            test.train(fold_size)
        else:
            test.test(seed, threshold_tc, sec_kmnc, threshold_cc, threshold_gc, symbols_sq, seq, size_tkc, size_tkpc)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
