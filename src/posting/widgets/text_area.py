from dataclasses import dataclass
from rich.style import Style
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.reactive import reactive, Reactive
from textual.widgets import TextArea, Label, Select, Checkbox
from textual.widgets.text_area import Selection, TextAreaTheme


class ReadOnlyTextArea(TextArea):
    """
    A read-only text area.
    """

    BINDINGS = [
        Binding("up,k", "cursor_up", "Cursor Up", show=False),
        Binding("down,j", "cursor_down", "Cursor Down", show=False),
        Binding("right,l", "cursor_right", "Cursor Right", show=False),
        Binding("left,h", "cursor_left", "Cursor Left", show=False),
        Binding("shift+up,K", "cursor_up(True)", "cursor up select", show=False),
        Binding("shift+down,J", "cursor_down(True)", "cursor down select", show=False),
        Binding("shift+left,H", "cursor_left(True)", "cursor left select", show=False),
        Binding(
            "shift+right,L", "cursor_right(True)", "cursor right select", show=False
        ),
        Binding("ctrl+left,b", "cursor_word_left", "cursor word left", show=False),
        Binding("ctrl+right,w", "cursor_word_right", "cursor word right", show=False),
        Binding(
            "home,ctrl+a,0,^", "cursor_line_start", "cursor line start", show=False
        ),
        Binding("end,ctrl+e,$", "cursor_line_end", "cursor line end", show=False),
        Binding("pageup,ctrl+b", "cursor_page_up", "cursor page up", show=False),
        Binding("pagedown,ctrl+f", "cursor_page_down", "cursor page down", show=False),
        Binding(
            "ctrl+shift+left,B",
            "cursor_word_left(True)",
            "cursor left word select",
            show=False,
        ),
        Binding(
            "ctrl+shift+right,W",
            "cursor_word_right(True)",
            "cursor right word select",
            show=False,
        ),
        Binding("f6,V", "select_line", "select line", show=False),
        Binding(
            "v",
            "toggle_visual_mode",
            description="Select mode",
            key_display="v",
        ),
        Binding(
            "y,c", "copy_to_clipboard", description="Copy selection", key_display="y"
        ),
    ]

    @dataclass
    class VisualModeToggled(Message):
        value: bool
        text_area: TextArea

        @property
        def control(self) -> TextArea:
            return self.text_area

    visual_mode = reactive(False, init=False)

    def on_mount(self):
        self.read_only = True

    def action_toggle_visual_mode(self):
        self.visual_mode = not self.visual_mode

    def watch_visual_mode(self, value: bool) -> None:
        self.cursor_blink = not value
        if not value:
            self.selection = Selection.cursor(self.selection.end)

        self.set_class(value, "visual-mode")
        self.post_message(self.VisualModeToggled(value, self))

    def action_cursor_up(self, select: bool = False) -> None:
        return super().action_cursor_up(self.visual_mode or select)

    def action_cursor_right(self, select: bool = False) -> None:
        return super().action_cursor_right(self.visual_mode or select)

    def action_cursor_down(self, select: bool = False) -> None:
        return super().action_cursor_down(self.visual_mode or select)

    def action_cursor_left(self, select: bool = False) -> None:
        return super().action_cursor_left(self.visual_mode or select)

    def action_cursor_line_end(self, select: bool = False) -> None:
        return super().action_cursor_line_end(self.visual_mode or select)

    def action_cursor_line_start(self, select: bool = False) -> None:
        return super().action_cursor_line_start(self.visual_mode or select)

    def action_cursor_word_left(self, select: bool = False) -> None:
        return super().action_cursor_word_left(self.visual_mode or select)

    def action_cursor_word_right(self, select: bool = False) -> None:
        return super().action_cursor_word_right(self.visual_mode or select)

    def action_copy_to_clipboard(self) -> None:
        text_to_copy = self.selected_text
        if text_to_copy:
            message = f"Copied {len(text_to_copy)} characters."
            self.notify(message, title="Selection copied")
        else:
            text_to_copy = self.text
            message = f"Copied message ({len(text_to_copy)} characters)."
            self.notify(message, title="Message copied")

        import pyperclip

        pyperclip.copy(text_to_copy)
        self.visual_mode = False


