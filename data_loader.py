import torch
from torch.utils.data import DataLoader, TensorDataset, random_split

# Generate synthetic medical-style binary classification data (28x28 like MNIST)
def create_synthetic_data(num_samples=1000):
    X = torch.randn(num_samples, 1, 28, 28)  # image-like input
    y = torch.randint(0, 2, (num_samples,))  # binary labels
    return TensorDataset(X, y)

def load_node_data(num_nodes=3, samples_per_node=1000, test_split=0.2, batch_size=32):
    node_data = {}
    test_loaders = []

    for i in range(num_nodes):
        full_data = create_synthetic_data(num_samples=samples_per_node)
        test_size = int(test_split * samples_per_node)
        train_size = samples_per_node - test_size
        train_data, test_data = random_split(full_data, [train_size, test_size])

        node_data[f"Hospital_{chr(65+i)}"] = DataLoader(train_data, batch_size=batch_size, shuffle=True)
        test_loaders.append(DataLoader(test_data, batch_size=batch_size))

    # Combine all test sets into one for evaluation
    test_dataset = torch.utils.data.ConcatDataset([loader.dataset for loader in test_loaders])
    test_loader = DataLoader(test_dataset, batch_size=batch_size)
    return node_data, test_loader