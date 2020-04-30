import unittest
from foldingathome import Donor

class TestDonor (unittest.TestCase):

    def test_donor(self):
        donor = Donor("fbuchinger")
        self.assertEqual(donor.name,"fbuchinger",msg="Donor has a username")
        self.assertIsInstance(donor.id, int, msg="Donor has an id")
        self.assertIsInstance(donor.score, int, msg="Donor has a credit score")
        self.assertIsInstance(donor.work_units, int, msg="Donor has a work unit score")
        self.assertIsInstance(donor.rank, int, msg="Donor has a rank")
        self.assertIsInstance(donor.relative_rank, float, msg="Donor has a relative rank compared to other users")

    def test_non_existant_donor(self):
        self.assertRaises(Exception, Donor,"DOESNOTEXIST_poasdokKJKJKALDJSAJKLJSAL", msg="non-existant Donor raises exception")
        
if __name__ == '__main__':
    unittest.main()
