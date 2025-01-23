from numpy.testing import assert_almost_equal

import easydiffraction as ed


def test_fitting_pd_neut_cwl_LBCO_HRPT() -> None:
    """
    Test fitting of La0.5Ba0.5CoO3 from neutron diffraction data
    in a constant wavelength experiment performed on HRPT@PSI.
    :return: None
    """
    job = ed.Job()

    job.add_phase_from_file('tests/data/lbco.cif')
    job.add_experiment_from_file('tests/data/hrpt.xye')

    job.phases['lbco'].cell.length_a = 3.89
    job.phases['lbco'].scale = 6
    job.set_background([(10.0, 170), (165.0, 170)])
    job.pattern.zero_shift = 0.5
    job.instrument.wavelength = 1.494
    job.instrument.resolution_u = 0.1
    job.instrument.resolution_v = -0.1
    job.instrument.resolution_w = 0.1
    job.instrument.resolution_x = 0
    job.instrument.resolution_y = 0.05

    job.phases['lbco'].cell.length_a.free = True
    job.phases['lbco'].atom_sites['La'].b_iso_or_equiv.free = True
    job.phases['lbco'].atom_sites['Ba'].b_iso_or_equiv.free = True
    job.phases['lbco'].atom_sites['Co'].b_iso_or_equiv.free = True
    job.phases['lbco'].atom_sites['O'].b_iso_or_equiv.free = True
    job.phases['lbco'].scale.free = True
    job.pattern.zero_shift.free = True
    job.pattern.backgrounds[0][0].y.free = True
    job.pattern.backgrounds[0][1].y.free = True
    job.instrument.resolution_u.free = True
    job.instrument.resolution_v.free = True
    job.instrument.resolution_w.free = True
    job.instrument.resolution_y.free = True

    job.fit()

    assert job.fitting_results.minimizer_engine.package == 'lmfit'
    assert job.fitting_results.x.size == 3098
    assert job.fitting_results.n_pars == 13
    assert job.fitting_results.success
    assert_almost_equal(job.fitting_results.reduced_chi, 1.25, decimal=2)


def test_fitting_pd_neut_tof_Si_SEPD() -> None:
    """
    Test fitting of Si from neutron diffraction data in a time-of-flight
    experiment performed on SEPD@Argonne.
    :return: None
    """
    job = ed.Job(type='tof')

    phase = ed.Phase(name='si')
    phase.space_group.name_hm_alt = 'F d -3 m'
    phase.cell.length_a = 5.43146
    phase.atom_sites.append(
        label='Si',
        type_symbol='Si',
        fract_x=0.125,
        fract_y=0.125,
        fract_z=0.125,
        occupancy=1,
        b_iso_or_equiv=0.529,
    )
    job.add_phase(phase=phase)
    job.phases['si'].scale = 10

    job.add_experiment_from_file('tests/data/sepd.xye')

    job.set_background([(x, 200) for x in range(0, 35000, 5000)])
    job.parameters.dtt1 = 7476.91
    job.parameters.dtt2 = -1.54
    job.parameters.ttheta_bank = 144.845
    job.parameters.alpha0 = 0.024
    job.parameters.alpha1 = 0.204
    job.parameters.beta0 = 0.038
    job.parameters.beta1 = 0.011
    job.parameters.sigma0 = 0.0
    job.parameters.sigma1 = 0.0
    job.parameters.sigma2 = 0.0

    phase.scale.free = True
    job.pattern.zero_shift.free = True
    for background_point in job.pattern.backgrounds[0]:
        background_point.y.free = True
    job.parameters.sigma0.free = True
    job.parameters.sigma1.free = True
    job.parameters.sigma2.free = True

    job.fit()

    assert phase.space_group.name_hm_alt.raw_value == 'F d -3 m'
    assert phase.space_group.it_coordinate_system_code.raw_value == '2'
    assert job.fitting_results.minimizer_engine.package == 'lmfit'
    assert job.fitting_results.x.size == 5600
    assert job.fitting_results.n_pars == 12
    assert job.fitting_results.success
    assert_almost_equal(job.fitting_results.reduced_chi, 5.42, decimal=2)


if __name__ == '__main__':
    test_fitting_pd_neut_cwl_LBCO_HRPT()
