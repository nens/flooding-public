# -*- coding: utf-8 -*-
import csv

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.conf import settings

from flooding_lib.tools.pyramids import pyramids
from flooding_visualization.symbol_manager import SymbolManager
from flooding_visualization.mapnik_legend import MapnikPointLegend
from flooding_visualization.models import ShapeDataLegend
from flooding_presentation.models import PresentationType, PresentationLayer
from flooding_presentation.views import external_file_location


def get_symbol(request, symbol):
    """Get a symbol, which is optionally colored, rotated, scaled

    inputs: via GET
      - symbol: <filename_nopath> of symbol, e.g. plus_64.png
      - mask (optional): <filename_nopath> of mask, e.g. plus_64_mask.png
      - colorize (optional): <r,g,b> (float 0..1) e.g. 0.5,0.3,0.7
      - size (optional): <x,y>, cannot be 0 e.g. 32,32
      - rotate (optional): <angle> int in degrees, ccw e.g. 180

      - shadow_height (optional): <shadow_height> shadow height in
        pixels e.g. 2

    output: binary png, or exception if original does not exist
    """

    #get GET parameters
    q = request.GET

    kwargs = {}
    if q.__contains__('mask'):
        kwargs['mask'] = (q.get('mask'),)
    if q.__contains__('color'):
        kwargs['color'] = [float(v) for v in (q.get('color')).split(',')]
    if q.__contains__('size'):
        kwargs['size'] = [int(v) for v in (q.get('size')).split(',')]
    if q.__contains__('rotate'):
        kwargs['rotate'] = (int(q.get('rotate')),)
    if q.__contains__('shadow_height'):
        kwargs['shadow_height'] = (int(q.get('shadow_height')),)
    if q.__contains__('force'):
        kwargs['force'] = True

    #get absolute filename of symbol, crashes if symbol does not exist

    #enable this for debugging
    #set_console_logger()
    sm = SymbolManager(settings.SYMBOLS_DIR)
    filename_abs = sm.get_symbol_transformed(symbol, **kwargs)
    f = open(filename_abs, 'rb')
    result_bin = f.read()
    f.close()

    #generate response
    response = HttpResponse(result_bin)
    response['Content-type'] = 'image/png'
    return response


def legend_shapedata(request):
    """Draws a ShapeDataLegend

    input: GET['object_id']: ShapeDataLegend.id
    output: png image of the legend
    """

    ## FIRST check if this is a new style grid, with dynamic legend
    presentationlayer_id = request.GET.get('presentationlayer_id')
    # Hack -- object_id really means legend id, but sometimes the
    # presentationlayer_id is passed in that way (because I do that
    # explictly in NPyramidOverlay.js, but I don't know why
    # presentationlayer_id isn't passed in in the first place)
    if presentationlayer_id is None:
        presentationlayer_id = request.GET.get('object_id')

    if presentationlayer_id:
        try:
            presentationlayer = PresentationLayer.objects.get(
                pk=presentationlayer_id)
            result = pyramids.get_result_by_presentationlayer(
                presentationlayer)
            if result:
                # Handle these elsewhere, dynamic
                template_variables = pyramids.result_legend(
                    result, presentationlayer,
                    request.GET.get('colormap'), request.GET.get('maxvalue'))
                return render(
                    request,
                    'visualization/legend_shapedata_grid.html',
                    template_variables)
        except PresentationLayer.DoesNotExist:
            pass

    # No, it's not, continue in the old way

    shapedatalegend = get_object_or_404(
        ShapeDataLegend, pk=request.GET['object_id'])
    geo_type = shapedatalegend.presentationtype.geo_type

    if geo_type == PresentationType.GEO_TYPE_POINT:
        sm = SymbolManager(settings.SYMBOLS_DIR)
        mpl = MapnikPointLegend(shapedatalegend, sm)
        title, blocks = mpl.get_legend_data()

        return render(
            request,
            'visualization/legend_shapedata_point.html',
            {'title': title, 'blocks': blocks})

    elif geo_type == PresentationType.GEO_TYPE_LINE:
        if shapedatalegend.id in [20]:
            legend_data = [(100, '005bff'),
                          (500, '00ebff'),
                           (1000, '4dff00'),
                           (5000, 'fff100'),
                           (20000, 'ff4100')]

            return render(
                request,
                'visualization/legend_shapedata_grid.html',
                {'title': shapedatalegend.name,
                 'content': legend_data})
        else:
            sm = SymbolManager(settings.SYMBOLS_DIR)
            mpl = MapnikPointLegend(shapedatalegend, sm)
            title, blocks = mpl.get_legend_data()

            return render(
                request,
                'visualization/legend_shapedata_point.html',
                {'title': title, 'blocks': blocks})

    elif geo_type == PresentationType.GEO_TYPE_POLYGON:
        sm = SymbolManager(settings.SYMBOLS_DIR)
        mpl = MapnikPointLegend(shapedatalegend, sm)
        title, blocks = mpl.get_legend_data()

        return render(
            request,
            'visualization/legend_shapedata_point.html',
            {'title': title, 'blocks': blocks})

    elif geo_type in (PresentationType.GEO_TYPE_GRID,
                      PresentationType.GEO_TYPE_PYRAMID):
        try:
            pl = get_object_or_404(
                PresentationLayer, pk=request.GET['presentationlayer_id'])
            file_location = (
                pl.presentationgrid.png_default_legend.file_location)
            file_folder = file_location[:file_location.rfind('\\')]
            color_mapping = file_folder + '\colormapping.csv'

            f = open(external_file_location(color_mapping), 'rb')
            try:
                reader = list(csv.DictReader(f))
                legend_data = [
                    (float(r['leftbound']), r['colour']) for r in reader]
            finally:
                f.close()
        except:
            legend_data = []

        return render(
            request,
            'visualization/legend_shapedata_grid.html',
            {'title': shapedatalegend.name,
             'content': legend_data})


def uber_service(request):
    """Collection of all available services.

    This function calls the actual functions
    """
    q = request.GET
    action = q.get('action').lower()
    if action == 'get_symbol':
        symbol = q['symbol']
        return get_symbol(request, symbol)
    elif action == 'get_legend_shapedata':
        return legend_shapedata(request)

    raise Http404


def testmapping(request):
    shapedatalegend = get_object_or_404(ShapeDataLegend, pk=1)
    sm = SymbolManager(settings.SYMBOLS_DIR)
    mpl = MapnikPointLegend(shapedatalegend, sm)
    #mapnik_rules = mpl.get_rules()

    result = '%s %s %s' % (mpl.get_rule_name({'value': 0.0}),
                           mpl.get_rule_name({'value': 1.0}),
                           mpl.get_rule_name({'value': 20.0}),)

    return HttpResponse(result)
