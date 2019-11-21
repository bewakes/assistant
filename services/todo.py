import os
import sys
import json
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.socket_mixin import SocketHandlerMixin  # noqa
from utils.terminal_formatter import Style  # noqa
from utils import log  # noqa

logger = log.get_logger('Notes')

STATUS_NOT_DONE = '[ ]'
STATUS_DONE = '[X]'
STATUS_POSTPONED = '[-]'  # This might not be used


def sort_status_key(k_item):
    k, item = k_item
    if item['status'] == STATUS_NOT_DONE:
        return -1
    return 0


class TodoService(SocketHandlerMixin):
    """
    Service to store todos
    """
    def __init__(self):
        dirname = os.path.expanduser('~/.assistant')
        self.data_path = os.path.join(dirname, 'todo.json')
        self.data = self._read_data()

    def _read_data(self):
        try:
            with open(self.data_path) as f:
                data = json.load(f)
                return data
        except FileNotFoundError:
            return {'count': 0, 'todos': {}}
        except json.decoder.JSONDecodeError:
            logger.error('Invalid json')
            return None

    def _write_data(self):
        with open(self.data_path, 'w') as f:
            json.dump(self.data, f, indent=4)

    def handle_add(self, args):
        if not args:
            return Style.red('Usage: todo add <your todo>')
        todo_text = ' '.join(args)
        hashed = hashlib.md5(todo_text.encode('utf-8'))
        id = hashed.hexdigest()[:4]
        if self.data['todos'].get(id):
            return Style.yellow('The todo is already added.')
        self.data['count'] += 1
        self.data['todos'][id] = {
            'item': todo_text,
            'status': STATUS_NOT_DONE,
        }
        # Save to file
        self._write_data()
        return Style.green(f'\nTodo "{todo_text}" added with id "{id}"\n') + \
            self.todo_summary

    def handle_check(self, args):
        if not args:
            return Style.red('Usage todo check <todo id>')
        id = args[0]
        todo = self.data['todos'].get(id)
        if not todo:
            return Style.red(f'Todo item with id "{id}" does not exist')
        if todo['status'] == STATUS_DONE:
            return Style.yellow('The todo item is already checked!!')
        elif todo['status'] == STATUS_NOT_DONE:
            self.data['count'] -= 1
            self.data['todos'][id]['status'] = STATUS_DONE
            self._write_data()
            return Style.green(f'\nTodo "{id}" checked out!!\n') + self.todo_summary

    def handle_uncheck(self, args):
        if not args:
            return Style.red('Usage todo uncheck <todo id>')
        id = args[0]
        todo = self.data['todos'].get(id)
        if not id:
            return Style.red(f'Todo item with id {id} does not exist')
        if todo['status'] == STATUS_DONE:
            self.data['count'] += 1
            self.data['todos'][id]['status'] = STATUS_NOT_DONE
            self._write_data()
            return Style.green(f'\nTodo "{id}" unchecked!!\n') + self.todo_summary
        elif todo['status'] == STATUS_NOT_DONE:
            return Style.yellow(f'Todo "{id}" is already unchecked!!')

    @property
    def todo_summary(self):
        total = len(self.data['todos'].keys())
        checked = len([k for k, v in self.data['todos'].items() if v['status'] == STATUS_DONE])
        return Style.bold(
            f'Total Todos: {total}   '
            f'Checked Todos: {checked}   '
            f'Unchecked Todos: {total-checked}   '
        )

    def handle_list(self, args):
        result = '\n'
        if not self.data['todos']:
            return Style.yellow('Congrats!! You do not have any todos')
        checked_count = 0
        unchecked_count = 0
        sorted_by_status = sorted(self.data['todos'].items(), key=sort_status_key, reverse=True)
        for k, v in sorted_by_status:
            if v['status'] == STATUS_DONE:
                checked_count += 1
                result += Style.magenta(f'{k}: {v["status"]} {v["item"]}\n')
            else:
                unchecked_count += 1
                result += Style.yellow(f'{k}: {v["status"]} {v["item"]}\n')
        return result + self.todo_summary

    def handle_clean(self, args):
        """This removes archived todos"""
        old_count = len(self.data['todos'].keys())
        new_todos = {
            k: v
            for k, v in self.data['todos'].items()
            if v['status'] != STATUS_DONE
        }
        new_count = len(new_todos.keys())
        self.data['todos'] = new_todos
        self._write_data()
        return Style.green(f'\nDeleted {old_count - new_count} checked todos.\n') + \
            self.todo_summary


if __name__ == '__main__':
    t = TodoService()
    port = sys.argv[1]
    try:
        t.initialize_and_run(port)
    except SystemExit:
        pass
    except Exception:
        import traceback
        logger.error(traceback.format_exc())
