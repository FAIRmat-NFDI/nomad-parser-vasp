from typing import (
    TYPE_CHECKING,
)

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.config import config
from nomad.parsing.file_parser.mapping_parser import (
    MappingAnnotationModel,
    MetainfoParser,
    XMLParser,
)
from nomad_simulations_plugin.numerical_settings import KMesh

configuration = config.get_plugin_entry_point('nomad_parser_vasp.parsers:myparser')

# TODO move to schema parser and prepare all relevant annotations for every file format

# ! vasprun.xml has many meta fields, explaining field semantics
Program.name.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.generator.i[@name="program"]')
)
Program.version.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.generator.i[@name="version"]')
)
# ? compilation mode?
Program.compilation_host.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.generator.i[@name="platform"]')
)
Simulation.m_annotations = dict(xml=MappingAnnotationModel(path='modeling'))
KMesh.grid.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.kpoints.generation.v[@name="divisions"]')
)
KMesh.offset.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.kpoints.generation.v[@name="shift"]')
)
KMesh.high_symmetry_points.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.kpoints.varray.v[@name="kpointlist"]')
)
KMesh.weights.m_annotations = dict(
    xml=MappingAnnotationModel(path='modeling.kpoints.varray.v[@name="weights"]')
)
dft_path = 'modeling.calculation[@name="electronic"]'
DFT.xc_functionals.libxc_name.m_annotations = dict(
    xml=MappingAnnotationModel(
        operator=(convert_xc, [dft_path + '.i[@name="GGA"]'])  # add LDA & mGGA
    )
)
DFT.exact_exchange_mixing_factor.m_annotations = dict(
    xml=MappingAnnotationModel(
        operator=(
            lambda mix, cond: mix if cond else 0,
            [dft_path + '.i[@name="HFALPHA"]', dft_path + '.i[@name="LHFCALC"]'],
        )
    )  # TODO convert vasp bool
)
# ? target <structure name="initialpos" > and <structure name="finalpos" >
AtomicCell.positions.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.structure.varray[@name="positions"]')
)
"""
forces.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.structure.varray[@name="forces"]')
)
stress.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.structure.varray[@name="stress"]')
)
"""
AtomicCell.lattice_vectors.m_annotations = dict(
    xml=MappingAnnotationModel(
        path='calculation.structure.crystal.varray[@name="basis"]'
    )
)
"""
cell_volume.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.structure.crystal.i[@name="volume"]')
)
reciprocal_lattice_vectors.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.structure.crystal.varray[@name="rec_basis"]')
)
total_free_energy.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.energy.i[@name="e_fr_energy"]')
)
total_internal_energy.m_annotations = dict(
    xml=MappingAnnotationModel(path='calculation.energy.i[@name="e_0_energy"]')
)
"""
ElectronicEigenvalues.spin_channel.m_annotations = dict(
    xml=MappingAnnotationModel(
        path='calculation.eigenvalues.array.set.set[@comment="spin 1"]'
    )
)
ElectronicEigenvalues.reciprocal_cell.m_annotations = dict(
    xml=MappingAnnotationModel(
        path=ElectronicEigenvalues.spin_channel.m_annotations.xml
        + '.set[@comment="kpoint 1"]'
    )  # TODO not going to work: add conversion to reference
)
ElectronicEigenvalues.occupation.m_annotations = dict(
    xml=MappingAnnotationModel(
        path=ElectronicEigenvalues.reciprocal_cell.m_annotations.xml + '.r[0]'
    )
)
ElectronicEigenvalues.value.m_annotations = dict(
    xml=MappingAnnotationModel(
        path=ElectronicEigenvalues.reciprocal_cell.m_annotations.xml + '.r[1]'
    )
)
# ? partial bands


class VasprunXMLParser(MatchingParser):
    def parse(
        self,
        mainfile: str,
        archive: EntryArchive,
        logger: BoundLogger,
        child_archives: dict[str, EntryArchive] = None,
    ) -> None:
        logger.info(
            self.__class__.__repr__() + '.parse', parameter=configuration.parameter
        )  # give feedback to Ahmed
        archive_parser = MetainfoParser(
            annotation_key='xml',
            data_object=[
                Program,
                Simulation(
                    model_system=[ModelSystem(cell=AtomicCell)],
                    model_method=[DFT, KMesh],
                    output=[ElectronicEigenvalues],
                ),
            ],
        )
        xml_parser = XMLParser(filepath='vasprun.xml')  # TODO apply match
        xml_parser.convert(archive_parser)
        archive.data = archive_parser.data_object
