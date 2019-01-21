import re
import html
from mistletoe.span_token import SpanToken, remove_token as remove_token_span
from mistletoe import HTMLRenderer
from mistletoe.block_token import remove_token as remove_token_block
from mistletoe.block_token import *
from mistletoe.span_token import *
from mistletoe.block_token import _token_types
from mistletoe.span_token import _token_types as _token_types_span


class DiscordMentions(SpanToken):
    precedence = 6
    parse_inner = False
    pattern = re.compile(r'(&lt;(?:@!?|#)\d+&gt;|@(?:everyone|here))')

    def __init__(self, match_obj):
        self.target = match_obj.group(1)


class DiscordRenderer(HTMLRenderer):
    def __init__(self):
        super().__init__(DiscordMentions)

    def __enter__(self):
        print(_token_types, _token_types_span)
        remove_token_block(Table)
        remove_token_block(List)
        remove_token_block(Quote)
        remove_token_block(Heading)
        remove_token_block(Footnote)
        remove_token_span(AutoLink)
        return self

    @staticmethod
    def render_line_break(token):
        return '<br />\n'

    def render_inline_code(self, token):
        template = '<code class="pre--inline">{}</code>'
        inner = html.escape(token.children[0].content)
        return template.format(inner)

    # TODO: change
    def render_block_code(self, token):
        template = '<pre class="pre--multiline"><code{attr}>{inner}</code></pre>'
        if token.language:
            attr = ' class="{}"'.format('language-{}'.format(self.escape_html(token.language)))
        else:
            attr = ''
        inner = html.escape(token.children[0].content)
        return template.format(attr=attr, inner=inner)

    def render_paragraph(self, token):
        return self.render_inner(token)

    def render_discord_mentions(self, token):
        template = '<span class="mention">{}</span>'
        return template.format(token.target)
