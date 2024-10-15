from typing import TYPE_CHECKING, Dict, List, Any

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

import numpy as np
import re

from nomad.datamodel import EntryArchive
from nomad.parsing.file_parser import TextParser, Quantity
from nomad.parsing.file_parser.mapping_parser import (
    MetainfoParser,
    TextParser as MappingTextParser,
    Path,
)

from nomad_parser_vasp.schema_packages.vasp_package import Simulation


RE_N = r'[\n\r]'


def get_key_values(val_in):
    val = [v for v in val_in.split('\n') if '=' in v]
    data = {}
    pattern = re.compile(r'([A-Z_]+)\s*=\s*(\.?[a-zA-Z]*[\d\-\.\+\sE]*\.?)')

    def convert(v):
        if isinstance(v, list):
            v = [convert(vi) for vi in v]
        elif isinstance(v, str):
            try:
                v = float(v) if '.' in v else int(v)
            except Exception:
                pass
        else:
            pass
        return v

    for v in val:
        res = pattern.findall(v)
        for resi in res:
            vi = resi[1].split()
            vi = vi[0] if len(vi) == 1 else vi
            if isinstance(vi, str):
                vi = vi.strip()
                vi_upper = vi.upper()
                if vi_upper in ['T', '.TRUE.', 'TRUE']:
                    vi = True
                elif vi_upper in ['F', '.FALSE.', 'FALSE']:
                    vi = False
            data[resi[0]] = convert(vi)
    return data


