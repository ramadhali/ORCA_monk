import unittest
from pathlib import Path
from orca_parsers.orca_parser_gs import *

class TestOrcaParser(unittest.TestCase):
    def load_output(self,filename):
        path=Path("tests")/filename
        return path.read_text()
    
    def test_sp_energy(self):
        output=self.load_output("test_sp.out")
        data=parse_scf_properties(output)
        print(data)                 ## print for SP
        self.assertTrue(data["normal_termination"])
        self.assertIsNotNone(data["final_energy_hartree"])

    def test_opt(self):
        output=self.load_output("test_opt.out")
        data=parse_optimization_properties(output)
        print(data)                 ## print for OPT
        self.assertTrue(data["optimization_converged"])
        self.assertGreater(data["optimization_cycles"],0)

    def test_freq(self):
        output=self.load_output("test_freq.out")
        data=parse_frequency_properties(output)
        print(data)
        self.assertGreater(data["n_frequencies"],0)
        self.assertIsNotNone(data["lowest_frequency_cm-1"])
        self.assertGreaterEqual(data["n_imaginary_frequencies"],0)

    def test_thermo(self):
        output=self.load_output("test_freq.out")
        data=parse_thermochemistry_properties(output)
        print(data)
        self.assertIsNotNone(data["zero_point_energy_hartree"])
        self.assertIsNotNone(data["enthalpy_hartree"])
        self.assertIsNotNone(data["gibbs_free_energy_hartree"])
    
