# Dictionaries

All parameter names used in EasyDiffraction are divided into several
dictionaries given below. Each keyword in the dictionaries has one badge showing
the corresponding type of dictionary, and can have one or more badges showing
the type of experiment to which the keyword belongs.

## Crystallographic information file

EasyDiffraction input and output files use the simple, human-readable STAR/CIF
data format, following the specifications of
[International Union of Crystallography](https://www.iucr.org) (IUCr), wherever
possible.

## Model dictionary

This dictionary provides data names for describing model parameters.

[pd-neut-cwl][3]{:.label-experiment} [pd-neut-tof][3]{:.label-experiment}
[sc-neut-cwl][3]{:.label-experiment} [pd-xray][3]{:.label-experiment}

- [\_space_group](dictionaries/_space_group.md) [coreCIF][1]{:.label-cif}
  - [\_space_group.name_H-M_alt](dictionaries/_space_group.md)
    [coreCIF][1]{:.label-cif}
  - [\_space_group.IT_coordinate_system_code](dictionaries/_space_group.md)
    [coreCIF][1]{:.label-cif}
- [\_cell](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
  - [\_cell.angle_alpha](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
  - [\_cell.angle_beta](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
  - [\_cell.angle_gamma](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
  - [\_cell.length_a](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
  - [\_cell.length_b](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
  - [\_cell.length_c](dictionaries/_cell.md) [coreCIF][1]{:.label-cif}
- [\_atom_site](dictionaries/_atom_site.md) [coreCIF][1]{:.label-cif}
  - [\_atom_site.label](dictionaries/_atom_site.md) [coreCIF][1]{:.label-cif}
  - [\_atom_site.type_symbol](dictionaries/_atom_site.md)
    [coreCIF][1]{:.label-cif}
  - [\_atom_site.fract_x](dictionaries/_atom_site.md) [coreCIF][1]{:.label-cif}
  - [\_atom_site.fract_y](dictionaries/_atom_site.md) [coreCIF][1]{:.label-cif}
  - [\_atom_site.fract_z](dictionaries/_atom_site.md) [coreCIF][1]{:.label-cif}
  - [\_atom_site.occupancy](dictionaries/_atom_site.md)
    [coreCIF][1]{:.label-cif}
  - [\_atom_site.ADP_type](dictionaries/_atom_site.md) [coreCIF][1]{:.label-cif}
  - [\_atom_site.B_iso_or_equiv](dictionaries/_atom_site.md)
    [coreCIF][1]{:.label-cif}
  - [\_atom_site.site_symmetry_multiplicity](dictionaries/_atom_site.md)
    [coreCIF][1]{:.label-cif}
  - [\_atom_site.Wyckoff_symbol](dictionaries/_atom_site.md)
    [coreCIF][1]{:.label-cif}

## Experiment and instrument dictionary

This dictionary provides data names for describing experimental and instrumental
parameters.

[pd-neut-cwl][3]{:.label-experiment} [pd-neut-tof][3]{:.label-experiment}
[sc-neut-cwl][3]{:.label-experiment} [pd-xray][3]{:.label-experiment}

- [\_diffrn_radiation](dictionaries/_diffrn_radiation.md)
  [coreCIF][1]{:.label-cif}
  - [\_diffrn_radiation.probe](dictionaries/_diffrn_radiation.md)
    [coreCIF][1]{:.label-cif}

[pd-neut-cwl][3]{:.label-experiment} [sc-neut-cwl][3]{:.label-experiment}
[pd-xray][3]{:.label-experiment}

- [\_diffrn_radiation_wavelength](dictionaries/_diffrn_radiation_wavelength.md)
  [coreCIF][1]{:.label-cif}
  - [\_diffrn_radiation_wavelength.wavelength](dictionaries/_diffrn_radiation_wavelength.md)
    [coreCIF][1]{:.label-cif}
- [\_pd_background](dictionaries/_pd_background.md) [pdCIF][2]{:.label-cif}
  - [\_pd_background.line_segment_X](dictionaries/_pd_background.md)
    [pdCIF][2]{:.label-cif}
  - [\_pd_background.line_segment_intensity](dictionaries/_pd_background.md)
    [pdCIF][2]{:.label-cif}
  - [\_pd_background.X_coordinate](dictionaries/_pd_background.md)
    [pdCIF][2]{:.label-cif}
- [\_pd_phase_block](dictionaries/_pd_phase.md) [pdCIF][2]{:.label-cif}
  - [\_pd_phase_block.id](dictionaries/_pd_phase.md) [pdCIF][2]{:.label-cif}
  - [\_pd_phase_block.scale](dictionaries/_pd_phase.md)
    [customCIF][0]{:.label-cif}

[pd-neut-cwl][3]{:.label-experiment}

- [\_pd_calib](dictionaries/_pd_calib.md) [pdCIF][2]{:.label-cif}
  - [\_pd_calib.2theta_offset](dictionaries/_pd_calib.md)
    [pdCIF][2]{:.label-cif}
- [\_pd_instr](dictionaries/_pd_instr.md) [pdCIF][2]{:.label-cif}
  - [\_pd_instr.resolution_u](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.resolution_v](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.resolution_w](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.resolution_x](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.resolution_y](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.reflex_asymmetry_p1](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.reflex_asymmetry_p2](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.reflex_asymmetry_p3](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.reflex_asymmetry_p4](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
- [\_pd_meas](dictionaries/_pd_meas.md) [pdCIF][2]{:.label-cif}
  - [\_pd_meas.2theta_scan](dictionaries/_pd_meas.md) [pdCIF][2]{:.label-cif}
  - [\_pd_meas.intensity_total](dictionaries/_pd_meas.md)
    [pdCIF][2]{:.label-cif}
  - [\_pd_meas.intensity_total_su](dictionaries/_pd_meas.md)
    [pdCIF][2]{:.label-cif}

[pd-neut-tof][3]{:.label-experiment}

- [\_pd_instr](dictionaries/_pd_instr.md) [pdCIF][2]{:.label-cif}
  - [\_pd_instr.zero](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.dtt1](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.dtt2](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.2theta_bank](dictionaries/_pd_instr.md)
    [customCIF][0]{:.label-cif}
  - [\_pd_instr.alpha0](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.alpha1](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.beta0](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.beta1](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.sigma0](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.sigma1](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
  - [\_pd_instr.sigma2](dictionaries/_pd_instr.md) [customCIF][0]{:.label-cif}
- [\_pd_meas](dictionaries/_pd_meas.md) [pdCIF][2]{:.label-cif}
  - [\_pd_meas.time_of_flight](dictionaries/_pd_meas.md) [pdCIF][2]{:.label-cif}
  - [\_pd_meas.intensity_total](dictionaries/_pd_meas.md)
    [pdCIF][2]{:.label-cif}
  - [\_pd_meas.intensity_total_su](dictionaries/_pd_meas.md)
    [pdCIF][2]{:.label-cif}

[sc-neut-cwl][3]{:.label-experiment}

- [\_extinction](dictionaries/_extinction.md) [customCIF][0]{:.label-cif}

  - [\_extinction.model](dictionaries/_extinction.md)
    [customCIF][0]{:.label-cif}
  - [\_extinction.mosaicity](dictionaries/_extinction.md)
    [customCIF][0]{:.label-cif}
  - [\_extinction.radius](dictionaries/_extinction.md)
    [customCIF][0]{:.label-cif}

- [\_exptl_crystal](dictionaries/_exptl_crystal.md) [customCIF][0]{:.label-cif}
  - [\_exptl_crystal.id](dictionaries/_exptl_crystal.md)
    [customCIF][0]{:.label-cif}
  - [\_exptl_crystal.scale](dictionaries/_exptl_crystal.md)
    [customCIF][0]{:.label-cif}

<!-- prettier-ignore-start -->
[0]: #
[1]: https://www.iucr.org/resources/cif/dictionaries/browse/cif_core
[2]: https://www.iucr.org/resources/cif/dictionaries/browse/cif_pd
[3]: glossary.md
<!-- prettier-ignore-end -->
