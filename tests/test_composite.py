import unittest
from src.pydhc import composite
import unittest
import numpy as np
from numpy.typing import NDArray
from numpy.testing import assert_array_max_ulp


class TestComposite(unittest.TestCase):

    def test_ones(self):
        fr = np.arange(0, 10)
        to = np.arange(1, 11)
        cfr = np.arange(0,10,0.1)
        cto = cfr+0.1
        array = np.ones((cto.shape[0],1))
        x  = composite(fr, to, cfr, cto, array)
        y = np.ones((fr.shape[0],1))
        assert_array_max_ulp(x,y,10)

    def test_composite_from_to_shape_fail(self):
        fr = np.arange(0, 10)
        to = np.arange(1, 10)
        with self.assertRaises(AssertionError):
            composite(fr, to, 0, 1, np.ones((1, 1)))

    def test_composite_from_to_shape(self):
        fr = np.arange(0, 10)
        to = np.arange(1, 11)
        cfr = np.arange(1)
        cto = np.arange(1)+1
        composite(fr, to, cfr, cto, np.ones((1, 1)))


if __name__ == "__main__":
    unittest.main()
