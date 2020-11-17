import torch
import torch.nn as nn
import torch.nn.functional as F
from layers import ImplicitGraph
from torch.nn import Parameter
from utils import get_spectral_rad, SparseDropout
import torch.sparse as sparse


class IGNN(nn.Module):
    def __init__(self, nfeat, nhid, nclass, num_node, dropout, kappa=0.9, adj_orig=None):
        super(IGNN, self).__init__()

        self.adj = None
        self.adj_rho = None
        self.adj_orig = adj_orig

        #one layer with V
        self.ig1 = ImplicitGraph(nfeat, nhid, num_node, kappa)
        self.dropout = dropout
        self.X_0 = Parameter(torch.zeros(nhid, num_node), requires_grad=False)
        self.V = nn.Linear(nhid, nclass, bias=False)

    def forward(self, features, adj):
        if adj is not self.adj:
            self.adj = adj
            self.adj_rho = get_spectral_rad(adj)

        x = features
        x = self.ig1(self.X_0, adj, x, F.relu, self.adj_rho, A_orig=self.adj_orig).T
        x = F.normalize(x, dim=-1)
        x = F.dropout(x, self.dropout, training=self.training)
        x = self.V(x)
        return x

