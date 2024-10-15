from nomad.config.models.plugins import ParserEntryPoint
from pydantic import Field


class VASPParserEntryPoint(ParserEntryPoint):
    parameter: int = Field(0, description='Custom configuration parameter')

    def load(self):
        from nomad.parsing import MatchingParserInterface

        return MatchingParserInterface(
            parser_class_name='nomad_parser_vasp.parsers.parser.VASPParser',
            **self.dict(),
        )


vasp_parser_entry_point = VASPParserEntryPoint(
    name='nomad-parser-vasp',
    python_package='nomad_parser_vasp',
    code_name='VASP',
    code_category='ab initio',
    entry_point_type='parser',
    description='Parser for VASP XML and OUTCAR outputs',
    mainfile_contents_re=(
        r'^\s*<\?xml version="1\.0" encoding="ISO-8859-1"\?>\s*?\s*<modeling>?\s*<generator>?\s*<i '
        r'name="program" type="string">\s*vasp\s*</i>?|^\svasp[\.\d]+.+?(?:\(build|complex)[\s\S]+?executed '
        r'on'
    ),
    mainfile_mime_re='(application/.*)|(text/.*)',
    mainfile_name_re='.*[^/]*xml[^/]*',
    mainfile_alternative=True,
    supported_compressions=['gz', 'bz2', 'xz'],
)
