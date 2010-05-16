import unittest
import sys, os
sys.path = ['..'] + sys.path

if __name__ == "__main__":
	ts = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(m) for m in [__import__(mod) for mod in [f[:-3]  for f in os.listdir(".") if f.endswith(".py") and f.startswith("test_")]]])
	unittest.main(defaultTest="ts")

