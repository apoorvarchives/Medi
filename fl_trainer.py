from fl_node import FLNode
from model import SimpleMLP, fed_avg, evaluate_model, hash_model

import torch
import random

class FLTrainer:
    def __init__(self, node_data_dict, test_loader, device='cpu'):
        self.nodes = [FLNode(nid, dl, device) for nid, dl in node_data_dict.items()]
        self.test_loader = test_loader
        self.device = device
        self.global_model = SimpleMLP().to(device)

    def run_round(self, local_epochs=1, lr=0.01):
        local_models = []
        contributors = []
        local_scores = {}

        for node in self.nodes:
            node.reset_model(self.global_model)
            trained_model = node.local_train(epochs=local_epochs, lr=lr)
            acc = evaluate_model(trained_model, self.test_loader)
            local_scores[node.id] = acc
            local_models.append(trained_model)
            contributors.append(node.id)

        self.global_model = fed_avg(local_models)
        accuracy = evaluate_model(self.global_model, self.test_loader)
        model_hash = hash_model(self.global_model)

        return self.global_model, model_hash, accuracy, contributors, local_scores

    def get_global_model(self):
        return self.global_model
