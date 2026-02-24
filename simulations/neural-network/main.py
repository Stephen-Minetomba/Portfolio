def piecewise_membrane(x):
    if x < 0.2:
        return 0  # sub-threshold, nothing happens
    elif x < 0.8:
        return x**2  # amplify intermediate voltages
    else:
        return 1  # spike threshold reached

class Neuron:
    def __init__(self, bias, weights, inputs):
        self.bias = bias
        self.weights = weights
        self.inputs = inputs

    def value(self):
        return piecewise_membrane(self.bias + sum(w*x for w,x in zip(self.weights, self.inputs)))

inputs = [0, 1]

# Test 1:
## Hidden layer 1
n1 = Neuron(bias=0.0, weights=[1, 1], inputs=inputs) # or gate using neuron
n2 = Neuron(bias=-1, weights=[1, 1], inputs=inputs) # and gate using neuron
## Hidden layer 2
n3 = Neuron(bias=-0.5, weights=[1, -2], inputs=[n1.value(), n2.value()]) # xor gate using neuron
## Output layer
neuron = Neuron(bias=0.0, weights=[8], inputs=[n3.value()]) # x8 multiplier using neuron

print(neuron.value())