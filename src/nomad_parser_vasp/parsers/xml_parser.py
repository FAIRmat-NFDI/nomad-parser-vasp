from nomad.datamodel.datamodel import (
    EntryArchive,
)
from structlog.stdlib import (
    BoundLogger,
)

from nomad.config import config
from nomad.parsing import MatchingParser
from nomad.parsing.file_parser.mapping_parser import (
    MappingAnnotationModel,
    MetainfoParser,
    XMLParser,
)
from nomad_simulations.schema_packages.general import Simulation, Program
from nomad_simulations.schema_packages.model_system import (
    ModelSystem,
    AtomicCell,
)
from nomad_simulations.schema_packages.model_method import (
    DFT,
    XCFunctional,
)
from nomad_simulations.schema_packages.numerical_settings import KMesh

configuration = config.get_plugin_entry_point(
    'nomad_parser_vasp.parsers:xml_entry_point'
)

# TODO move to schema parser and prepare all relevant annotations for every file format


# ! vasprun.xml has many meta fields, explaining field semantics
Simulation.m_def.m_annotations['xml'] = MappingAnnotationModel(path='modeling')

Simulation.program.m_annotations['xml'] = MappingAnnotationModel(path='.generator')

Simulation.model_method.m_annotations['xml'] = MappingAnnotationModel(
    path='.parameters'
)

Simulation.model_system.m_annotations['xml'] = MappingAnnotationModel(
    path='.calculation'
)

Simulation.model_system.cell.m_annotations['xml'] = MappingAnnotationModel(
    path='.structure'
)

Simulation.outputs.m_annotations['xml'] = MappingAnnotationModel(path='.calculation')

Program.name.m_annotations['xml'] = MappingAnnotationModel(
    path='.i[?"@name"="program"]'
)

Program.version.m_annotations['xml'] = MappingAnnotationModel(
    path='.i[?"@name"="version"]'
)

# ? compilation mode
Program.compilation_host.m_annotations['xml'] = MappingAnnotationModel(
    path='.i[?"@name"="platform"]'
)

DFT.numerical_settings.m_annotations['xml'] = MappingAnnotationModel(
    path='modeling.kpoints'
)

dft_path = '.separator[?"@name"="electronic exchange-correlation"]'
DFT.xc_functionals.m_annotations['xml'] = MappingAnnotationModel(
    path=dft_path
)  # start from Simulation.model_method path

DFT.exact_exchange_mixing_factor.m_annotations = dict(
    xml=MappingAnnotationModel(
        operator=(
            lambda mix, cond: mix if cond else 0,
            [dft_path + '.i[?"@name"="HFALPHA"]', dft_path + '.i[?"@name"="LHFCALC"]'],
        )
    )  # TODO convert vasp bool
)

XCFunctional.libxc_name.m_annotations = dict(
    xml=MappingAnnotationModel(
        path=dft_path + '.i[?"@name"="GGA"]'  # TODO add LDA & mGGA, convert_xc
    )
)

KMesh.grid.m_annotations['xml'] = MappingAnnotationModel(
    path='.generation.v[?"@name"="divisions"]'
)  # start from DFT.numerical_settings

KMesh.offset.m_annotations['xml'] = MappingAnnotationModel(
    path='.generation.v[?"@name"="shift"]'
)  # start from DFT.numerical_settings

KMesh.offset.m_annotations['xml'] = MappingAnnotationModel(
    path='.generation.v[?"@name"="shift"]'
)  # start from DFT.numerical_settings

KMesh.points.m_annotations['xml'] = MappingAnnotationModel(
    path='.varray[?"@name"="kpointlist"].v'
)  # start from DFT.numerical_settings

KMesh.weights.m_annotations['xml'] = MappingAnnotationModel(
    path='.varray[?"@name"="weights"].v'
)  # start from DFT.numerical_settings


# ? target <structure name="initialpos" > and <structure name="finalpos" >


AtomicCell.positions.m_annotations = dict(
    xml=MappingAnnotationModel(path='.varray[?"@name"="positions"]')
)  # start from Simulation.model_system.cell path

"""
...forces.m_annotations['xml'] = MappingAnnotationModel(
    path='.varray[?"@name"="forces"]'
)  # start from Simulation.model_system.cell path

...stress.m_annotations['xml'] = MappingAnnotationModel(
    path='.varray[?"@name"="stress"]'
)  # start from Simulation.model_system.cell path
"""

AtomicCell.lattice_vectors.m_annotations['xml'] = MappingAnnotationModel(
    path='.crystal.varray[?"@name"="basis"]'
)  # start from Simulation.model_system.cell path

"""
cell_volume.m_annotations['xml'] = MappingAnnotationModel(
    path='.crystal.i[?"@name"="volume"]'
)  # start from Simulation.model_system.cell path

reciprocal_lattice_vectors.m_annotations['xml'] = MappingAnnotationModel(
    path='.crystal.varray[?"@name"="rec_basis"]'
)  # start from Simulation.model_system.cell path

total_free_energy.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation.energy.i[?"@name"="e_fr_energy"]'
)

total_internal_energy.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation.energy.i[?"@name"="e_0_energy"]'
)

...eigenvalues.m_annotations['xml'] = MappingAnnotationModel(
    path='.eigenvalues.array'
)

ElectronicEigenvalues.spin_channel.m_annotations['xml'] = MappingAnnotationModel(
    path='.eigenvalues.set.set[?"@comment"="spin 1"]'
)  # start from Simulation.outputs path

ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.spin_channel.m_annotations.xml
    + '.set[?"@comment"="kpoint 1"]'
)  # TODO not going to work: add conversion to reference

ElectronicEigenvalues.occupation.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.reciprocal_cell.m_annotations.xml + '.r[0]'
)

ElectronicEigenvalues.value.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.reciprocal_cell.m_annotations.xml + '.r[1]'
)
"""


class VasprunXMLParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] = None,
    ) -> None:
        logger.info('VasprunXMLParser.parse', parameter=configuration.parameter)
        data_parser = MetainfoParser(annotation_key='xml', data_object=Simulation())
        XMLParser(filepath=mainfile).convert(data_parser)
        archive.data = data_parser.data_object
