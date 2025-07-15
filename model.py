# --------------------------- model.py ---------------------------
import torch
import torch.nn as nn
import torch.nn.functional as F
import copy
import hashlib

class SimpleMLP(nn.Module):
    def __init__(self):
        super(SimpleMLP, self).__init__()
        self.fc1 = nn.Linear(4, 16)
        self.fc2 = nn.Linear(16, 8)
        self.out = nn.Linear(8, 2)  # binary classification

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return self.out(x)

def train_model(model, dataloader, criterion, optimizer, epochs=1):
    model.train()
    for _ in range(epochs):
        for inputs, targets in dataloader:
            optimizer.zero_grad()
            output = model(inputs)
            loss = criterion(output, targets)
            loss.backward()
            optimizer.step()
    return model

@torch.no_grad()
def evaluate_model(model, dataloader):
    model.eval()
    correct, total = 0, 0
    for inputs, targets in dataloader:
        output = model(inputs)
        _, predicted = torch.max(output, 1)
        total += targets.size(0)
        correct += (predicted == targets).sum().item()
    return 100.0 * correct / total

def fed_avg(models):
    avg_model = copy.deepcopy(models[0])
    with torch.no_grad():
        for key in avg_model.state_dict().keys():
            avg = sum(model.state_dict()[key] for model in models) / len(models)
            avg_model.state_dict()[key].copy_(avg)
    return avg_model

@torch.no_grad()
def hash_model(model):
    state = model.state_dict()
    flat_tensor = torch.cat([param.flatten().cpu() for param in state.values()])
    return hashlib.sha256(flat_tensor.numpy().tobytes()).hexdigest()
