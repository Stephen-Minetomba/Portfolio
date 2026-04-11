import random

# === PARAMETERS ===
N = 250_000      # number of neurons in the ant brain
connections_per_neuron = 50
T = 100          # number of timesteps
decay = 0.9      # membrane voltage decay

# === INITIALIZE NEURON STATES ===
voltages = [0.0] * N   # membrane potentials
spikes = [0] * N       # spikes (0 or 1)

# === SPARSE CONNECTIONS ===
connections = [[] for _ in range(N)]
weights = [[] for _ in range(N)]
for i in range(N):
    targets = random.sample(range(N), connections_per_neuron)
    connections[i] = targets
    weights[i] = [random.uniform(-1, 1) for _ in targets]

# === PIECEWISE MEMBRANE FUNCTION ===
def piecewise_membrane(x):
    if x < 0.2:
        return 0
    elif x < 0.8:
        return x**2
    else:
        return 1

# === SIMULATION LOOP ===
for t in range(T):
    new_spikes = [0] * N
    for i in range(N):
        # integrate inputs from connected neurons
        input_sum = sum(w * spikes[j] for w, j in zip(weights[i], connections[i]))
        voltages[i] = voltages[i] * decay + input_sum  # apply decay
        spike = piecewise_membrane(voltages[i])
        if spike == 1:
            voltages[i] = 0  # reset after spike
        new_spikes[i] = spike
    spikes = new_spikes

    # Optional: print some info every 10 timesteps
    if t % 10 == 0:
        total_spikes = sum(spikes)
        print(f"Timestep {t}: Total spikes = {total_spikes}")