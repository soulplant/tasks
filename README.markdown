t the task manager
==================

    % t add-task -a "Get the milk."
    > Added task 1.
    % t add-task -a "Something I want to do today."
    > Added task 2.
    % t add-task "Something less important that came up while I was doing something else."
    > Added task 3.

The first two tasks will be added to your active task list (which is intended to be used as the list of tasks you want to do today), the third task is put in your inbox.

    t list-tasks     # prints the tasks in your active list
    t list-tasks -i  # prints the tasks in your inbox
    t list-tasks -a  # prints all tasks

    t X              # indicates that you've put one tomato into the current task (the one at the top of your active list)
    t -              # indicates a cancelled tomato for the current task
    t done           # marks the current task as "done", which removes it from your active list
    t activate 1     # activates task 1 (puts it in your active list)
    t activate -d 1  # deactivates task 1 (puts it in your inbox)
    t reorder        # allows you to reorder your active task list
    t pick 1         # puts task 1 at the top of your active task list
