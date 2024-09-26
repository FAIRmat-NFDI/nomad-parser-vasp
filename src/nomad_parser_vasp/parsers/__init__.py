from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class SimulationParserEntryPoint(ParserEntryPoint):
    parser_class_name: str = Field(
        description="""
        The fully qualified name of the Python class that implements the parser.
        This class must have a function `def parse(self, mainfile, archive, logger)`.
    """
    )
    level: int = Field(
        0,
        description="""
        Order of execution of parser with respect to other parsers.
    """,
    )

    def load(self):
        from nomad.parsing import MatchingParserInterface

        return MatchingParserInterface(**self.dict())


parser_entry_point = SimulationParserEntryPoint(
    name='parsers/vasp',
    aliases=['parsers/vasp'],
    description='Entry point for the VASP parser.',
    python_package='nomad_parser_vasp.parsers',
    parser_class_name='nomad_parser_vasp.parsers.parser.VASPParser',
    level=0,
    supported_compressions=['gz', 'bz2', 'xz'],
    mainfile_mime_re='(application/.*)|(text/.*)',
    mainfile_name_re='.*[^/]*xml[^/]*',
    mainfile_contents_re=(
        r'^\s*<\?xml version="1\.0" encoding="ISO-8859-1"\?>\s*?\s*<modeling>?\s*<generator>?\s*<i '
        r'name="program" type="string">\s*vasp\s*</i>?|^\svasp[\.\d]+.+?(?:\(build|complex)[\s\S]+?executed '
        r'on'
    ),
    # mainfile_alternative=True,
)