class OutcarTextParser(TextParser):
    def __init__(self):
        self._chemical_symbols = None

        super().__init__(None)

    def init_quantities(self):
        def str_to_array(val_in):
            val = [
                re.findall(r'(\-?\d+\.[\dEe]+)', v)
                for v in val_in.strip().split('\n')
                if '--' not in v
            ]
            return [
                np.array([v[0:3] for v in val], float),
                np.array([v[3:6] for v in val], float),
            ]

        def str_to_stress(val_in):
            val = [float(v) for v in val_in.strip().split()]
            stress = np.zeros((3, 3))
            stress[0][0] = val[0]
            stress[1][1] = val[1]
            stress[2][2] = val[2]
            stress[0][1] = stress[1][0] = val[3]
            stress[1][2] = stress[2][1] = val[4]
            stress[0][2] = stress[2][0] = val[5]
            return stress

        def str_to_header(val_in):
            (
                version,
                build_date,
                build_type,
                platform,
                date,
                time,
                parallel,
            ) = val_in.split()
            parallel = 'parallel' if parallel == 'running' else parallel
            subversion = '%s %s %s' % (build_date, build_type, parallel)
            date = date.replace('.', ' ')
            return dict(
                version=version,
                subversion=subversion,
                platform=platform,
                date=date,
                time=time,
            )

        def str_to_positions(val_in):
            re_position = re.compile(
                r'\d*\s*(\-*\d+\.\d+)\s*(\-*\d+\.\d+)\s*(\-*\d+\.\d+)'
            )
            positions = []
            for val in val_in.strip().split('\n'):
                position = re_position.search(val)
                if position:
                    positions.append(position.groups())
            return np.array(positions, dtype=float)

        def str_to_eigenvalues(val_in):
            val = []
            for line in val_in.strip().splitlines():
                val.extend(['nan' if '*' in v else v for v in line.split()])
            return np.array(val, np.float64)

        scf_iteration = [
            Quantity(
                'energy_total',
                r'free energy\s*TOTEN\s*=\s*([\d\.\-]+)\s*eV',
                repeats=False,
                dtype=float,
            ),
            Quantity(
                'energy_entropy0',
                r'energy without entropy\s*=\s*([\d\.\-]+)',
                repeats=False,
                dtype=float,
            ),
            Quantity(
                'energy_T0',
                r'energy\(sigma\->0\)\s*=\s*([\d\.\-]+)',
                repeats=False,
                dtype=float,
            ),
            Quantity(
                'energy_components',
                r'Free energy of the ion-electron system \(eV\)\s*\-+([\s\S]+?)\-{10}',
                str_operation=get_key_values,
                convert=False,
            ),
            Quantity(
                'time',
                r'LOOP\: +cpu time +([\d\.]+)\: +real time +([\d\.]+)',
                dtype=np.dtype(np.float64),
            ),
        ]

        calculation_quantities = [
            Quantity(
                'scf_iteration',
                r'Iteration\s*\d+\(\s*\d+\s*\)([\s\S]+?energy\(sigma\->0\)\s*=\s*.+)',
                repeats=True,
                sub_parser=TextParser(quantities=scf_iteration),
            ),
            Quantity(
                'energies',
                r'FREE ENERGIE OF THE ION-ELECTRON SYSTEM \(eV\)\s*\-+\s*([\s\S]+?)\-{10}',
                sub_parser=TextParser(
                    quantities=[
                        Quantity(
                            'energy_total',
                            r'free\s*energy\s*TOTEN\s*=\s*([\-\d\.]+)',
                            repeats=False,
                            dtype=float,
                        ),
                        Quantity(
                            'energy_entropy0',
                            r'energy\s*without\s*entropy\s*=\s*([\-\d\.]+)',
                            repeats=False,
                            dtype=float,
                        ),
                        Quantity(
                            'energy_T0',
                            r'energy\(sigma\->0\)\s*=\s*([\-\d\.]+)',
                            repeats=False,
                            dtype=float,
                        ),
                    ]
                ),
            ),
            Quantity(
                'stress',
                r'in kB\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*(\-?\d+\.\d+)\s*'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)',
                str_operation=str_to_stress,
                convert=False,
            ),
            Quantity(
                'positions_forces',
                r'POSITION\s*TOTAL\-FORCE \(eV/Angst\)\s*\-+\s*([\d\.\s\-E]+)',
                str_operation=str_to_array,
                convert=False,
            ),
            Quantity(
                'lattice_vectors',
                r'direct lattice vectors\s*reciprocal lattice vectors\s*'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)',
                str_operation=str_to_array,
                convert=False,
            ),
            Quantity(
                'converged',
                r'aborting loop because (EDIFF is reached)',
                repeats=False,
                dtype=str,
                convert=False,
            ),
            Quantity(
                'fermi_energy', r'E\-fermi :\s*([\d\.]+)', dtype=str, repeats=False
            ),
            Quantity(
                'eigenvalues',
                r'band No\.\s*band energies\s*occupation\s*([\d\.\s\-\*]+?)(?:k\-point|spin|\-{10})',
                repeats=True,
                dtype=float,
                str_operation=str_to_eigenvalues,
            ),
            Quantity('convergence', r'(aborting loop because EDIFF is reached)'),
            Quantity(
                'time',
                r'LOOP\+\: +cpu time +([\d\.]+)\: +real time +([\d\.]+)',
                dtype=np.dtype(np.float64),
            ),
        ]

        self._quantities = [
            Quantity(
                'calculation',
                r'(\-\-\s*Iteration\s*\d+\(\s*1\s*\)\s*[\s\S]+?)'
                r'((?:FREE ENERGIE OF THE ION\-ELECTRON SYSTEM \(eV\)[\s\S]+?LOOP\+.+)|\Z)',
                repeats=True,
                sub_parser=TextParser(quantities=calculation_quantities),
            ),
            Quantity(
                'header',
                r'vasp\.([\d\.]+)\s*(\w+)\s*[\s\S]+?\)\s*(\w+)\s*'
                r'executed on\s*(\w+)\s*date\s*([\d\.]+)\s*([\d\:]+)\s*(\w+)',
                repeats=False,
                str_operation=str_to_header,
                convert=False,
            ),
            Quantity(
                'parameters',
                r'Startparameter for this run:([\s\S]+?)\-{100}',
                str_operation=get_key_values,
                repeats=False,
                convert=False,
            ),
            Quantity(
                'ions_per_type', r'ions per type =\s*([ \d]+)', dtype=int, repeats=False
            ),
            Quantity(
                'species',
                r'(\w+) +([A-Z][a-z]*).+?:\s*energy of atom +\d+',
                dtype=str,
                repeats=True,
            ),  # TODO: deprecate
            Quantity(
                'kpoints',
                r'Following reciprocal coordinates:[\s\S]+?\n([\d\.\s\-]+)',
                repeats=False,
                dtype=float,
            ),
            Quantity('nbands', r'NBANDS\s*=\s*(\d+)', dtype=int, repeats=False),
            Quantity(
                'lattice_vectors',
                r'direct lattice vectors\s*reciprocal lattice vectors\s*'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)'
                r'(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)(\-?\d+\.\d+\s*)',
                str_operation=str_to_array,
                convert=False,
            ),
            Quantity(
                'positions',
                r'ion\s*position\s*nearest neighbor table([\s\S]+?)LATTYP',
                str_operation=str_to_positions,
                convert=False,
            ),
            # alternative format
            Quantity(
                'positions',
                r'position of ions in cartesian coordinates\s*\(Angst\):([\s\S]+?)\n *\n',
                str_operation=str_to_positions,
                convert=False,
            ),
            Quantity(
                'response_functions',
                r'\s*Response functions by sum over occupied states\:([\s\S]+?)(?:\-\-\-\-\-\-)',
                repeats=False,
                sub_parser=TextParser(
                    quantities=[
                        Quantity(
                            'input_parameters',
                            rf'{RE_N}* *(\w+) *\= *([\w\.\-]+) *.*',
                            repeats=True,
                        )
                    ]
                ),
            ),
        ]


