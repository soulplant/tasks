from directory import Directory
from task_store import TaskStore
import os
import shutil

if os.path.isdir('tasks'):
    shutil.rmtree('tasks')
d = Directory('tasks')
d.make()

ts = TaskStore(d)

print ts.tasks()

t = ts.make_task('this is a test task')
t.add_to_log('Woo! A test!')
t.save()

for t in ts.tasks():
    print t.name()
