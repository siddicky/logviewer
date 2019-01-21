import re
from mistletoe.span_token import SpanToken
from mistletoe import HTMLRenderer


class DiscordMentions(SpanToken):
    ...
    #  pattern =


class DiscordRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__()

    @staticmethod
    def render_line_break(token):
        return '<br />\n'
