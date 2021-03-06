#------------------------------------------
# Name:     menu
# Purpose:  Menu interface (with GUI) for creating/managing tasks.
#
# Author:   Robin Siebler
# Created:  7/28/14
#------------------------------------------
__author__ = 'Robin Siebler'
__date__ = '7/28/14'

import util
from tasklist import Task, TaskList
from collections import OrderedDict
import sys
import ui
import help

class Menu:

    def __init__(self):
        """Initialize the task list and populate the dictionary for menu actions."""

        self.tasklist = TaskList()
        self.current_task = ''
        self.current_task_file = ''
        self.main_view = ''
        self.controls_enabled = False

    def display_message(self, message):
        self.message_dialog = ui.load_view('dialogs/message')
        self.message_dialog['label1'].text = message
        self.message_dialog.present('popover', popover_location = (500,500))
		
    def show_tasks(self, sender, tasks=None):
        """Display the tasks (in ID order)

        :param tasks: tasks object
        """
        
        if not tasks:
            tasks = self.tasklist.tasks
        tv_text = ""
        if len(tasks) > 0:
            if not self.controls_enabled:
                #enable controls if there are tasks loaded
                self.main_view['button_number'].enabled = True
                self.main_view['button_priority'].enabled = True
                self.main_view['button_save'].enabled = True
                self.main_view['button_delete_task'].enabled = True
                self.main_view['button_modify'].enabled = True
                self.main_view['button_search'].enabled = True
                self.controls_enabled = True
            for task in tasks:
                tv_text += '{}: {}\n\tPriority: {}\n\tTags: {}\n'.format(task.id, task.note, task.priority, task.tags)
        else:
            tv_text = '\nThere are no tasks to display!\n'
        
        self.task_textview.text = tv_text

    def show_tasks_by_priority(self, sender, tasks=None):
        """Display the tasks (in Priority order)

        :param tasks: tasks object
        """
        low_dict = OrderedDict()
        med_dict = OrderedDict()
        high_dict = OrderedDict()

        if not tasks:
            tasks = self.tasklist.tasks
        tv_text = ''

        if len(tasks) > 0:
            for task in tasks:
                if task.priority == 'Low':
                    low_dict[task.id] = [task.note, task.priority, task.tags]
                if task.priority == 'Medium':
                    med_dict[task.id] = [task.note, task.priority, task.tags]
                if task.priority == 'High':
                    high_dict[task.id] = [task.note, task.priority, task.tags]
        else:
            tv_text += '\nThere are no tasks to display!\n'
            return

        tv_text += 'High\n' + '-' * 20 + '\n'
        if len(high_dict) > 0:
            for key in high_dict:
                tv_text += '{}: {}\n\tTags: {}\n'.format(key, high_dict[key][0], high_dict[key][2])
        else:
            tv_text += 'There are no high priority tasks\n'

        tv_text += '\nMedium\n' + '-' * 20 + '\n'
        if len(med_dict) > 0:
            for key in med_dict:
                tv_text += '{}: {}\n\tTags: {}\n'.format(key, med_dict[key][0], med_dict[key][2])
        else:
            tv_text += 'There are no medium priority tasks\n'

        tv_text+= '\nLow\n' + '-' * 20 + '\n'
        if len(low_dict) > 0:
            for key in low_dict:
                tv_text += '{}: {}\n\tTags: {}\n'.format(key, low_dict[key][0], low_dict[key][2])
        else:
            tv_text += 'There are no low priority tasks\n'

        self.task_textview.text = tv_text

    def prompt_search(self, sender):
    	"""Prompt the user for a search string."""
    	
        self.search_dialog = ui.load_view('dialogs/search_tasks')
        self.search_dialog.present('sheet')

    def search_tasks(self, sender):
        """Search the task list for a task whose note or tag contains the user provided search string."""

        search_string = self.search_dialog['textfield1'].text.lower()
        tasks = self.tasklist.search(search_string)
        if tasks:
            self.search_dialog.close()
            self.show_tasks(sender,tasks=tasks)
        else:
            #self.search_dialog.close()
            message = 'There were no tasks containing "{}".'.format(search_string)
            self.display_message(message)
            
    def prompt_add(self, sender):
    	"""Prompt the user to add a task."""
    	
    	self.add_dialog = ui.load_view('dialogs/add_task')
        self.add_dialog.present('sheet')

    def add_task(self, sender):
        """Add a new task."""

        note = self.add_dialog['textfield_task'].text
        priority_num = self.add_dialog['segmentedcontrol1'].selected_index
        if priority_num == 0:
        	priority = 'Low'
        elif priority_num == 1:
        	priority = 'Medium'
        elif priority_num == 2:
        	priority = 'High'
        tags = self.add_dialog['textfield_tags'].text
        self.tasklist.add_task(note, priority, tags)
        self.add_dialog.close()
        self.show_tasks(None)

    def prompt_delete_file(self, sender):
    	"""Prompt the user to delete a task file."""
    	
    	self.delete_dialog = ui.load_view('dialogs/delete_task_file')
        self.delete_dialog.present('sheet')

    def delete_file(self, sender):
    	"""Delete a task file."""
        task_file = self.delete_dialog['textfield1'].text
        if not task_file == '':
        	task_file = util.validate_file(task_file)
        if task_file:
        	self.delete_dialog.close()
        	util.delete(task_file)
        else:
        	self.display_message(self.delete_dialog['textfield1'].text + ' is not a valid file!')
        	self.delete_dialog['textfield1'].text = ''

    def prompt_delete_task(self, sender):
    	"""Prompt the user to delete a task."""
    	
    	self.delete_dialog = ui.load_view('dialogs/delete_task')
        self.delete_dialog.present('popover', popover_location = (500,500))

    def delete_task(self, sendr):
        """Delete a task."""
        task_id = self.delete_dialog['textfield1'].text
        task_id = self._validate_task_id(task_id)
        if task_id:
            self.delete_dialog.close()
            self.tasklist.delete_task(task_id)
            self.tasklist._renumber_tasks()
            #Task.last_id -= 1
            self.show_tasks(None)
        else:
            self.delete_dialog['textfield1'].text = ''
            
    def prompt_modify_task_number(self, sender):
    	"""Prompt the user for the number of the task modify."""
    	
    	self.modify_dialog = ui.load_view('dialogs/modify_task_number')
        self.modify_dialog.present('popover', popover_location = (500,500))

    def modify_task(self, sender):
        """Change the fields of a task."""

        task_id = self._validate_task_id(self.modify_dialog['textfield1'].text)
        if task_id:
            self.current_task = self.tasklist._find_task(task_id)
            self.modify_dialog.close()
            self.modify_dialog = ui.load_view('dialogs/modify_task')
            self.modify_dialog['textfield_task'].text = self.current_task.note
            if self.current_task.priority == 'Low':
                self.modify_dialog['segmentedcontrol1'].selected_index = 0
            if self.current_task.priority == 'Medium':
                self.modify_dialog['segmentedcontrol1'].selected_index = 1
            if self.current_task.priority == 'High':
                self.modify_dialog['segmentedcontrol1'].selected_index = 2
            self.modify_dialog['textfield_tags'].text = self.current_task.tags
            self.modify_dialog.present('sheet')

    def save_modified_task(self, sender):
        """Save the contents of the modified task."""
        	
        self.current_task.note = self.modify_dialog['textfield_task'].text
        priority_num = self.modify_dialog['segmentedcontrol1'].selected_index
        if priority_num == 0:
        	self.current_task.priority = 'Low'
        elif priority_num == 1:
        	self.current_task.priority = 'Medium'
        elif priority_num == 2:
        	self.current_task.priority = 'High'
        self.current_task.tags = self.modify_dialog['textfield_tags'].text
        self.modify_dialog.close()
        self.show_tasks(None)
                
    def prompt_load(self, sender):
    	"""Prompt the user for the name of a task file."""
    	
        self.load_dialog = ui.load_view('dialogs/load_task_file')
        self.load_dialog.present('sheet')

    def load_tasks(self, sender):
        """Retrieve the contents of the task file."""

        task_file = self.load_dialog['textfield1'].text
        if not task_file == '':
        	task_file = util.validate_file(task_file)
        if task_file:
        	self.load_dialog.close()
	        self.tasklist.tasks = util.load(task_file)
	        self.current_task_file = task_file
	        Task.last_id = len(self.tasklist.tasks)
	        self.show_tasks(None)
        else:
        	self.display_message(self.load_dialog['textfield1'].text + ' is not a valid file')
        	self.load_dialog['textfield1'].text = ''

    def prompt_save(self, sender):
    	"""Prompt the user for the name of a task file."""
    	
        self.save_dialog = ui.load_view('dialogs/save_task_file')
        self.save_dialog.present('sheet')

    def save_tasks(self, sender):
		"""Save the tasks to the specified file."""
		
		task_file = self.save_dialog['textfield1'].text
		if not task_file == '':
			if task_file.rfind('.tsk', len(task_file) -4) == -1:
				task_file += '.tsk'
			self.save_dialog.close()
			if task_file == self.current_task_file:
				# some bug; even though the file should be closed, I can't overwrite 
				util.delete(task_file)
			util.save(self.tasklist.tasks, task_file)
		else:
			self.save_dialog['textfield1'].text = ''

    def _validate_task_id(self, task_id):
        """Validate the given task ID.

        :return: False if an invalid ID was provided, otherwise a string containing the valid task id.
        """

        if task_id.isdecimal() and int(task_id) <= len(self.tasklist.tasks):
            return task_id
        else:
            self.display_message('{} is not an existing task!'.format(task_id))
            return None

    def run(self):
        main_view = ui.load_view("menu")
    	# turn off invalid controls
    	main_view['button_number'].enabled = False
    	main_view['button_priority'].enabled = False
    	main_view['button_save'].enabled = False
    	main_view['button_delete_task'].enabled = False
    	main_view['button_modify'].enabled = False
    	main_view['button_search'].enabled = False
        main_view.present("sheet")
        self.main_view = main_view
        self.task_textview = main_view['task_textview']
    	self.task_textview.text = help.help_text


if __name__ == '__main__':
    Menu().run()
