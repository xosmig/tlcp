from antlrgenerated.tlcpParser import tlcpParser
from antlrgenerated.tlcpVisitor import tlcpVisitor
import antlr4
from io import StringIO
from copy import deepcopy
from typing import Optional, Iterator, List, Tuple
from functools import reduce


class Config:
    def __init__(self, name: str, text: str, family: str):
        self.name = name
        self.text = text
        self.family = family

    def __add__(self, other: 'Config'):
        assert self.family == other.family
        return Config(self.name + other.name, self.text + other.text, self.family)

    def add_name_prefix(self, pref) -> 'Config':
        if self.name != "":
            pref = pref + "_"
        return Config(pref + self.name, self.text, self.family)

    @staticmethod
    def empty_config(family):
        return Config("", "", family)


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

        if len(families_commands) > 1:
            raise RuntimeError("Multiple #FAMILIES(...) statements are not allowed.")

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
        return [conf.add_name_prefix(name_prefix) for conf in self.visit(block)]

    def visitBlock(self, ctx: tlcpParser.BlockContext):
        return reduce(lambda agg, child: [prefix + suffix for prefix in agg for suffix in self.visit(child)],
                      ctx.getChildren(),
                      [Config.empty_config(self.current_family)])

    def visitFamilyStatement(self, ctx: tlcpParser.FamilyStatementContext) -> List[Config]:
        if self.families and self.current_family not in self.get_family_statement_families(ctx):
            return [Config.empty_config(self.current_family)]
        return self.visit(get_typed_child(ctx, tlcpParser.StatementContext))

    def visitOneOf(self, ctx: tlcpParser.OneOfContext) -> List[Config]:
        options = get_typed_children(ctx, tlcpParser.OptionContext)
        return sum((self.visit(option) for option in options), start=[])

    def visitOption(self, ctx: tlcpParser.OptionContext) -> List[Config]:
        name = get_typed_child(ctx, tlcpParser.OptionNameContext).getText()
        if "_" in name:
            raise RuntimeError("Option name '{}' contains prohibited symbol '_'.".format(name))
        block = get_typed_child(ctx, tlcpParser.BlockContext)
        return [conf.add_name_prefix(name) for conf in self.visit(block)]

    def visitTlcStatement(self, ctx: tlcpParser.TlcStatementContext) -> List[Config]:
        # just returns the text used for the original TLC statement
        assert ctx.start.getInputStream() is ctx.stop.getInputStream()
        input_stream = ctx.start.getInputStream()
        text = input_stream.getText(ctx.start.start, ctx.stop.stop) + "\n"
        return [Config("", text, self.current_family)]

    def get_family_statement_families(self, statement: tlcpParser.FamilyStatementContext):
        families = [family.getText()
                    for family in get_typed_children(statement, tlcpParser.FamilyNameContext)]
        for family in families:
            if family not in self.families:
                raise RuntimeError("Unknown family '{}'".format(family))

        # statements without families explicitly specified apply to all families
        if not families:
            families = self.families

        return families

    def visitTerminal(self, node):
        raise AssertionError("Unreachable state: some statement was not processed.")


# Returns a list of objects of type tp.
def get_typed_children(ctx: antlr4.ParserRuleContext, tp: type) -> list:
    return [child for child in ctx.getChildren() if isinstance(child, tp)]


# Return an object of type tp.
def get_typed_child(ctx: antlr4.ParserRuleContext, tp: type):
    lst = get_typed_children(ctx, tp)
    if not lst:
        raise AssertionError("Object has no children of type {}.".format(tp))
    if len(lst) > 1:
        raise AssertionError("Object has multiple children of type {}.".format(tp))
    return lst[0]
