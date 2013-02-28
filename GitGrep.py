import sublime, sublime_plugin
import commands, os

class GitGrepCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('git grep', '', self.git_grep, None, None)

    def git_grep(self, query):
        status, base_dir = commands.getstatusoutput('git rev-parse --show-toplevel')
        if status != 0:
            sublime.message_dialog(base_dir)
            return
        os.chdir(base_dir)

        status, matches = commands.getstatusoutput('git grep "%s"' % query)
        if status != 0:
            sublime.message_dialog(matches)
            return

        matches = matches.decode('utf8', 'ignore').split("\n")

        def split(l):
            file_name, line, match = l.split(":", 2)
            return [match.strip(), ":".join([file_name, line])]

        items = map(split, matches)

        def on_done(index):
            if index < 0:
                return

            line = matches[index]
            file_name, line_no, match = line.split(":", 2)
            file_name = os.path.join(base_dir, file_name)
            self.window.open_file(file_name + ':' + line_no, sublime.ENCODED_POSITION)

        self.window.show_quick_panel(items, on_done)
