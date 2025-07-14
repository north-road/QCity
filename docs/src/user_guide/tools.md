# Using QCity

## User Interface

The QCity panel is separated into 4 vertical tabs:

1. Project areas - digitizing project areas and configuring settings for each project area.
2. Development sites - digitizing development sites and setting automatic or manual calculation of development statistics.
3. Building levels - digitizing building leveles and setting floor level composition.
4. Statistics - viewing statistics for each project area and exporting statistics to csv files.

## Project Areas

QCity uses GeoPackages to store layer files. GeoPackage is an open, standards-based, platform independent and portable format for geospatial information. GeoPackages are a file format that act as a container for multiple spatial layers to be stored inside. For more information on GeoPackage, see the [GeoPackage Website](https://www.geopackage.org/).

When first opening QCity, there are two options available:

1. `New QCity Package`.
2. `Load QCity Package`.

<img width="455" height="168" alt="QCity_Project_Setup_Packages" src="https://github.com/user-attachments/assets/9f13a0ac-96ed-4ef9-90a6-a5960e6b8e4f" />

Clicking on `New QCity Package` will open the native save dialog from the operating system. Browse to the location where you would like to save the QCity data, name the QCity GeoPackage and click `Save`.

Clicking on `Load QCity Package` will open the native open dialog from the operating system. Browse to the location of an existing QCity GeoPackage and click `Open`.

### Data Structure

When a new QCity GeoPackage is created, three layers are automatically created. These layers are:

1. Building Levels.
2. Development Sites.
3. Project Areas.

These layers have relationships preconfigured so that the development sites layer can aggregate data from the building levels layer and the project area layer can aggregate data from the development sites.

<img width="1984" height="1403" alt="QCity_Layer_Data_Structure" src="https://github.com/user-attachments/assets/12613a92-d3ae-4187-b14c-5e9889ba579b" />

### Project Settings

Each project area has the following settings that can be configured:

1. Dwellings
2. Car Parking
3. Bike Parking

The dwelling sizes and parking ratios configured in the project settings will apply to all developments linked to that project area. These settings can be changed at any time by simply changing the values in each section. Changing these settings will recalculate the dwelling and parking statistics for that project area.

<img width="417" height="792" alt="Project_Settings" src="https://github.com/user-attachments/assets/b71b5510-d5cb-4cf5-b3cb-346cf89abb6f" />

### Creating A Project Area

To create a new project area, left click on the green + button on the right hand side of the project areas panel.

<img width="455" height="333" alt="Project_Settings_Add_Project_Area" src="https://github.com/user-attachments/assets/0ff09fe1-8f49-4360-9635-27d424ebfb92" />

Then left click on the map area to start creating a polygon. Keep left clicking to create more points in the polygon and then right click to finish digitizing the polygon.

Once digitizing the polygon has been completed, a window will appear require a project area name to be provided.

<img width="199" height="119" alt="Project_Settings_Add_Project_Name" src="https://github.com/user-attachments/assets/841e7051-0750-4c85-a3d9-abc3728f3aa6" />

### Deleting a Project Area

A project area can be deleted by left clicking on the project area in the Project Setup panel and left clicking on the red minus button on the right hand side of the project areas panel.

<img width="454" height="337" alt="Project_Settings_Remove_Project_Area" src="https://github.com/user-attachments/assets/3b469dd4-cc16-4f15-99ea-09bf160e7908" />

**Caution: Deleting a project area will also delete any associated development sites and building levels.**

### Renaming a Project Area

A project area can be renamed by left clicking on the project area in the Project Setup panel and left clicking on the pencil and paper button on the right hand side of the project areas panel.

<img width="454" height="337" alt="Project_Settings_Rename_Project_Area" src="https://github.com/user-attachments/assets/4ea00ba2-a6e5-499e-9432-a9999ac81cb0" />
