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

### Base Layers

The project tab in QCity includes an `Add base layers` dropdown menu situated below the `Load QCity Package` button. Once configured, this `Add base layers` dropdown allows you to quickly add spatial data to your QGIS project. In order to populate this menu a QGIS project is required to be configured in a folder for each menu entry.

![Base_Layers_Diagram](https://github.com/user-attachments/assets/430892ec-8beb-4b81-ad95-0f885f72cabb)

Each entry in the `Add base layers` dropdown corresponds to a separate QGIS project in the base layers folder. It is advised to store the QGIS projects and spatial data in a central location with adequate privileges to allow multiple users to access the base layers.

![Base_Layers_Folder](https://github.com/user-attachments/assets/d3fe4c08-f929-4005-a706-3aa35fab2995)

> Note: The creation of the QGIS projects and folder in a central location will need to be completed by a person with adequate permissions such as a GIS analyst.

Once the QGIS projects are created with the spatial data, you need to point QCity to the locaton of the folder. To do this left click on `Settings` and then left click on `Options` in the menu.

![Base_Layers_Settings_Menu](https://github.com/user-attachments/assets/bc0520be-1695-4c13-b138-d080b59ca1c3)

Left click on `Advanced` in the left hand panel. Disable the check box `Use new settings tree widget (some settings will be missing)` by left clicking on the checkbox. Then left click on `I will be careful, I promise!`.

![Base_Layers_Settings_Advanced](https://github.com/user-attachments/assets/9d241e97-ac10-4bf7-b7a1-d17bf4336740)

Scroll down to `plugins` and expand the list by left clicking on the triangle to the left of the `plugins` entry. Expand the `qcity` entry by left clicking on the triangle to the left of the `qcity` entry. Add the full path to the folder which contains the QGIS base layers projects.

![Base_Layers_Folder_Path](https://github.com/user-attachments/assets/2885566d-0621-4c9c-bf48-a18dcf277f25)

Left click on `Ok` and restart QGIS. Once QGIS is restarted the `Add base layers` dropdown will be populated.

![Base_Layers_Dropdown](https://github.com/user-attachments/assets/ddb7188d-819c-42b1-880e-d582bff4d7f8)

Left click on the base layer you want to add to your project and then left click on the `Load selected base layers` button to the right hand side of the `Add base layers` dropdown. This will then add the layers configured in the QGIS project in the base layers folder to your project.

![Base_Layers_Add_Layers_Button](https://github.com/user-attachments/assets/1734ddcf-1cdf-4a36-af8d-f9d38e341efe)

> For system admininstrators, the base layers configuration can be automated (e.g. for use in QGIS deployment scripts) via a Python command:
> `QgsSettings().setValue('plugins/qcity/base_project_folder', 'c:/path/to/project/folder')`

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

Once digitizing the polygon has been completed, a window will appear requiring a project area name to be provided.

![Project_Settings_Add_Project_Name](https://github.com/user-attachments/assets/841e7051-0750-4c85-a3d9-abc3728f3aa6)

### Deleting a Project Area

A project area can be deleted by left clicking on the project area in the Project Setup panel and left clicking on the red minus button on the right hand side of the project areas panel.

![Project_Settings_Remove_Project_Area](https://github.com/user-attachments/assets/3b469dd4-cc16-4f15-99ea-09bf160e7908)

**Caution: Deleting a project area will also delete any associated development sites and building levels.**

### Renaming a Project Area

A project area can be renamed by left clicking on the project area in the Project Setup panel and left clicking on the pencil and paper button on the right hand side of the project areas panel.

![Project_Settings_Rename_Project_Area](https://github.com/user-attachments/assets/4ea00ba2-a6e5-499e-9432-a9999ac81cb0)

A new window will open which will allow you to rename the project area.

![Project_Area_Rename_Window](https://github.com/user-attachments/assets/111caf57-77cd-4d12-8048-fbc733dde0bb)

> Should a name already be used, QCity will warn you that the name already exists and will not allow you to reuse it.

## Development Sites

Each development site has the following settings that can be configured:

1. General Details
2. Development Statistics
3. Car Parking Statistics
4. Bike Parking Statistics

### Relation to Project Area

The `Development Sites` tab includes the name of the project area which it is associated with under the development sites heading. This provides you with an indication which project area you are creating the development site within.

![Development_Sites_Heading](https://github.com/user-attachments/assets/c0f7d230-d567-4109-a28d-bedaa6c459db)

Should you digitize a development site outside of the project area boundary, QCity will present a warning that the development site is outside of the spatial extent of the project area.

![Development_Sites_Warning_Spatial_Extent](https://github.com/user-attachments/assets/76a03016-7926-4b65-b160-3f1ba4901bf8)

> The development site is linked to the project area that is selected in the projects tab. When working with multiple project areas, always ensure you check the header of the development sites tab to see which project area it is associated with.

### Creating a Development Site

To create a new development site, left click on the green + button on the right hand side of the development sites panel.

![Development_Site_Create](https://github.com/user-attachments/assets/aa1c15d7-6148-49d9-8924-24eb75726415)

Then left click on the map area to start creating a polygon. Keep left clicking to create more points in the polygon and then right click to finish digitizing the polygon.

Once digitizing the polygon has been completed, a window will appear requiring a development site name to be provided.

![Development_Site_Name](https://github.com/user-attachments/assets/96f33afe-954c-4a3b-9c54-c84804c5e79b)

### Creating a Development Site - Snapping

When creating new development sites, often the boundaries correspond to existing cadastral boundaries. In order to digitize a development site to the boundaries of cadastral lots or other features, snapping needs to be enabled.

Snapping options are available in the QGIS Snapping toolbar.

![Snapping_Toolbar](https://github.com/user-attachments/assets/24dde987-79de-4d38-9ad8-174b0d5a77a6)

If the Snapping toolbar is not visible, left click on `View`, hover the cursor over `Toolbars` and left click on `Snapping Toolbar` to enable the Snapping Toolbar.

![Snapping_Toolbar_Checkbox](https://github.com/user-attachments/assets/02a301ef-8b03-4026-bdcf-c4fefc95e0dd)

To enable snapping, left click on the `Enable Snapping` button on the Snapping Toolbar which appears as a red magnet.

![Enable_Snapping](https://github.com/user-attachments/assets/ecf75a98-b8c5-46ba-8391-d4113eae3c6c)

To enable snapping to a specific layer, left click on the snapping options dropdown icon situated to the right of the `Enable Snapping` button. Left click on the `Advanced Configuration`.

![Snapping_Options_Menu](https://github.com/user-attachments/assets/e338b263-3f79-45c7-8ca7-0677c1e5617e)

Once the Snapping toolbar is set to advanced configuration, left click on the `Edit Advanced Configuration` button which appears as an eye icon. Left click on the checkbox next to the layer you would like to snap to and from the `Type` dropdown, select whether you would like to snap to vertices, segments etc.

![Snapping_Advanced_Configuration](https://github.com/user-attachments/assets/b10886f2-1eab-4a1c-a6d3-26c94ad44430)

Once snapping has been enabled, when created a new development site, you will see a purple indicator on the map canvas to snap to the desired features.

![Snapping_Indicator](https://github.com/user-attachments/assets/0120e5af-4b45-4a2a-b97c-1e9487a403f5)

> For more information on using snapping within QGIS, please see the [QGIS documentation](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#snapping-and-digitizing-options).

### Deleting a Development Site

A development site can be deleted by selecting the development site you want to delete in the development sites panel and left clicking on the red minus button on the right hand side of the development sites panel.

![Development_Sites_Delete](https://github.com/user-attachments/assets/7ce818b2-044e-4bec-9104-ed6bfb2aac63)

**Caution: Deleting a development site will also delete any associated building levels.**

### Renaming a Development Site

A development site can be renamed by selecting the development site you want to rename in the development sites panel and left clicking on the pencil and paper button on the right hand side of the development sites panel.

![Development_Site_Rename](https://github.com/user-attachments/assets/40c66d57-053c-4df0-8b29-2821c7e5b572)

A new window will open which will allow you to rename the development site.

![Development_Site_Rename_Window](https://github.com/user-attachments/assets/5139b1b6-111b-4e1f-b125-628ceaed7e66)

> Should a name already be used, QCity will warn you that the name already exists and will not allow you to reuse it.

### General Details

The general details section of the developent sites tab allows you to input the following:

1. Location (Address)
2. Status - Drop down list including:
    1. `Constructed` for modeling of development sites already constructed
    2. `Proposed` for development sites where an approval has been issued but no construction has commenced
    3. `Modeled` for development sites which are hypothetical developments yet to occur
3. Year - The year of construction, approval or anticipated construction date
4. Owner - Owner of the development site

### Development Statistics

The development statistics are set to automatically calculate floorspace and dwelling yield by default. The values are calculated from the building levels associated with the development sites. Should you wish to model an already constructed or approved building, untick the `Automatically calculate floorspace` checkbox and input the floorspace and dwelling values for the development site manually.

![Development_Statistics_Manual_Configuration](https://github.com/user-attachments/assets/f31925c1-baeb-4748-bdac-c0a981786125)

> Modeling the commercial floorspace and dwelling yield for already constructed or approved developments does not need the building levels to be modeled in order for QCity to aggregate the data. The building levels are only required to be created for constructed or approved development sites if you wish to visualize the development in a map.

### Car Parking Statistics

The car parking statistics are set to automatically calculate the number of car parking bays for the development site by default. The values are calculated from the commercial and office floorspace and number of dwellings from the building levels and the parking ratios set in the [project settings](#project-settings). Should you wish to model an already constructed or approved building, untick the `Automatically calculate car parking` check box and input the number of commercial, office and residential bays for the development site manually.

![Car_Parking_Statistics_Manual_Configuration](https://github.com/user-attachments/assets/f4d335ef-3e08-4f67-9fd8-b68b419fdf00)

> Modeling the car parking bays for already constructed or approved developments does not need the building levels to be modeled in order for QCity to aggregate the data. The building levels are only required to be created for constructed or approved development sites if you wish to visualize the development in a map.

### Bike Parking Statistics

The bike parking statistics are set to automatically calculate the number of bike parking bays for the development site by default. The values are calculated from the commercial and office floorspace and number of dwellings from the building levels and the parking ratios set in the [project settings](#project-settings). Should you wish to model an already constructed or approved building, untick the `Automatically calculate bicycle parking` check box and input the number of commercial, office and residential bays for the development site manually.

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

> If you would like to export the statistics for the development sites from the QGIS attribute table into a spreadsheet, you can do this by left clicking in the top left hand corner of the attribute table next to the field *fid* and using the keyboard shortcut Ctrl + C and pasting into the spreadsheet using Ctrl + V.

## Building Levels

### Relation to Development Sites

The `Building Levels` tab includes the name of the development site which it is associated with under the building levels heading. This provides you with an indication which development site you are creating the building levels within.

![Building_Levels_Heading](https://github.com/user-attachments/assets/0d2dc5cf-4044-4ec6-b265-497e85e6fb4d)

Should you digitize a building level outside of the development site boundary, QCity will present a warning that the building level is outside the spatial extent of the development site.

![Building_Levels_Warning_Spatial_Extent](https://github.com/user-attachments/assets/a6ceaf19-e5c2-4ffc-82d4-f9b86aee479c)

> The building levels are linked to the development site that is selected in the development sites tab. When working with multiple development sites, always ensure you check the header of the building levels tab to see which development site it is associated with.

### Creating a new Building Level

To create a new building level, left click on the green + button on the right hand side of the building levels panel.

![Building_Levels_Create](https://github.com/user-attachments/assets/a95d5cca-67f1-43b2-8b6c-e69bde612a68)

Then left click on the map area to start creating a polygon. Keep left clicking to create more points in the polygon and then right click to finish digitizing the polygon.

Once digitizing the polygon has been completed, a window will appear requiring a building level name to be provided.

![Building_Level_Name](https://github.com/user-attachments/assets/76cc54ca-fff8-4e16-a912-4b3520eeeaa3)

Left click on `OK` and the building level will be created.

### Creating a new Building Level - Snapping

When creating new building levels, often the boundaries correspond to the boundaries of existing features such as cadastral boundaries or development site boundaries. In order to digitize a building level to the boundaries of cadastral lots or other features, snapping needs to be enabled.

Snapping options are available in the QGIS Snapping toolbar.

![Snapping_Toolbar](https://github.com/user-attachments/assets/24dde987-79de-4d38-9ad8-174b0d5a77a6)

If the Snapping toolbar is not visible, left click on `View`, hover the cursor over `Toolbars` and left click on `Snapping Toolbar` to enable the Snapping Toolbar.

![Snapping_Toolbar_Checkbox](https://github.com/user-attachments/assets/02a301ef-8b03-4026-bdcf-c4fefc95e0dd)

To enable snapping, left click on the `Enable Snapping` button on the Snapping Toolbar which appears as a red magnet.

![Enable_Snapping](https://github.com/user-attachments/assets/ecf75a98-b8c5-46ba-8391-d4113eae3c6c)

To enable snapping to a specific layer, left click on the snapping options dropdown icon situated to the right of the `Enable Snapping` button. Left click on the `Advanced Configuration`.

![Snapping_Options_Menu](https://github.com/user-attachments/assets/e338b263-3f79-45c7-8ca7-0677c1e5617e)

Once the Snapping toolbar is set to advanced configuration, left click on the `Edit Advanced Configuration` button which appears as an eye icon. Left click on the checkbox next to the layer you would like to snap to and from the `Type` dropdown, select whether you would like to snap to vertices, segments etc.

![Snapping_Advanced_Configuration](https://github.com/user-attachments/assets/b10886f2-1eab-4a1c-a6d3-26c94ad44430)

Once snapping has been enabled, when created a new building level, you will see a purple indicator on the map canvas to snap to the desired features.

![Snapping_Indicator](https://github.com/user-attachments/assets/0120e5af-4b45-4a2a-b97c-1e9487a403f5)

> For more information on using snapping within QGIS, please see the [QGIS documentation](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#snapping-and-digitizing-options).

### Creating a new Building Level - Advanced Digitizing

When digitizing building levels you may wish to digitize with specific measurements and angles in order to create polygons with accurate setbacks and lengths. In order to digitize with this level of accuracy, you will need to use the QGIS Advanced Digitizing Tools.

#### Enabling Advanced Digitizing Tools

To enable the Advanced Digitizing Tools, left click on `View` in the top left corner of the QGIS window, hover the cursor over `Panels` menu entry and left click on `Advanced Digitizing` to enable the Advanced Digitizing panel.

![Advanced_Digitizing_Checkbox](https://github.com/user-attachments/assets/ab843c0c-7497-490f-94b0-cc32712e3335)

Once enabled, the Advanced Digitizing panel will usually open on the left hand side of the QGIS window.

![Advanced_Digitizing_Panel](https://github.com/user-attachments/assets/e515aab7-8829-43f9-b5dc-8f091819fd4c)

#### Using Advanced Digitizing Tools

To enable the Advanced Digitizing tools, left click on the green + button on the right hand side of the building levels panel to start digitizing a new building level polygon. Then before left clicking on the map area to create the first point in the polygon, left click on the `Enable Advanced Digitizing Tools` button in the Advanced Digitizing Tools panel which appears as a ruler and triangle icon.

![Advanced_Digitizing_Enable](https://github.com/user-attachments/assets/6d330d6c-a04f-4b65-8316-8f097d3fc008)

Once the Advanced Digitizing tools are enabled, you will notice that the cursor changes. Before creating the first point of the polygon, consider enabling construction mode to create a series of guides with the appropriate setbacks and wall lengths for the building level. Construction mode can be enabled by left clicking on the `Construction mode` button on the Advanced Digitizing panel which appears as a floor plan and hammer icon.

![Advanced_Digitizing_Construction_Mode](https://github.com/user-attachments/assets/8b4a0844-887c-415d-9563-8eb4e6f8c22d)

A drop down menu in the `Construction mode` button allows you to:

1. Record the construction guides
2. Show or hide the construction guides
3. Snap to the visible construction guides
4. Clear the construction guides completely

> The construction mode can also be enable and disabled with the keyboard shortcut `c` when using the Advanced Digitizing tools.

Begin creating a new building level polygon by left clicking on the map area. With the Advanced Digitizing tools enabled, you can input the distance and angle you would like to create the first length of the polygon.

![Advanced_Digitizing_Distance_and_Angle](https://github.com/user-attachments/assets/e3a1d9c5-46d7-45d5-a473-7c3f6d3ce7ec)

Once you had created the first point of the polygon, enter the distance and angle and left click again to create the next point. Repeat this process and right click to finish the polygon. Once you complete the building level polygon, a window will appear asking for a name of the building level polygon as outlined in [Creating a Building Level](#creating-a-new-building-level).

> For more information on the QGIS Advanced Digitizing tools, please see the [QGIS Documentation](https://docs.qgis.org/latest/en/docs/user_manual/working_with_vector/editing_geometry_attributes.html#the-advanced-digitizing-panel)

### Deleting a Building Level

A building level can be deleted by selecting the building level you want to delete in the building levels panel and left clicking on the red minus button on the right hand side of the building levels panel.

![Building_Levels_Delete](https://github.com/user-attachments/assets/ce491c6e-06ab-4b2f-ab2b-57f62fb7ec5d)

### Renaming a Building Level

A building level can be renamed by selecting the building level you want to rename in the building level panel and left clicking on the pencil and paper button on the right hand side of the building level panel.

![Building_Levels_Rename](https://github.com/user-attachments/assets/9ef4b78b-435b-463a-ab98-c4caa03acc2a)

A new window will open which will allow you to rename the building level.

![Building_Levels_Rename_Window](https://github.com/user-attachments/assets/19041748-6279-4691-a72a-d2edc6a3a549)

> Should a name already be used, QCity will warn you that the name already exists and will not allow you to reuse it.

### Changing the order of Building Levels

The order of building levels in the building levels panel can be changed by left clicking on the up and down arrow buttons on the right hand side of the building levels panel.

![Building_Levels_Reorder](https://github.com/user-attachments/assets/ad252a6c-95cf-440e-b771-a78ee6c4f790)

Reordering the building levels in the building levels panel will also change their position in the 3D map. In the below image the ground level has been moved to the top of the list and now is at the top of the building when viewed in 3D.

![Building_Levels_Reorder_3D](https://github.com/user-attachments/assets/79634037-b665-4cf2-9cd2-1086495c4b1f)

### Level Composition

For each building level there is a Level Composition section of the panel which allows you to specify the percentage of commercial, office and residential floor space for that building level. Each building level can have a different level composition. For the residential floorspace, this is further broken down into the percentage of the **residential floorspace** that is used for 1 bedroom, 2 bedroom, 3 bedroom and 4+ bedroom dwellings. A total percentage figure is provided which will turn red if the percentage exceeds 100%.

If the `Automatically calculate floorspace`, `Automatically calculate car parking` and `Automatically calculate bicycle parking` are enabled for the development site, changes to the level composition will automatically recalculate the floorspace, dwelling yield and parking numbers. This will use the dwelling sizes and parking rates specified in the ![Project Settings](#project-settings).

The level composition section of the building levels panel also includes the following:

1. Floor number - This represents the building level when viewed in 3D with floor number 1 being the lowest floor in the 3D building. Moving the building level up and down will automatically change this value.
2. Floor level - This represents the floor level of the building level which is dependent on the floor heights and levels of the building levels beneath it.
3. Floor height - This represents the height of the building level in 3D and will impact the floor level of the building levels above it. Changing the floor height will change the floor level of building levels above.

![Building_Levels_composition](https://github.com/user-attachments/assets/8501c1f7-0520-4a64-aeb8-9af5aae640c6)

### Unallocated Residential Floorspace

At the bottom of the building levels panel is the Unallocated Residential Floorspace table. Often when modeling dwellings in a building the calculations will result in some left over area. The Unallocated Residential Floorspce table shows the following information:

1. Dwelling size specified in the ![Project Settings](#project-settings).
2. Yield for each dwelling type from the allocated floorspace in the building level.
3. Unallocated area for each dwelling type and a total unallocated area for the building level. If the unallocated area is more than the size of certain dwelling types (1 bedroom, 2 bedroom etc) you may want to consider adjusting the percentage allocated to each dwelling type in the Level Composition to get a more optimal dwelling yield.

![Building_Levels_Unallocated_Residential_Floorspace](https://github.com/user-attachments/assets/ff5c147c-8adf-4171-8049-62127e41da02)

## Statistics

The 4th tab in QCity is the Statistics tab. This tab shows the development statistics for each project area and lets you export the data to view in an application such as a spreadsheet.

At the top of the Statistics tab is a drop down menu which lists all the project areas in the QCity package. Left click on the project area you want to see the statistics for.

![Statistics_Project_Drop_Down](https://github.com/user-attachments/assets/5a74fed1-a4ed-4018-97bd-91dfb57589d3)

Below this drop down menu are two buttons as follows:

1. `Update` - updates the statistics for the project area. This button will change to a red font `Requires update` when the data in the Statistics tab is out of date with changes to the data. Left clicking on the `Requires Update` button will update the statistics for the project area.
2. `Export` - Exports the data for the project area to a csv format which can then be imported into an application such as a spreadsheet. Left click on the `Export` button to export the data. This will open the operating system save dialog which will enable you to save the csv to the desired location.

![Statistics_Requires_Update](https://github.com/user-attachments/assets/12b6c2ee-ba42-4510-886f-1bc6bb7a6502)

Below the `Update` and `Export` buttons are the development statistics, car parking statistics and bike parking statistics. These statistics are generated from the project area, development sites and building levels data and will be automatically updated when the `Update` button is left clicked.

![Statistics](https://github.com/user-attachments/assets/01382af4-b278-4690-a5b0-abbe199916ff)
