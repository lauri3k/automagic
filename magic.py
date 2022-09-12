import os
from traitlets.config import get_config
from nbgrader.apps import NbGraderAPI
from ngshare_exchange import configureExchange

c = get_config()
configureExchange(c, "http://ngshare:8080/services/ngshare")
c.CourseDirectory.course_id = os.environ["RELEASE_NAME"]
c.CourseDirectory.root = os.environ["HOME"] + "/courses/" + os.environ["RELEASE_NAME"]
c.CourseDirectory.db_url = os.getenv("NBGRADER_DB_URL")

c.GenerateFeedback.preprocessors = [
    "nbgrader.preprocessors.GetGrades",
    "nbconvert.preprocessors.CSSHTMLHeaderPreprocessor",
    "nbgrader.preprocessors.ClearHiddenTests",
    "nbgrader.preprocessors.ClearOutput",
]

api = NbGraderAPI(config=c)
assignments = []

for i in api.get_released_assignments():
    print(api.collect(i))

for i in api.get_assignments():
    if i["num_submissions"] > 0:
        assignments.append(i["name"])

for n in assignments:
    students = api.get_submitted_students(n)
    for s in students:
        print(api.autograde(n, s, force=False))
    print(api.generate_feedback(n, force=False))
    print(api.release_feedback(n))
