#!/usr/bin/python
from __future__ import with_statement
from sqlalchemy.sql.expression import desc
from model import session, Task, LogEntry, Tomato, URL
import os
import sys
import tempfile

class Command(object):
    def has_arg(self, arg, long_arg, next_arg=False):
        for i in range(len(self.args)):
            if self.args[i] == '-' + arg or (long_arg and self.args[i] == '--' + long_arg):
                del(self.args[i])
                if next_arg:
                    attached_arg = self.args[i]
                    del(self.args[i])
                    return attached_arg
                return True
        if next_arg:
            return None
        return False
    
    def get_task(self, task_id):
        return session.query(Task).filter_by(id=task_id).one()
    
    def get_tasks(self, **kwargs):
        return session.query(Task).filter_by(**kwargs).order_by(desc(Task.active_order), Task.id).all()

    def get_active_tasks(self):
        return self.get_tasks(status='active')

    def get_top_task(self):
        tasks = self.get_active_tasks()
        if len(tasks) > 0:
            return tasks[0]
        return None
    
    def no_active_tasks(self):
        print "No active tasks"

    def get_named_task(self):
        if len(self.args) == 1:
            return self.get_task(int(self.args[0]))
        else:
            return self.get_top_task()

    def edit_text(self, input_text):
        temp_file = tempfile.mkstemp()[1]
        with open(temp_file, 'w') as f:
            f.write(input_text)
        result = os.system("vim %s" % temp_file)
        if result == 0:
            with open(temp_file, 'r') as f:
                output_text = f.read()
                return output_text
        return None

class ListTasksCommand(Command):
    name = "list-tasks"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.show_all = self.has_arg('a', 'all')
        self.show_inbox = self.has_arg('i', 'inbox')
        self.show_blocked = self.has_arg('b', 'blocked')

    def gather_tasks(self):
        kwargs = {}
        if self.show_all:
            return self.get_tasks()
        if self.show_blocked:
            return self.get_tasks(status='blocked')
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
        self.block = self.has_arg('b', 'block', True)
        self.inbox = self.has_arg('i', 'inbox')
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        if self.deactivate:
            self.task.deactivate()
            action = "Deactivated"
        elif self.block:
            self.task.block(self.block)
            action = "Blocked"
        elif self.inbox:
            self.task.inbox()
            action = "Inboxed"
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
        self.edit = self.has_arg('e', 'edit')
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        if not self.edit:
            print self.task.notes
            return
        current_text = ''
        if self.task.notes:
            current_text = self.task.notes
        edited_text = self.edit_text(current_text)
        if not edited_text:
            print "Cancelled notes update."
            return
        self.task.notes = edited_text
        session.commit()
        print "Updated notes."

class TomatoCommand(Command):
    name = "X"
    is_whole = True

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        self.task.add_tomato(self.is_whole)
        session.commit()
        self.task.show_progress()

class DashCommand(TomatoCommand):
    name = "-"
    is_whole = False

class ShowCommand(Command):
    name = "show"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.progress_only = self.has_arg('p', 'progress')
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        if self.progress_only:
            self.task.show_progress()
        else:
            self.task.show()

class DoneCommand(Command):
    name = "done"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        self.task.done()
        session.commit()
        self.task.show_progress()
        print "DONE"

class ReorderCommand(Command):
    name = "reorder"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args

    def set_task_active_order(self, task_id, active_order):
        self.get_task(task_id).set_active_order(active_order)

    def reorder(self, tasks):
        input_lines = ["%3d %s" % (t.id, t.name) for t in tasks]

        output_lines = self.edit_text("\n".join(input_lines)).split("\n")
        output_lines = filter(bool, output_lines) # remove empty lines
        if not output_lines:
            print "Cancelled reorder."
            return
        i = len(output_lines)
        for j in range(len(output_lines)):
            task_id = int(output_lines[j].lstrip().split(' ')[0])
            self.set_task_active_order(task_id, i-j)
        session.commit()
        print "Reordered active list."

    def execute(self):
        tasks = self.get_active_tasks()
        if len(tasks) == 0:
            self.no_active_tasks()
            return
        self.reorder(tasks)

class PickCommand(Command):
    name = "pick"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.task = self.get_task(int(args[0]))

    def execute(self):
        tasks = self.get_active_tasks()
        self.task.active_order = tasks[0].active_order + 1
        session.commit()
        print "Picked task %d" % self.task.id

class LogCommand(Command):
    name = "log"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.message = self.has_arg('m', 'message', True)
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        if self.message:
            self.task.log(self.message)
            session.commit()
            print "Logged message."
            return

        self.task.show_status_line()
        self.task.show_logs()

class UrlCommand(Command):
    name = "url"

    def __init__(self, args):
        Command.__init__(self)
        self.args = args
        self.url = self.has_arg('a', 'add', True)
        self.message = self.has_arg('m', 'message', True)
        self.task = self.get_named_task()

    def execute(self):
        if not self.task:
            self.no_active_tasks()
            return
        if self.url:
            self.task.add_url(self.url, self.message)
            print "Added URL."
            session.commit()
            return
        if len(self.task.urls) == 0:
            print "No urls."
            return
        for url in self.task.urls:
            url.show()


Commands = [
    ListTasksCommand,
    AddTaskCommand,
    ActivateCommand,
    NotesCommand,
    TomatoCommand,
    DashCommand,
    ShowCommand,
    DoneCommand,
    ReorderCommand,
    PickCommand,
    LogCommand,
    UrlCommand,
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
