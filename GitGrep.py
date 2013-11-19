import sublime, sublime_plugin
import subprocess, os

class GitGrepCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('git grep', '', self.git_grep, None, None)

    def git_grep(self, query):
        items = []

        try:
            base_dir = self.window.folders()[0]
            os.chdir(base_dir)
            matches = subprocess.check_output(['git', 'grep', query]).strip()
            matches = matches.decode('utf8', 'ignore').split("\n")
            for m in matches:
                try:
                    file_name, line, match = m.split(":", 2)
                    items.append([match.strip()[0:20], ":".join([file_name, line])])
                except ValueError as e:
                    print(e)
        except subprocess.CalledProcessError as e:
            print(e)

        if len(items) == 0:
            self.window.show_quick_panel(['No result'], None)
        else:
            def open_for(line, mode):
                file_name, line_no, match = line.split(":", 2)
                file_name = os.path.join(base_dir, file_name)
                view = self.window.open_file(file_name, mode)
                point = view.text_point(int(line_no) - 1 ,0)
                regison = view.line(point)
                view.show_at_center(regison)

            def on_done(index):
                if index >= 0:
                    open_for(matches[index], sublime.ENCODED_POSITION)
                else:
                    view = self.window.active_view()
                    (_, tab_index) = view.window().get_view_index(view)
                    if tab_index < 0:
                        view.close()

            def on_highlight(index):
                if index >= 0:
                    open_for(matches[index], sublime.TRANSIENT)

            self.window.show_quick_panel(items, on_done, sublime.MONOSPACE_FONT, -1, on_highlight)
