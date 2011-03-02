from task import Task

class TaskStore(object):
    def __init__(self, directory):
        self._directory = directory

    def _next_task_id(self):
        ds = self._directory.directories()
        max_id = 0
        for d in ds:
            if int(d.name()) > max_id:
                max_id = int(d.name())
        return str(max_id + 1)

    def tasks(self):
        result = []
        for d in self._directory.directories():
            result.append(Task(d))
        return result
        # return [Task(d) for d in self._directory.directories()]

    def make_task(self, name):
        task_id = self._next_task_id()
        d = self._directory.directory(task_id)
        t = Task(d)
        t.set_name(name)
        return t
