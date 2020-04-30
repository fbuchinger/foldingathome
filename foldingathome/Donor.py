import requests


class Donor:
    def __init__(self, donorname, team=0):
        r = requests.get(f"https://api.foldingathome.org/user/{donorname}")
        if r.status_code == 200:
            self.donor = r.json()
        else:
            raise Exception(f"No user found with name: {donorname}")


        self.name = self.donor["name"]
        self.id = self.donor["id"]
        self.score = self.donor["score"]
        self.work_units = self.donor["wus"]
        self.rank = self.donor.get("rank", -1)
        self.all_users = self.donor["users"]
        self.relative_rank = self.rank / self.all_users