from models.helpers import get_landmark
import os
from os import listdir
import numpy as np
from onn.OnlineNeuralNetwork import ONN
from torch.nn import Module


class simpleODL(Module):
    def __init__(self, features_size=2, max_num_hidden_layers=5, qtd_neuron_per_hidden_layer=10, n_classes=2):
        super(simpleODL, self).__init__()
        #Starting a neural network with feature size of 2, hidden layers expansible until 5, number of neuron per hidden layer = 10 #and two classes.
        self.onn_network = ONN(features_size, max_num_hidden_layers, qtd_neuron_per_hidden_layer, n_classes)



    def forward(self, x, y):
        #Do a partial training
        print(x)
        print("=== y ===")
        print(y)
        self.onn_network.partial_fit(x, y)
        prediction = self.onn_network.predict(x,y)
        return prediction
