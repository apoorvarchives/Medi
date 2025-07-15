import torch
import torch.optim as optim
from model import SimpleMLP, train_model


class FLNode:
    def __init__(self, node_id, local_dataloader, device='cpu'):
        self.id = node_id
        self.local_dataloader = local_dataloader
        self.device = device
        self.model = SimpleMLP().to(self.device)


    def local_train(self, epochs=1, lr=0.01):
        optimizer = optim.SGD(self.model.parameters(), lr=lr)
        criterion = torch.nn.CrossEntropyLoss()
        train_model(self.model, self.local_dataloader, criterion, optimizer, epochs)
        return self.model

    def get_model(self):
        return self.model

    def reset_model(self, global_model):
        self.model.load_state_dict(global_model.state_dict())
