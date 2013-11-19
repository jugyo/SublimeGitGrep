import sublime, sublime_plugin
import subprocess, os

class GitGrepCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('git grep', '', self.git_grep, None, None)

    def git_grep(self, query):
        items = []

        try:
            base_dir = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'])
            base_dir = base_dir.decode('utf8', 'ignore').strip()
            os.chdir(base_dir)
            matches = subprocess.check_output(['git', 'grep', query]).strip()
            matches = matches.decode('utf8', 'ignore').split("\n")
            for m in matches:
                file_name, line, match = m.split(":", 2)
                items.append([match.strip(), ":".join([file_name, line])])
        except subprocess.CalledProcessError as e:
            print(e)

        if len(items) == 0:
            self.window.show_quick_panel(['No result'], None)
        else:
            def on_done(index):
                if index < 0:
                    return
                line = matches[index]
                file_name, line_no, match = line.split(":", 2)
                file_name = os.path.join(base_dir, file_name)
                view = self.window.open_file(file_name + ':' + line_no, sublime.ENCODED_POSITION)
                point = view.text_point(int(line_no) - 1 ,0)
                regison = view.line(point)
                view.show_at_center(regison)
            self.window.show_quick_panel(items, on_done)