POSTLING_THEME = TextAreaTheme(
    name="posting",
    syntax_styles={
        "json.error": Style.parse("u #dc2626"),
        "json.null": Style(color="#7DAF9C"),
        "json.label": Style(color="#569cd6", bold=True),
        "string": Style(color="#ce9178"),
        "string.documentation": Style(color="#ce9178"),
        "comment": Style(color="#6A9955"),
        "keyword": Style(color="#569cd6"),
        "operator": Style(color="#569cd6"),
        "conditional": Style(color="#569cd6"),
        "keyword.function": Style(color="#569cd6"),
        "keyword.return": Style(color="#569cd6"),
        "keyword.operator": Style(color="#569cd6"),
        "repeat": Style(color="#569cd6"),
        "exception": Style(color="#569cd6"),
        "include": Style(color="#569cd6"),
        "number": Style(color="#b5cea8"),
        "float": Style(color="#b5cea8"),
        "class": Style(color="#4EC9B0"),
        "type.class": Style(color="#4EC9B0"),
        "function": Style(color="#4EC9B0"),
        "function.call": Style(color="#4EC9B0"),
        "method": Style(color="#4EC9B0"),
        "method.call": Style(color="#4EC9B0"),
        "boolean": Style(color="#7DAF9C"),
        "constant.builtin": Style(color="#7DAF9C"),
        "tag": Style(color="#EFCB43"),
        "yaml.field": Style(color="#569cd6", bold=True),
        "toml.type": Style(color="#569cd6"),
        "heading": Style(color="#569cd6", bold=True),
        "bold": Style(bold=True),
        "italic": Style(italic=True),
        "strikethrough": Style(strike=True),
        "link": Style(color="#40A6FF", underline=True),
        "inline_code": Style(color="#ce9178"),
        "info_string": Style(color="#ce9178", bold=True, italic=True),
    },
)


class TextAreaFooter(Horizontal):
    """The bar that appears above the response body, allowing
    you to customise the syntax highlighting, wrapping, line numbers,
    etc.
    """

    DEFAULT_CSS = """\
    TextAreaFooter {
        dock: bottom;
        height: 1;
        width: 1fr;
        background: $primary 10%;
        
        &:focus-within {
            background: $primary 55%;
        }

        &:disabled {
            background: transparent;
        }
        
        & Select {
            width: 8;
            margin-right: 1;
            & SelectCurrent {
                width: 8;
            }
            & SelectOverlay {
                width: 16;
            }
        }
        
        & Checkbox {
            margin-right: 1;
        }

        #response-cursor-location-label {
            padding: 0 1;
            color: $text 50%;
        }

        #response-mode-label {
            dock: left;
            padding: 0 1;
            color: $text-muted;
            &.visual-mode {
            }
        }
    }
    """

    language: Reactive[str | None] = reactive("json", init=False)
    soft_wrap: Reactive[bool] = reactive(True, init=False)
    visual_mode: Reactive[bool] = reactive(False, init=False)
    selection: Reactive[Selection] = reactive(Selection.cursor((0, 0)), init=False)

    def watch_selection(self, selection: Selection) -> None:
        row, column = selection.end
        self.cursor_location_label.update(f"{row+1}:{column+1}")

    def watch_visual_mode(self, value: bool) -> None:
        label = self.query_one("#response-mode-label", Label)
        label.set_class(value, "visual-mode")
        label.update("Visual" if value else "")

    def compose(self) -> ComposeResult:
        yield Label("", id="response-mode-label")
        with Horizontal(classes="dock-right w-auto"):
            yield Label("1:1", id="response-cursor-location-label")
            yield Select(
                prompt="Content type",
                value=self.language,
                allow_blank=False,
                options=[("JSON", "json"), ("HTML", "html"), ("Text", None)],
                id="response-content-type-select",
            ).data_bind(value=TextAreaFooter.language)
            yield Checkbox(
                label="Wrap",
                value=self.soft_wrap,
                button_first=False,
                id="response-wrap-checkbox",
            ).data_bind(value=TextAreaFooter.soft_wrap)

    @on(Select.Changed, selector="#response-content-type-select")
    def update_language(self, event: Select.Changed) -> None:
        event.stop()
        self.language = event.value

    @on(Checkbox.Changed, selector="#response-wrap-checkbox")
    def update_soft_wrap(self, event: Checkbox.Changed) -> None:
        event.stop()
        self.soft_wrap = event.value

    @property
    def cursor_location_label(self) -> Label:
        return self.query_one("#response-cursor-location-label", Label)