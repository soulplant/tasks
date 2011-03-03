from model import session, Task, LogEntry, Tomato, URL
import sys

class Command(object):
    def has_arg(self, arg, long_arg=None):
        for i in range(len(self.args)):
            if self.args[i] == '-' + arg or (long_arg and self.args[i] == '--' + long_arg):
                del(self.args[i])
                return True
        return False
    
    def get_task(self, task_id):
        return session.query(Task).filter_by(id=task_id).one()
    
    def get_tasks(self, **kwargs):
        return session.query(Task).filter_by(**kwargs).order_by(Task.active_order, Task.id).all()

    def get_top_task(self):
        tasks = self.get_tasks(status='active')
        if len(tasks) > 0:
            return tasks[0]
        return None
    
    def no_active_tasks(self):
        print "No active tasks"

class ListTasksCommand(Command):
    name = "list-tasks"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.show_all = self.has_arg('a', 'all')
        self.show_inbox = self.has_arg('i', 'inbox')

    def gather_tasks(self):
        kwargs = {}
        if self.show_all:
            return self.get_tasks()
        if self.show_inbox:
            return self.get_tasks(status='inbox')
        return self.get_tasks(status='active')
    
    def list_tasks(self, tasks):
        if len(tasks) == 0:
            print "No tasks."
            return
        for t in tasks:
            t.show_status_line()
    
    def execute(self):
        self.list_tasks(self.gather_tasks())

class AddTaskCommand(Command):
    name = "add-task"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.should_be_active = self.has_arg('a', 'active')
        self.name = self.args[0]

    def execute(self):
        t = Task(self.name)
        if self.should_be_active:
            t.activate()
        session.add(t)
        session.commit()
        print "Added task %d." % t.id

class ActivateCommand(Command):
    name = "activate"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.deactivate = self.has_arg('d', 'deactivate')
        self.task = self.get_task(int(self.args[0]))

    def execute(self):
        if self.deactivate:
            self.task.deactivate()
            action = "Deactivated"
        else:
            self.task.activate()
            action = "Activated"

        session.commit()
        print "%s task %d" % (action, self.task.id)

class NotesCommand(Command):
    name = "notes"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.task = self.get_task(int(self.args[0]))

    def execute(self):
        print self.task.notes

class TomatoCommand(Command):
    name = "X"
    is_whole = True

    def __init__(self, args):
        Command.__init__(self)
        self.args = args

    def execute(self):
        task = self.get_top_task()
        if not task:
            self.no_active_tasks()
            return
        task.add_tomato(self.is_whole)
        session.commit()
        task.show_progress()

class DashCommand(TomatoCommand):
    name = "-"
    is_whole = False

class ShowCommand(Command):
    name = "show"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args

    def execute(self):
        task = self.get_top_task()
        if not task:
            self.no_active_tasks()
            return
        task.show_progress()

class DoneCommand(Command):
    name = "done"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args

    def execute(self):
        task = self.get_top_task()
        if not task:
            self.no_active_tasks()
            return
        task.done()
        session.commit()
        task.show_progress()
        print "DONE"

Commands = [
    ListTasksCommand,
    AddTaskCommand,
    ActivateCommand,
    NotesCommand,
    TomatoCommand,
    DashCommand,
    ShowCommand,
    DoneCommand,
]

def lookup_command(name):
    for c in Commands:
        if c.name == name:
            return c
    return None

def main():
    if len(sys.argv) == 1:
        print "usage"
        return

    if len(sys.argv) == 1:
        command = ListTasksCommand
    else:
        command = lookup_command(sys.argv[1])
    args = sys.argv[2:]

    if command:
        command(args).execute()
        session.commit()
    else:
        print "unknown command: %s" % sys.argv[1]

main()
