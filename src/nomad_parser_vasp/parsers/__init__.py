from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class VasprunXMLEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad_parser_vasp.parsers.xml_parser import VasprunXMLParser

        return VasprunXMLParser(**self.dict())


xml_entry_point = VasprunXMLEntryPoint(
    name='VasprunXML Parser',
    description='Parser for VASP output in XML format.',
    mainfile_name_re='.*vasprun\.xml.*',
)
