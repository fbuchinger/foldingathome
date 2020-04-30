import unittest
from datetime import datetime

from foldingathome import Project

class TestProject (unittest.TestCase):

    def test_project(self):
        project = Project("13851") 
        self.assertEqual(project.id,"13851",msg="project has an id")
        self.assertIsInstance(project.manager, str, msg="project has a manager")
        self.assertIsInstance(project.cause, str, msg="project has a cause")
        self.assertIsInstance(project.modified, datetime, msg="project has a modified date")
        self.assertIsInstance(project.alias_projects, list, msg="project has a list of alias projects")

    def test_non_existant_project(self):
        self.assertRaises(Exception, Project,"DOES_NOT_EXIST_91282", msg="non-existant project raises exception")
        
if __name__ == '__main__':
    unittest.main()
