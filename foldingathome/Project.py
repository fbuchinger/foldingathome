import requests
import requests_cache
import datetime
from collections import defaultdict

requests_cache.install_cache('foldingathome_cache')

class Project:
    def __init__ (self, project_id):
        proj_req = requests.get(f"https://api.foldingathome.org/project/{project_id}")
        if proj_req.status_code == 200:
            self.project = proj_req.json()
        else:
            raise Exception(f"No project found with id: {project_id}")
        self.id = project_id
        self.manager = self.project["manager"]
        self.institution = self.project["institution"]
        self.cause = self._define_cause(self.project["cause"])
        self.modified = datetime.datetime.strptime(self.project["modified"], '%Y-%m-%d %H:%M:%S')
        self.description = self._prepare_description(self.project["description"])
        self.alias_projects = self._calculate_alias_ids(self.project["projects"])
        self.active_alias_projects = [project_id]
        self.prcgs = []


    def _calculate_alias_ids (self, alias_string):
        aliases = alias_string.split(",")
        alias_list = []
        for alias in aliases:
            # alias ranges like "14799-14850"
            if "-" in alias:
                alias_parts = alias.split("-")
                expanded_aliasrange = list(range(int(alias_parts[0]), int(alias_parts[1]) + 1))
                alias_list.extend(expanded_aliasrange)
            else:
                alias_list.append(alias)
        alias_list.append(self.id)
        return list(set(alias_list))

    def _define_cause (self, original_cause):
        if original_cause == "unspecified":
            description = self.project["description"].lower()
            covid_kws = ["coronavirus","covid-19", "sars-cov","sars2-ncov"]
            for kw in covid_kws:
                if kw in description:
                    return "covid-19"
        return original_cause

    def _prepare_description (self, description):
        description = description.split(" ")[:100]
        return (" ").join(description)

    def add_prcg (self, project_id, run = None, clone = None, generation = None):
        try:
            if not (isinstance(project_id,PRCG)):
                prcg = PRCG(project_id, run, clone, generation)
            else:
                prcg = project_id
            existing_prcg_ids = [e_prcg.get_id() for e_prcg in self.prcgs]
            if prcg and prcg.get_id() not in existing_prcg_ids:
                self.prcgs.append(prcg)
        except:
            raise

    def get_credits (self, fah_username):
        total_credits = 0
        for prcg in self.prcgs:
            total_credits += prcg.get_credit_for_user(fah_username)
        return total_credits



    def is_alias (self, project_id):
        return project_id in self.alias_projects

    def set_active_alias (self, project_id):
        """define an alias project the user has worked on """
        self.active_alias_projects.append(project_id)
        return 

    def get_active_aliases (self):
        """define an alias project the user has worked on """
        return list(set(self.active_alias_projects))

class PRCG:
    def __init__(self, project,run, clone, generation):
        self.project = project
        self.run = run
        self.clone = clone
        self.generation = generation
        prcg_req = requests.get(self.get_api_link())
        if prcg_req.status_code == 200:
            self.prcg_data = prcg_req.json()
        else:
            raise Exception(f"No prcg found with the combination: {project},{run}, {clone}, {generation}")
        
    def get_api_link (self):
        return f"https://api.foldingathome.org/project/{self.project}/run/{self.run}/clone/{self.clone}/gen/{self.generation}"

    def was_completed_by_user (self, fah_username):
        for entry in self.prcg_data:
            if entry["user"] == fah_username and entry["code"].lower() == "ok":
                return True
        return False


    def get_credit_for_user (self, fah_username):
        for entry in self.prcg_data:
            if entry["user"] == fah_username:
                return entry.get("credit",0)
        return 0

    def get_id(self):
        id_list = [self.project,self.run, self.clone, self.generation]
        str_list = [str(id) for id in id_list]
        return f"PRCG ({', '.join(str_list)})"

    def get_calculation_dates_for_user (self, fah_username = None):
        for entry in self.prcg_data:
            if entry["user"] == fah_username:
                assign_time = datetime.datetime.strptime(entry["assign_time"], '%Y-%m-%d %H:%M:%S')
                credit_time = datetime.datetime.strptime(entry["credit_time"], '%Y-%m-%d %H:%M:%S')

                return {
                    "assign_time": assign_time,
                    "credit_time": credit_time,
                    "calculation_days": entry["days"],
                    "calculation_time": credit_time - assign_time
                }
                






class Projects:
    def __init__ (self):
        self.projects = []

    def add_project (self, project_id):
        existing_project = self.get_project_by_id(project_id)
        if existing_project is not None:
            existing_project.set_active_alias(project_id)
            return existing_project

        if isinstance(project_id, Project):
            project = project_id
        else:
            project = Project(project_id)
        self.projects.append(project)
        return project

    def get_credits_for_user (self, fah_username):
        total_credits = 0
        for project in self.projects:
            total_credits += project.get_credits(fah_username)
        return total_credits

    def get_projects_by_cause (self):
        projects_by_cause = defaultdict(Projects)
        for project in self.projects:
            projects_by_cause[project.cause].add_project(project)
        return projects_by_cause

    def get_project_by_id (self, project_id):
        for project in self.projects:
            if project.is_alias(project_id):
                return project



