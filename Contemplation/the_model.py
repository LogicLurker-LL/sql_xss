import sys
import os

# Add the LNN directory to sys.path
lnn_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../LNN"))
sys.path.append(lnn_path)

from lnn import Predicates, Variable, Exists, Implies, Forall, Model, Fact, World, Iff, And

model = Model()
