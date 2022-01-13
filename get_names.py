import os
from traitlets.config import get_config
from nbgrader.apps import NbGraderAPI

c = get_config()
c.CourseDirectory.course_id = os.environ["RELEASE_NAME"]
c.CourseDirectory.root = os.environ["HOME"] + "/courses/" + os.environ["RELEASE_NAME"]

api = NbGraderAPI(config=c)
# assignments = []

for i in api.get_assignments():
    # assignments.append(i["name"])
    print(i["name"])
