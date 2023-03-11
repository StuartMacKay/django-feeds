import json

from pygments import highlight  # type: ignore
from pygments.formatters.html import HtmlFormatter  # type: ignore
from pygments.lexers.data import JsonLexer  # type: ignore

__all__ = [
    "prettify",
]


class PrettyEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(PrettyEncoder, self).__init__(*args, **kwargs)
        self.current_indent = 0
        self.current_indent_str = ""

    def encode(self, o):
        # Special Processing for lists
        if isinstance(o, (list, tuple)):
            primitives_only = True
            for item in o:
                if isinstance(item, (list, tuple, dict)):
                    primitives_only = False
                    break
            output = []
            if primitives_only:
                for item in o:
                    output.append(json.dumps(item))
                return "[ " + ", ".join(output) + " ]"
            else:
                self.current_indent += self.indent
                self.current_indent_str = "".join(
                    [" " for x in range(self.current_indent)]
                )
                for item in o:
                    output.append(self.current_indent_str + self.encode(item))
                self.current_indent -= self.indent
                self.current_indent_str = " " * self.current_indent
                return "[\n" + ",\n".join(output) + "\n" + self.current_indent_str + "]"
        elif isinstance(o, dict):
            output = []
            self.current_indent += self.indent
            self.current_indent_str = " " * self.current_indent
            items = sorted(o.items()) if self.sort_keys else o.items()
            for key, value in items:
                output.append(
                    self.current_indent_str
                    + json.dumps(key)
                    + ": "
                    + self.encode(value)
                )
            self.current_indent -= self.indent
            self.current_indent_str = " " * self.current_indent
            return "{\n" + ",\n".join(output) + "\n" + self.current_indent_str + "}"
        else:
            return json.dumps(o)


def prettify(data):
    response = json.dumps(data, sort_keys=True, indent=4, cls=PrettyEncoder)
    formatter = HtmlFormatter(style="colorful")
    response = highlight(response, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return style + response
