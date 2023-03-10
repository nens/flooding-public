/*************************************************************/
/**** description: Load the Flooding application            */
/****                                                        */
/*************************************************************/

var loadFloodingApp = function () {
    console.log('loading Flooding Application');
    var flooding = new NApp("Lizard Flooding",{
        id: "flooding",
        description: "overstromingsinformatie",
        defaultSubAppId: "floodingResults",

        onInit:function() {},
        onShow:function() {},
        onHide:function() {}
    });

    // Create Flooding
    var flooding_result = new NApp(ST_RESULTS ,{
        id: "floodingResults",
        description: "resultaten overstromings informatie bekijken",
        screenType: MAP,
        combMapData:true,

        navigation: new NNavigation({ initFunction: "frNavigation"}),
        infoWindowContainer: new NInfoWindowContainer({ initFunction: "frInfoWindowSettings"}),
        overlayContainer: new NOverlayContainer({ initFunction: "frOverlaySettings"}),
        toolbar: new NToolbar({ initFunction: "frToolbarSettings"}),
        overlayManager: new NOverlayManager(map, {prefixPngLocation: lizardKbFloodPngDirectory}),

        onInit:function() {},
        onShow:function() {
            try {
                region_layers_results.addOverlays();
            }
            catch (e) {}
        },
        onUnselect:function() {
            cancelLayerControls();
            try {
                region_layers_results.removeOverlays();
            }
            catch (e) {}
        }
    });

    var flooding_table = new NApp(ST_TABLE,{
        id: "floodingTable",
        description: "overstromings informatie",

        screenType: IFRAME,
        url:'flooding/scenario/',

        onInit:function() {},
        onShow:function() {},
        onHide:function() {}
    });

    var flooding_import = new NApp(ST_IMPORT,{
        id: "floodingImport",
        description: "importeren scenario gegevens",

        screenType: IFRAME,
        url:'flooding/tools/import/',

        onInit:function() {},
        onShow:function() {},
        onHide:function() {}
    });

    var flooding_export = new NApp(ST_EXPORT,{
        id: "floodingExport",
        description: "exporteren voor genereren waterkaart",

        screenType: IFRAME,
        url:'flooding/tools/export/',

        onInit:function() {},
        onShow:function() {},
        onHide:function() {}
    });

    var flooding_gdmap = new NApp(ST_GDMAP,{
        id: "floodingGDMap",
        description: "beheren van gebiedsdekkende kaarten",

        screenType: IFRAME,
        url:'flooding/tools/gdmap/',

        onInit:function() {},
        onShow:function() {},
        onHide:function() {}
    });

    flooding.addSubApps([
        flooding_result,
        flooding_table,
        flooding_import,
        flooding_export,
        flooding_gdmap
    ]);

    return flooding;
};
