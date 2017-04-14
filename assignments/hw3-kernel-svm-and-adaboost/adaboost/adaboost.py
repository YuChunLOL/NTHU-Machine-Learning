import numpy as np

from tree import ShallowDecisionTree
from utils import zero_one_loss

class AdaboostClassifer:
    """ Class labels need to be {+1, -1} """
    def __init__(self, data, param={}, scorer=zero_one_loss, verbose=False):

        self.train_X = data['train_X']
        self.train_y = data['train_y']
        self.test_X = data['test_X']
        self.test_y = data['test_y']

        self.base_classifer = param.get('base_classifer', ShallowDecisionTree)
        self.num_classifer = param.get('num_classifer', 5)
        self.scorer = scorer
        self.verbose = verbose

        self.sample_weights = np.ones_like(self.train_y).astype(float) / len(self.train_y)

        self.classifer_weights = np.ones(self.num_classifer) / self.num_classifer
        self.classifers = []

    def train(self, info=''):
        """ Perform adaptive boosting """

        if info:
            print('-'*100)
            print('[*] {}'.format(info))

        for t in range(self.num_classifer):
            classifer = self.base_classifer(data={'X': self.train_X, 'y': self.train_y}, sample_weights=self.sample_weights)
            classifer.train()

            y_pred = classifer.hypothesis(X=self.train_X)
            y_truth = self.train_y
            error = self.scorer(y_truth, y_pred, sample_weights=self.sample_weights)

            self.classifer_weights[t] = 0.5 * np.log((1 - error) / error)
            normalization_factor = 2 * np.sqrt(error * (1 - error))
            self.sample_weights = self.sample_weights * np.exp(-self.classifer_weights[t]*y_truth*y_pred) / normalization_factor

            self.classifers.append(classifer)

            if self.verbose:
                print('-'*100)
                print('[*] {}-th classifer weight: {}'.format(t+1, self.classifer_weights[t]))
                print('[*] {}-th classifer error: {}'.format(t+1, error))
                print('[*] {}-th classifer hypothesis: {}'.format(t+1, self.classifers[t].param))
                print('{}'.format(self.classifers[t]))

    def hypothesis(self, X):
        y_pred = np.zeros(len(X))
        for t in range(len(self.classifers)):
            y_pred += self.classifer_weights[t] * self.classifers[t].hypothesis(X)
        return np.sign(y_pred)
