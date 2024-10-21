# SPDX-FileCopyrightText: 2024 EasyDiffraction contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2021-2024 Contributors to the EasyDiffraction project <https://github.com/easyscience/EasyDiffraction

from easyscience.Datasets.xarray import xr


class Runner:
    def __init__(self):
        self._data = xr.Dataset()
        self._jobs = {}
        self._instrumental_parameters = []
        self._instrumental_parameters_link = {}
        self._experimental_parameters = []
        self._experimental_parameters_link = {}
        self._phases = []
        self._phase_link = {}

    def add_job(self, name: str, job_type: str = 'powder1d'):
        if job_type == 'powder1d':
            from easydiffraction.Jobs import Powder1DCW
            job_type = Powder1DCW
        elif job_type == 'powder1dTOF':
            from easydiffraction.Jobs import Powder1DTOF
            job_type = Powder1DTOF
        else:
            raise NotImplementedError
        job = job_type(name, self._data)
        self._jobs[name] = {
            'object':                  job,
            'phases':                  job.phases,
            'instrumental_parameters': job.parameters,
            'experimental_parameters': job.pattern
        }

    @property
    def phases(self):
        return [phase.name for phase in self._phases]

    def add_phase(self, phase, job_name: str = None):
        if phase.name in self.phases:
            raise AttributeError
        if job_name is None:
            self._phases.append(phase)
            return
        if job_name not in self._jobs.keys():
            raise AttributeError
        self._phases.append(phase)
        self._jobs[job_name]['object'].phases = phase

    @property
    def jobs(self):
        return {key: job['object'] for key, job in self._jobs.items()}
