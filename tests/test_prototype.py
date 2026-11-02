import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import prototype as p
class PrototypeTests(unittest.TestCase):
 def test_reference_recovery(self):
  _,_,metrics=p.demo()
  self.assertTrue(metrics)
 def test_invalid_data(self):
  with self.assertRaises(ValueError):p.finite([float('nan')])
  with self.assertRaises(ValueError):p.finite([])
 def test_reject_invalid_process_input(self):
  with self.assertRaises(ValueError):p.process([[1,1]],[[1,1]])

 def test_recovery_independent_of_pixel_units(self):
  import numpy as np
  truth=np.random.default_rng(7).random((12,80))
  for scale in (1e-200,1.,1e200):
   with self.subTest(scale=scale), np.errstate(over='raise',invalid='raise',divide='raise'):
    result,overlap=p.process(truth[:,:55]*scale,truth[:,35:]*scale,10,30)
    self.assertEqual(overlap,20)
    np.testing.assert_allclose(result/scale,truth,atol=1e-14)
 def test_constant_images_have_no_reliable_overlap(self):
  import numpy as np
  for value in (0.,1e-200,1e200):
   with self.subTest(value=value), self.assertRaisesRegex(ValueError,'No reliable'):
    p.process(np.full((5,30),value),np.full((5,30),value),5,10)
