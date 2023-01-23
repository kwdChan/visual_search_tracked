import os
from modules.visual_search.recorder import new_subject
os.chdir(os.path.dirname(__file__))

# create a new subject
new_subject(
    datapath = './data',
    subjectID = 'Daniel',
    subjectInfo = {
        "hello": True
    }

)