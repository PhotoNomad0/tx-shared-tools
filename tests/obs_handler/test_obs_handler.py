import os
import unittest

from door43_tools.obs_handler import OBSInspection


class ObsHandlerTest(unittest.TestCase):

    resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')

    def test_success(self):

        # given
        expected_warnings = 0
        expected_errors = 0
        file_name = 'hu_obs_text_obs/01.html'

        # when
        inspection = self.inspectFile(file_name)

        #then
        self.assertEqual(len(inspection.warnings), expected_warnings)
        self.assertEqual(len(inspection.errors), expected_errors)

    def inspectFile(self, file_name):
        file_path = os.path.join(ObsHandlerTest.resources_dir, file_name)
        self.assertTrue(os.path.isfile(file_path), "")
        inspection = OBSInspection(file_path)
        inspection.run()
        return inspection

