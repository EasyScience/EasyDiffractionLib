__author__ = "github.com/wardsimon"
__version__ = "0.0.1"

from bokeh.io import push_notebook
from ipywidgets import widgets
import numpy as np


def update_job(job, figure_handle, line_handle, x_data):
    def inner(**kwargs):
        print(kwargs)
        for name, value in kwargs.items():
            item = job._borg.map.get_item_by_key(int(name))
            item.value = value
        line_handle.data_source.data["y"] = job.interface.fit_func(x_data)
        push_notebook(handle=figure_handle)

    return inner


def create_interactive(job, handle, vis_line, x_data):
    def generate_structural():
        cell_pars = {
            str(par._borg.map.convert_id_to_key(par)): widgets.HBox(
                [
                    widgets.Label(value=par.name),
                    widgets.FloatSlider(
                        min=0,
                        max=par.raw_value * 5,
                        value=par.raw_value,
                        continuous_update=False,
                    ),
                ]
            )
            for par in job.phases[0].cell.get_parameters()
            if par.enabled
        }
        return cell_pars

    cell_pars = generate_structural()
    par_pars = {
        str(par._borg.map.convert_id_to_key(par)): widgets.HBox(
            [
                widgets.Label(value=par.name),
                widgets.FloatSlider(
                    min=-np.abs(par.raw_value * 5),
                    max=np.abs(par.raw_value) * 5,
                    value=par.raw_value,
                    continuous_update=False,
                ),
            ]
        )
        for par in job.parameters.get_parameters()
        if par.enabled
    }
    pat_pars = {
        str(par._borg.map.convert_id_to_key(par)): widgets.HBox(
            [
                widgets.Label(value=par.name),
                widgets.FloatSlider(
                    min=0,
                    max=par.raw_value * 5,
                    value=par.raw_value,
                    continuous_update=False,
                ),
            ]
        )
        for par in job.pattern.get_parameters()
        if par.enabled
    }

    all_pars = dict(**cell_pars, **par_pars, **pat_pars)

    tab = widgets.Tab()
    tab.set_title(0, "Structural")
    tab.set_title(1, "Instrumental")
    tab.set_title(2, "Pattern")

    # interact function in isolation
    f = widgets.interactive(
        update_job(job, handle, vis_line, x_data),
        **{name: value.children[1] for name, value in all_pars.items()}
    )
    tab.children = [
        widgets.VBox(children=list(cell_pars.values())),
        widgets.VBox(children=list(par_pars.values())),
        widgets.VBox(children=list(pat_pars.values())),
    ]
    for value in all_pars.values():
        value.children[1].description = ""
    return tab
