from project.core.simulation import Simulation
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

if __name__ == "__main__":
    sim = Simulation()
    sim.run()
