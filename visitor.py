from antlrgenerated.tlcpParser import tlcpParser
from antlrgenerated.tlcpVisitor import tlcpVisitor
import antlr4
from typing import Optional, List
from functools import reduce
import os


class Config:
    def __init__(self, name: str, path: str, text: str):
        self.name = name
        self.text = text
        self.path = path

    def __add__(self, other: 'Config'):
        return Config(
            self.name + other.name,
            os.path.join(self.path, other.path),
            self.text + other.text)

    def add_name_prefix(self, pref: str, include_in_path: bool) -> 'Config':
        return Config(
            pref + "_" + self.name if self.name else pref,
            os.path.join(pref, self.path) if include_in_path else self.path,
            self.text
        )

    @staticmethod
    def empty_config():
        return Config("", "", "")


# noinspection PyPep8Naming
class TlcpVisitor(tlcpVisitor):
    def __init__(self, basic_name):
        self.basic_name = basic_name
        self.current_family = None
        self.families = []

    def visitWithBuilder(self, node, builders):
        node.tlcBuilders = builders
        node.accept(self)

    def visitConfig(self, ctx: tlcpParser.ConfigContext) -> List[Config]:
        families_commands = get_typed_children(ctx, tlcpParser.FamiliesContext)

        if not families_commands:
            return self.visitConfigWithFamily(ctx, family=None)

        assert(len(families_commands) == 1)
        families_cmd = families_commands[0]
        self.families = [family.getText()
                         for family in get_typed_children(families_cmd, tlcpParser.FamilyNameContext)]

        for family in self.families:
            if "_" in family:
                raise RuntimeError("Family name '{}' contains prohibited symbol '_'.".format(family))

        return sum((self.visitConfigWithFamily(ctx, family) for family in self.families), start=[])

    def visitConfigWithFamily(self, ctx: tlcpParser.ConfigContext, family: Optional[str]) -> List[Config]:
        self.current_family = family
        block = get_typed_child(ctx, tlcpParser.BlockContext)
        name_prefix = self.basic_name + "_" + family if family else self.basic_name
        return [conf.add_name_prefix(name_prefix, include_in_path=True)
                for conf in self.visit(block)]

    def visitBlock(self, ctx: tlcpParser.BlockContext):
        return reduce(lambda agg, child: [prefix + suffix for prefix in agg for suffix in self.visit(child)],
                      ctx.getChildren(),
                      [Config.empty_config()])

    def visitFamilyStatement(self, ctx: tlcpParser.FamilyStatementContext) -> List[Config]:
        statement_families = self.get_family_statement_families(ctx)
        for family in statement_families:
            if family not in self.families:
                raise RuntimeError("Unknown family '{}'".format(family))

        if self.families and self.current_family not in statement_families:
            return [Config.empty_config()]
        return self.visit(get_typed_child(ctx, tlcpParser.StatementContext))

    def visitBlockWIthBeginEnd(self, ctx: tlcpParser.BlockWIthBeginEndContext):
        return self.visit(get_typed_child(ctx, tlcpParser.BlockContext))

    def visitOneOf(self, ctx: tlcpParser.OneOfContext) -> List[Config]:
        options = get_typed_children(ctx, tlcpParser.OptionContext)
        with_subfolders = bool(get_token_children(ctx, tlcpParser.ONE_OF_WITH_SUBFOLDERS))
        for option in options:
            # We use this little hack to pass information down the tree.
            option.tlcp_with_subfolders = with_subfolders
        return sum((self.visit(option) for option in options), start=[])

    def visitOption(self, ctx: tlcpParser.OptionContext) -> List[Config]:
        name = get_typed_child(ctx, tlcpParser.OptionNameContext).getText()
        if "_" in name:
            raise RuntimeError("Option name '{}' contains prohibited symbol '_'.".format(name))
        block = get_typed_child(ctx, tlcpParser.BlockContext)

        # We use the ability of python to create fields on the fly to pass information down the tree.
        # noinspection PyUnresolvedReferences
        return [conf.add_name_prefix(name, include_in_path=ctx.tlcp_with_subfolders)
                for conf in self.visit(block)]

    def visitTlcStatement(self, ctx: tlcpParser.TlcStatementContext) -> List[Config]:
        # just returns the text used for the original TLC statement
        assert ctx.start.getInputStream() is ctx.stop.getInputStream()
        input_stream = ctx.start.getInputStream()
        text = input_stream.getText(ctx.start.start, ctx.stop.stop) + "\n"
        return [Config("", "", text)]

    def get_family_statement_families(self, statement: tlcpParser.FamilyStatementContext):
        statement_families = [
            family_ctx.getText()
            for family_ctx in get_typed_children(statement, tlcpParser.FamilyNameContext)]

        # statements without families explicitly specified apply to all families
        if not statement_families:
            statement_families = self.families

        return statement_families

    def visitTerminal(self, node):
        raise AssertionError("Unreachable state: some statement was not processed.")


# Returns a list of objects of type tp.
def get_typed_children(ctx: antlr4.ParserRuleContext, tp: type) -> list:
    return [child for child in ctx.getChildren() if isinstance(child, tp)]


# Return an object of type tp.
def get_typed_child(ctx: antlr4.ParserRuleContext, tp: type):
    lst = get_typed_children(ctx, tp)
    if not lst:
        raise AssertionError("Object has no children of type '{}'.".format(tp))
    if len(lst) > 1:
        raise AssertionError("Object has multiple children of type '{}'.".format(tp))
    return lst[0]


def get_token_children(ctx: antlr4.ParserRuleContext, token_tp: int) -> List[antlr4.Token]:
    # noinspection PyUnresolvedReferences
    return [child
            for child in ctx.getChildren()
            if isinstance(child, antlr4.TerminalNode) and child.getSymbol().type == token_tp]


def get_token_child(ctx: antlr4.ParserRuleContext, token_tp: int) -> antlr4.Token:
    lst = get_token_children(ctx, token_tp)
    if not lst:
        raise AssertionError("Object has no token children of type '{}'.".format(token_tp))
    if len(lst) > 1:
        raise AssertionError("Object has multiple token children of type '{}'.".format(token_tp))
    return lst[0]
