from typing import TYPE_CHECKING

from nomad.metainfo.metainfo import SubSection

if TYPE_CHECKING:
    from nomad.datamodel.datamodel import (
        EntryArchive,
    )
    from structlog.stdlib import (
        BoundLogger,
    )

from nomad.metainfo import SchemaPackage
from nomad.parsing.file_parser.mapping_parser import MappingAnnotationModel
from nomad_simulations.schema_packages.general import Program, Simulation
from nomad_simulations.schema_packages.model_method import ModelMethod, DFT, XCFunctional
from nomad_simulations.schema_packages.model_system import (AtomicCell,
                                                            ModelSystem)
from nomad_simulations.schema_packages.numerical_settings import KMesh

m_package = SchemaPackage()

# note: vasprun.xml has many meta fields, explaining field semantics
Simulation.m_def.m_annotations['xml'] = MappingAnnotationModel(path='modeling')

Simulation.program.m_annotations['xml'] = MappingAnnotationModel(path='generator')

Simulation.model_method = SubSection(DFT.m_def)
Simulation.model_method.m_annotations['xml'] = MappingAnnotationModel(
    path='parameters'
)

Simulation.model_system.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation'
)

ModelSystem.cell.m_annotations['xml'] = MappingAnnotationModel(path='structure')

Simulation.outputs.m_annotations['xml'] = MappingAnnotationModel(path='calculation')

Program.name.m_annotations['xml'] = MappingAnnotationModel(
    path='modeling.generator.i[?"@name"==\'program\'] | [0].__value',
)

Program.version.m_annotations['xml'] = MappingAnnotationModel(
    path='modeling.generator.i[?"@name"==\'version\'] | [0].__value',
)

# Apply similar logic here
Program.compilation_host.m_annotations['xml'] = MappingAnnotationModel(
    path='modeling.generator.i[?"@name"==\'platform\'] | [0].__value'
)

DFT.m_def.m_annotations['xml'] = MappingAnnotationModel(
    path='separator[?"@name"==\'electronic exchange-correlation\']'
)

DFT.numerical_settings.m_annotations['xml'] = MappingAnnotationModel(
    path='modeling.kpoints'
)

DFT.xc_functionals.m_annotations['xml'] = MappingAnnotationModel(
    path='.'
)

DFT.exact_exchange_mixing_factor.m_annotations = dict(
    xml=MappingAnnotationModel(
        operator=(
            'mix_alpha',
            [
                'i[?"@name"==\'HFALPHA\'] | [0].__value',
                'i[?"@name"==\'LHFCALC\'] | [0].__value',
            ],
        )
    )  # TODO convert vasp bool
)

XCFunctional.libxc_name.m_annotations = dict(
    xml=MappingAnnotationModel(
        path='i[?"@name"==\'GGA\'] | [0].__value'  # TODO add LDA & mGGA, convert_xc
    )
)

KMesh.grid.m_annotations['xml'] = MappingAnnotationModel(
    path='generation.v[?"@name"==\'divisions\'] | [0].__value'
)

KMesh.offset.m_annotations['xml'] = MappingAnnotationModel(
    path='generation.v[?"@name"==\'shift\'] | [0].__value'
)

KMesh.points.m_annotations['xml'] = MappingAnnotationModel(
    path='varray[?"@name"==\'kpointlist\'].v | [0].__value'
)

KMesh.weights.m_annotations['xml'] = MappingAnnotationModel(
    path='varray[?"@name"==\'weights\'].v | [0].__value'
)

# ? target <structure name="initialpos" > and <structure name="finalpos" >

AtomicCell.positions.m_annotations = dict(
    xml=MappingAnnotationModel(path='varray[?"@name"==\'positions\'] | [0].__value')
)

"""
...forces.m_annotations['xml'] = MappingAnnotationModel(
    path='varray[?"@name"==\'forces\'] | [0].__value'
)

...stress.m_annotations['xml'] = MappingAnnotationModel(
    path='varray[?"@name"==\'stress\'] | [0].__value'
)
"""

AtomicCell.lattice_vectors.m_annotations['xml'] = MappingAnnotationModel(
    path='crystal.varray[?"@name"==\'basis\'] | [0].__value'
)

"""
cell_volume.m_annotations['xml'] = MappingAnnotationModel(
    path='crystal.i[?"@name"==\'volume\'] | [0].__value'
)

reciprocal_lattice_vectors.m_annotations['xml'] = MappingAnnotationModel(
    path='crystal.varray[?"@name"==\'rec_basis\'] | [0].__value'
)

total_free_energy.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation.energy.i[?"@name"==\'e_fr_energy\'] | [0].__value'
)

total_internal_energy.m_annotations['xml'] = MappingAnnotationModel(
    path='calculation.energy.i[?"@name"==\'e_0_energy\'] | [0].__value'
)

...eigenvalues.m_annotations['xml'] = MappingAnnotationModel(
    path='.eigenvalues.array'
)

ElectronicEigenvalues.spin_channel.m_annotations['xml'] = MappingAnnotationModel(
    path='.eigenvalues.set.set[?comment==\'spin 1\'] | [0].__value'
)

ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.spin_channel.m_annotations['xml']
    + '.set[?comment==\'kpoint 1\'] | [0].__value'
)

ElectronicEigenvalues.occupation.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] + '.r[0] | [0].__value'
)

ElectronicEigenvalues.value.m_annotations['xml'] = MappingAnnotationModel(
    path=ElectronicEigenvalues.reciprocal_cell.m_annotations['xml'] + '.r[1] | [0].__value'
)
"""

m_package.__init_metainfo__()