class OutcarParser(MappingTextParser):
    def get_version(self, source: Dict[str, Any]) -> str:
        return ' '.join(
            [
                source[key]
                for key in ['version', 'subversion', 'platform']
                if source.get(key)
            ]
        )

    def get_data(self, source: Any, **kwargs) -> Any:
        if isinstance(source, dict) and source.get('value') is not None:
            return source['value']
        path = kwargs.get('path')
        if path is None:
            return
        parser = Path(path=path)
        return parser.get_data(source)

    def get_energy_contributions(
        self, source: Dict[str, Any], **kwargs
    ) -> List[Dict[str, Any]]:
        exclude = kwargs.get('exclude', [])
        return [
            {'name': key, 'value': val}
            for key, val in source.items()
            if key not in exclude
        ]

    def get_eigenvalues(
        self, eigenvalues: np.ndarray, parameters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        ispin = parameters.get('ISPIN', 1)
        n_kpts = len(eigenvalues) // ispin
        n_bands = len(eigenvalues[0]) // 3
        eigenvalues = np.reshape(eigenvalues, (ispin, n_kpts, n_bands, 3))
        data = []
        for nspin in range(ispin):
            eigs, occs = eigenvalues[nspin].T[1:3]
            data.append(dict(eigenvalues=eigs.T, occupations=occs.T, n_bands=n_bands))
        return data


class VASPOutcarParser:
    def parse(
        self,
        mainfile: 'str',
        archive: 'EntryArchive',
        logger: 'BoundLogger',
        child_archives: 'dict[str, EntryArchive]' = None,
    ) -> None:
        # set up archive parser
        archive_data_parser = MetainfoParser()
        archive_data = Simulation()
        archive_data_parser.data_object = archive_data
        archive_data_parser.annotation_key = 'outcar'

        # set up outcar parser
        source_parser = OutcarParser()
        source_parser.text_parser = OutcarTextParser()
        source_parser.filepath = mainfile

        # TODO remove this for debug only
        self.archive_data_parser = archive_data_parser
        self.source_parser = source_parser

        # convert
        source_parser.convert(archive_data_parser)

        # assign simulation section to archive data
        archive.data = archive_data_parser.data_object

        # close file handles
        # archive_data_parser.close()
        # source_parser.close()
