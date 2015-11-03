"""This is the Bokeh charts interface. It gives you a high level API
to build complex plot is a simple way.

This is the Scatter class which lets you build your Scatter charts
just passing the arguments to the Chart class and calling the proper
functions.
"""
#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2014, Continuum Analytics, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import absolute_import

from bokeh.charts.builder import create_and_build
from bokeh.charts.glyphs import HorizonGlyph
from .line_builder import LineBuilder
from ...properties import Float, Int, List, string_types, String, Color, Bool
from ..attributes import ColorAttr, DashAttr, MarkerAttr, IdAttr
from ...models.sources import ColumnDataSource
from ...models.axes import CategoricalAxis
from ...models.ranges import FactorRange

#-----------------------------------------------------------------------------
# Classes and functions
#-----------------------------------------------------------------------------


def Horizon(data=None, x=None, y=None, series=None, **kws):
    """ Create a scatter chart using :class:`ScatterBuilder <bokeh.charts.builders.scatter_builder.ScatterBuilder>`
    to render the geometry from values.

    Args:
        data (:ref:`userguide_charts_data_types`): table-like data
        x (str or list(str), optional): the column label to use for the x dimension
        y (str or list(str), optional): the column label to use for the y dimension

    In addition the the parameters specific to this chart,
    :ref:`userguide_charts_defaults` are also accepted as keyword parameters.

    Returns:
        :class:`Chart`: includes glyph renderers that generate the scatter points

    Examples:

    .. bokeh-plot::
        :source-position: above

        from bokeh.sampledata.autompg import autompg as df
        from bokeh.charts import Scatter, output_file, show

        scatter = Scatter(df, x='mpg', y='hp', color='cyl', marker='origin',
                          title="Auto MPG", xlabel="Miles Per Gallon",
                          ylabel="Horsepower")

        output_file('scatter.html')
        show(scatter)

    """
    kws['x'] = x
    kws['y'] = y

    tools = kws.get('tools', True)
    if tools == True:
        tools = "save,resize,reset"
    elif isinstance(tools, string_types):
        tools = tools.replace('pan', '')
        tools = tools.replace('wheel_zoom', '')
        tools = tools.replace('box_zoom', '')
        tools = tools.replace(',,', ',')
    kws['tools'] = tools

    chart = create_and_build(HorizonBuilder, data, **kws)

    # Hide numerical axis
    chart.left[0].visible = False

    # Add the series names to the y axis
    chart.extra_y_ranges = {"series": FactorRange(factors=chart._builders[0].series_names)}
    chart.add_layout(CategoricalAxis(y_range_name="series"), 'left')
    return chart


class HorizonBuilder(LineBuilder):
    """This is the Scatter class and it is in charge of plotting
    Scatter charts in an easy and intuitive way.

    Essentially, we provide a way to ingest the data, make the proper
    calculations and push the references into a source object.
    We additionally make calculations for the ranges. And finally add
    the needed glyphs (markers) taking the references from the source.

    """

    glyph = HorizonGlyph
    series_max = Float()
    series_count = Int()
    bins = List(Float)
    series_column = String()
    fold_height = Float()
    graph_ratio = Float()
    positive_color = '#006400'
    default_attributes = {'bin_num': IdAttr(sort=True, ascending=True),
                          'color': ColorAttr(sort=False),
                          'dash': DashAttr(),
                          'marker': MarkerAttr(),
                          'series': IdAttr(sort=False)}

    pos_color = Color("#006400", help="""
    The color of the positive folds. (default: "#006400")
    """)

    neg_color = Color("#6495ed", help="""
    The color of the negative folds. (default: "#6495ed")
    """)

    num_folds = Int(3, help="""
    The number of folds stacked on top of each other. (default: 3)
    """)

    flip_neg = Bool(default=True)

    def setup(self):
        super(HorizonBuilder, self).setup()

        # collect series names and columns selected to color by
        if self.attributes['series'].columns is None:
            self.series_column = self.attributes['color'].columns[0]
        else:
            self.series_column = self.attributes['series'].columns

        self.series_max = self.y.data.max()
        self.series_count = len(self.series_names)

    def process_data(self):
        super(HorizonBuilder, self).process_data()

        # calculate group attributes, useful for each horizon glyph
        self.fold_height = max(self.y.max, abs(self.y.min))/self.num_folds
        self.bins = [bin_id * self.fold_height for bin_id in range(self.num_folds + 1)]
        self.graph_ratio = self.num_folds / len(self.series_names)

        # manually set attributes to have constant color
        ds = ColumnDataSource(self._data.df)
        self.attributes['series'].setup(data=ds, columns=self.series_column)
        self.attributes['color'].setup(data=ds, columns=self.pos_color)

    def set_ranges(self):
        super(HorizonBuilder, self).set_ranges()
        self.y_range.start = 0
        self.y_range.end = self.series_max
