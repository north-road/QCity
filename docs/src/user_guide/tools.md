# Using QCity

## User Interface

The QCity panel is separated into 4 vertical tabs:

1. Project areas - digitizing project areas and configuring settings for each project area.
2. Development sites - digitizing development sites and setting automatic or manual calculation of development statistics.
3. Building levels - digitizing building levels and setting floor level composition.
4. Statistics - viewing statistics for each project area and exporting statistics to csv files.

## Project Areas

QCity uses GeoPackages to store layer files. GeoPackage is an open, standards-based, platform independent and portable format for geospatial information. GeoPackages are a file format that act as a container for multiple spatial layers to be stored inside. For more information on GeoPackage, see the [GeoPackage Website](https://www.geopackage.org/).

When first opening QCity, there are two options available:

1. `New QCity Package`.
2. `Load QCity Package`.

![QCity_Project_Setup_Packages](https://github.com/user-attachments/assets/9f13a0ac-96ed-4ef9-90a6-a5960e6b8e4f)

Clicking on `New QCity Package` will open the native save dialog from the operating system. Browse to the location where you would like to save the QCity data, name the QCity GeoPackage and click `Save`.

Clicking on `Load QCity Package` will open the native open dialog from the operating system. Browse to the location of an existing QCity GeoPackage and click `Open`.

### Data Structure

When a new QCity GeoPackage is created, three layers are automatically created. These layers are:

1. Building Levels.
2. Development Sites.
3. Project Areas.

These layers have relationships preconfigured so that the development sites layer can aggregate data from the building levels layer and the project area layer can aggregate data from the development sites.

![QCity_Layer_Data_Structure](https://github.com/user-attachments/assets/12613a92-d3ae-4187-b14c-5e9889ba579b)

### Project Settings

Each project area has the following settings that can be configured:

1. Dwellings
2. Car Parking
3. Bike Parking

The dwelling sizes and parking ratios configured in the project settings will apply to all developments linked to that project area. These settings can be changed at any time by simply changing the values in each section. Changing these settings will recalculate the dwelling and parking statistics for that project area.

![Project_Settings](https://github.com/user-attachments/assets/b71b5510-d5cb-4cf5-b3cb-346cf89abb6f)

### Creating A Project Area

To create a new project area, left click on the green + button on the right hand side of the project areas panel.

![Project_Settings_Add_Project_Area](https://github.com/user-attachments/assets/0ff09fe1-8f49-4360-9635-27d424ebfb92)

Then left click on the map area to start creating a polygon. Keep left clicking to create more points in the polygon and then right click to finish digitizing the polygon.

Once digitizing the polygon has been completed, a window will appear require a project area name to be provided.

![Project_Settings_Add_Project_Name](https://github.com/user-attachments/assets/841e7051-0750-4c85-a3d9-abc3728f3aa6)

### Deleting a Project Area

A project area can be deleted by left clicking on the project area in the Project Setup panel and left clicking on the red minus button on the right hand side of the project areas panel.

![Project_Settings_Remove_Project_Area](https://github.com/user-attachments/assets/3b469dd4-cc16-4f15-99ea-09bf160e7908)

**Caution: Deleting a project area will also delete any associated development sites and building levels.**

### Renaming a Project Area

A project area can be renamed by left clicking on the project area in the Project Setup panel and left clicking on the pencil and paper button on the right hand side of the project areas panel.

![Project_Settings_Rename_Project_Area](https://github.com/user-attachments/assets/4ea00ba2-a6e5-499e-9432-a9999ac81cb0)

## Development Sites

Each development site has the following settings that can be configured:

1. General Details
2. Development Statistics
3. Car Parking Statistics
4. Bike Parking Statistics

### Relation to Project Area

The development sites tab includes the name of the project area which it is associated with under the development sites heading. This provides you with an indication which project area you are creating the development site within.

![Development_Sites_Heading](https://github.com/user-attachments/assets/c0f7d230-d567-4109-a28d-bedaa6c459db)

Should you digitize a development site outside of the project area boundary, QCity will present a warning that the development site is outside of the spatial extent of the project area.

![Development_Sites_Warning_Spatial_Extent](https://github.com/user-attachments/assets/76a03016-7926-4b65-b160-3f1ba4901bf8)

> The development site is linked to the project area that is selected in the projects tab. When working with multiple project areas, always ensure you check the header of the development sites tab to see which project area it is associated with.

### Digitizing Development Sites - Snapping

When creating new development sites, often the boundaries correspond to existing cadastral boundaries. In order to digitize a development site to the boundaries of cadastral lots or other features, snapping needs to be enabled.

Snapping options are available in the Snapping toolbar.

![Snapping_Toolbar](https://github.com/user-attachments/assets/24dde987-79de-4d38-9ad8-174b0d5a77a6)

If the Snapping toolbar is not visible, left click on `View`, hover the cursor over `Toolbars` and left click on `Snapping Toolbar` to enable the Snapping Toolbar.

![Snapping_Toolbar_Checkbox](https://github.com/user-attachments/assets/02a301ef-8b03-4026-bdcf-c4fefc95e0dd)

To enable snapping, left click on the `Enable Snapping` button on the Snapping Toolbar which appears as a red magnet

![Enable_Snapping](https://github.com/user-attachments/assets/ecf75a98-b8c5-46ba-8391-d4113eae3c6c)

To enable snapping to a specific layer, left click on the snapping options dropdown icon situated to the right of the `Enable Snapping` button. Left click on the `Advanced Configuration`.

![Snapping_Options_Menu](https://github.com/user-attachments/assets/e338b263-3f79-45c7-8ca7-0677c1e5617e)

Once the Snapping toolbar is set to advanced configuration, left click on the `Edit Advanced Configuration` button which appears as an eye icon. Left click on the checkbox next to the layer you would like to snap to and from the `Type` dropdown, select whether you would like to snap to vertices, segments etc.

![Snapping_Advanced_Configuration](https://github.com/user-attachments/assets/b10886f2-1eab-4a1c-a6d3-26c94ad44430)

Once snapping has been enabled, when created a new development site, you will see a purple indicator on the map canvas to snap to the desired features.

![Snapping_Indicator](https://github.com/user-attachments/assets/0120e5af-4b45-4a2a-b97c-1e9487a403f5)

> For more information on using snapping within QGIS, please see the QGIS ![documentation](https://docs.qgis.org/3.40/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#snapping-and-digitizing-options). 

### General Details

The general details section of the developent sites tab allows you to input the following:

1. Location (Address)
2. Status - Drop down list including:
    1. `Constructed` for modeling of development sites already constructed
    2. `Proposed` for development sites where an approval has been issued but no construction has commenced
    3. `Modelled` for development sites which are hypothetical developments yet to occur
4.  Year - The year of construction, approval or anticipated construction date
5.  Owner - Owner of the development site

### Development Statistics

The development statistics are set to automatically calculate floorspace and dwelling yield by default. The values are calculated from the building levels associated with the development sites. Should you wish to model an already constructed or approved building, untick the `Automatically calculate floorspace` checkbox and input the floorspace and dwelling values for the development site manually.

![Development_Statistics_Manual_Configuration](https://github.com/user-attachments/assets/f31925c1-baeb-4748-bdac-c0a981786125)

> Modeling the commercial floorspace and dwelling yield for already constructed or approved developments does not need the building levels to be modeled in order for QCity to aggregate the data. The building levels are only required to be created for constructed or approved development sites if you wish to visualize the development in a map.

### Car Parking Statistics

The car parking statistics are set to automatically calculate the number of car parking bays for the development site by default. The values are calculated from the commercial and office floorspace and number of dwellings from the building levels and the parking ratios set in the [project settings](#Project-Settings). Should you wish to model an already constructed or approved building, untick the `Automatically calculate car parking` check box and input the number of commercial, office and residential bays for the development site manually.

![Car_Parking_Statistics_Manual_Configuration](https://github.com/user-attachments/assets/f4d335ef-3e08-4f67-9fd8-b68b419fdf00)

> Modeling the car parking bays for already constructed or approved developments does not need the building levels to be modeled in order for QCity to aggregate the data. The building levels are only required to be created for constructed or approved development sites if you wish to visualize the development in a map.

### Bike Parking Statistics

The bike parking statistics are set to automatically calculate the number of bike parking bays for the development site by default. The values are calculated from the commercial and office floorspace and number of dwellings from the building levels and the parking ratios set in the [project settings](#Project-Settings). Should you wish to model an already constructed or approved building, untick the `Automatically calculate bicycle parking` check box and input the number of commercial, office and residential bays for the development site manually.

![Bike_Parking_Statistics_Manual_Configuration](https://github.com/user-attachments/assets/9733a83f-502f-4af6-887e-17a949dbb772)

> Modeling the bike parking bays for already constructed or approved developments does not need the building levels to be modeled in order for QCity to aggregate the data. The building levels are only required to be created for constructed or approved development sites if you wish to visualize the development in a map.

### Viewing Data for Individual Development Sites

Viewing the data for each development site can done in two ways. The first is to left click on the development site in the development sites list in the development sites tab and view the data in the:

1. General Details
2. Development Statistics
3. Car Parking Statistics
4. Bike Parking Statistics

This approach is appropriate for viewing the statistics for an individual development site at a time. However, if the project area has many development sites, an alternative way to view the statistics for each development site is to use the QGIS attribute table.

To open the attribute table for the development sites layer, go to the development sites layer in the Layers panel and left click on it to select it.

![Development_Sites_Layer_Selected](https://github.com/user-attachments/assets/18f3700b-b7c7-4b16-80e7-ebde6b10647e)

If the Layers panel is not visible, left click on `View` in the top left hand corner of the QGIS window, then hover the cursor over the `Panels` entry in the menu and make sure the Layers panel checkbox is ticked. If the Layers panel is not checked, left click on it to enable the panel.

![Layers_Panel_Checkbox](https://github.com/user-attachments/assets/a2271d3d-d2b1-4629-9479-0820834ad410)

Once the development sites layer is selected, right click on the development sites layer in the Layers panel and left click on `Open Attribute Table` in the menu. This will open the attribute table for the development sites layer.

![Development_Sites_Attribute_Table](https://github.com/user-attachments/assets/db406927-2577-46c4-9895-29e48db3617e)

With the attribute table you can view the statistics for all the development sites across **all** project areas within the QCity Package.

> If you would like to export the statistics for the development sites from the QGIS attribute table into a spreadsheet, you can do this by left clicking in the top left hand corner of the attribute table next to the field *fid* and using the keyboard shortcut Ctrl + C and pasting into the spreadsheet using Ctrl + V

