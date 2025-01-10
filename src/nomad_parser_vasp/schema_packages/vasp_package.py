from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from nomad.datamodel.metainfo.annotations import Mapper as MapperAnnotation
from nomad.metainfo import SchemaPackage
from nomad.parsing.file_parser.mapping_parser import MAPPING_ANNOTATION_KEY
from nomad_simulations.schema_packages import (
    general,
    model_method,
    model_system,
    numerical_settings,
    outputs,
    properties,
    variables,
)

m_package = SchemaPackage()

OUTCAR_ANNOTATION_KEY = 'outcar'
XML_ANNOTATION_KEY = 'xml'
XML2_ANNOTATION_KEY = 'xml2'


general.Program.name.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(
    mapper='.i[?"@name"==\'program\'] | [0].__value',
)

general.Program.version.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(
    mapper='.i[?"@name"==\'version\'] | [0].__value',
)

general.Program.version.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(
    mapper=('get_version', ['.@']),
)

# Apply similar logic here
general.Program.compilation_host.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.i[?"@name"==\'platform\'] | [0].__value')


model_method.XCFunctional.libxc_name.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(
    mapper='.i[?"@name"==\'GGA\'] | [0].__value'  # TODO add LDA & mGGA, convert_xc
)
model_method.XCFunctional.libxc_name.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.name')


numerical_settings.KMesh.grid.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.generation.v[?"@name"==\'divisions\'] | [0].__value')

numerical_settings.KMesh.offset.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.generation.v[?"@name"==\'shift\'] | [0].__value')

numerical_settings.KMesh.points.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.varray[?"@name"==\'kpointlist\'].v | [0]')

numerical_settings.KMesh.weights.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.varray[?"@name"==\'weights\'].v | [0]')


numerical_settings.KSpace.k_mesh.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.@')


model_method.DFT.xc_functionals.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.separator[?"@name"==\'electronic exchange-correlation\']')
model_method.DFT.xc_functionals.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper=('get_xc_functionals', ['.@']))

model_method.DFT.exact_exchange_mixing_factor.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(
    mapper=(
        'mix_alpha',
        [
            '.i[?"@name"==\'HFALPHA\'] | [0].__value',
            '.i[?"@name"==\'LHFCALC\'] | [0].__value',
        ],
    )
)  # TODO convert vasp bool

numerical_settings.KSpace.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='modeling.kpoints')


model_system.AtomicCell.positions.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.varray.v', unit='angstrom')
model_system.AtomicCell.positions.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.positions_forces', unit='angstrom', search='@ | [0]')

model_system.AtomicCell.lattice_vectors.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(
    mapper='.crystal.varray[?"@name"==\'basis\'] | [0].v', unit='angstrom'
)
model_system.AtomicCell.lattice_vectors.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(
    mapper='.lattice_vectors', unit='angstrom', search='@ | [0]'
)


model_system.AtomicCell.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.structure')
model_system.AtomicCell.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.@')


variables.Variables.n_points.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.npoints')
variables.Variables.n_points.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.npoints')


properties.energies.EnergyContribution.name.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(mapper='."@name"')
properties.energies.EnergyContribution.name.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.name')
# value is already defined in TotalEnergy since they use the same def
# get_energy function should be able to handle extraction from both sources


properties.energies.TotalEnergy.value.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(
    mapper=(
        'get_data',
        ['.@'],
        dict(path='.i[?"@name"==\'e_fr_energy\'] | [0].__value'),
    ),
    unit='eV',
)
properties.energies.TotalEnergy.value.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(
    mapper=('get_data', ['.@'], dict(path='.energy_total')), unit='eV'
)

properties.energies.TotalEnergy.contributions.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(
    mapper=('get_energy_contributions', ['.i'], dict(exclude=['e_fr_energy']))
)
properties.energies.TotalEnergy.contributions.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(
    mapper=('get_energy_contributions', ['.@'], dict(exclude=['energy_total']))
)


properties.forces.TotalForce.rank.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.rank')
properties.forces.TotalForce.variables.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(mapper='.@')
properties.forces.TotalForce.value.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.forces', unit='eV/angstrom')
properties.forces.TotalForce.rank.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.rank')
properties.forces.TotalForce.variables.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.@')
properties.forces.TotalForce.value.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(
    mapper='.forces',
    unit='eV/angstrom',
)


outputs.ElectronicEigenvalues.n_bands.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(mapper='length(.array.set.set.set[0].r)')
outputs.ElectronicEigenvalues.n_bands.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML2_ANNOTATION_KEY] = MapperAnnotation(mapper='length(.array.set.set.set[0].r)')
outputs.ElectronicEigenvalues.n_bands.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.n_bands')
outputs.ElectronicEigenvalues.variables.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.@')

# TODO This only works for non-spin pol
outputs.ElectronicEigenvalues.occupation.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML2_ANNOTATION_KEY] = MapperAnnotation(mapper='.occupations')
outputs.ElectronicEigenvalues.occupation.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.occupations')
outputs.ElectronicEigenvalues.value.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML2_ANNOTATION_KEY] = MapperAnnotation(mapper='.eigenvalues')
outputs.ElectronicEigenvalues.value.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(mapper='.eigenvalues')


outputs.Outputs.total_energies.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.energy')
outputs.Outputs.total_energies.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.energies')
outputs.Outputs.total_forces.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper=('get_forces', ['.@']))
outputs.Outputs.total_forces.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper=('get_forces', ['.@']))
outputs.Outputs.electronic_eigenvalues.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML_ANNOTATION_KEY] = MapperAnnotation(mapper=('get_eigenvalues', ['eigenvalues']))
outputs.Outputs.electronic_eigenvalues.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[XML2_ANNOTATION_KEY] = MapperAnnotation(mapper=('get_eigenvalues', ['eigenvalues']))
outputs.Outputs.electronic_eigenvalues.m_annotations.setdefault(
    MAPPING_ANNOTATION_KEY, {}
)[OUTCAR_ANNOTATION_KEY] = MapperAnnotation(
    mapper=('get_eigenvalues', ['.eigenvalues', 'parameters'])
)


general.Simulation.program.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.generator')
general.Simulation.program.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.header')

model_method.DFT.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.parameters.separator[?"@name"==\'electronic\']')
model_method.DFT.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='parameters')

general.Simulation.model_system.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.calculation')
general.Simulation.model_system.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.calculation')

general.Simulation.outputs.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='.calculation')
general.Simulation.outputs.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML2_ANNOTATION_KEY
] = MapperAnnotation(mapper='.calculation')
general.Simulation.outputs.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='.calculation')


# note: vasprun.xml has many meta fields, explaining field semantics
general.Simulation.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML_ANNOTATION_KEY
] = MapperAnnotation(mapper='modeling')
general.Simulation.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    XML2_ANNOTATION_KEY
] = MapperAnnotation(mapper='modeling')
general.Simulation.m_def.m_annotations.setdefault(MAPPING_ANNOTATION_KEY, {})[
    OUTCAR_ANNOTATION_KEY
] = MapperAnnotation(mapper='@')


m_package.__init_metainfo__()
