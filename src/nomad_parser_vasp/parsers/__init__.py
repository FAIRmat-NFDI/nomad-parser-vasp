from pydantic import Field
from nomad.config.models.plugins import ParserEntryPoint


class VasprunXMLEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad.parsing import MatchingParserInterface

        return MatchingParserInterface(
            parser_class_name='nomad_parser_vasp.parsers.xml_parser.VasprunXMLParser',
            **self.dict(),
        )


xml_entry_point = VasprunXMLEntryPoint(
    name='nomad-parser-vasp',
    python_package='nomad_parser_vasp',
    code_name='VASP XML',
    code_category='ab initio',
    entry_point_type='parser',
    description='Parser for VASP output in XML format.',
    mainfile_name_re='.*vasprun\.xml.*',
)
