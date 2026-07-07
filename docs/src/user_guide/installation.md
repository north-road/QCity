# Installing QCity

To install QCity, open the QGIS **Plugin Manager** by clicking on the top menu `Plugins` &rarr; `Manage and Install Plugins`.

![QGIS_Plugin_Menu](https://github.com/user-attachments/assets/3c2d6b9c-7709-47e6-98e4-ee28590b809c)

<!-- Remove the experimental sections of this documentation once QCity is no longer marked as experimental. -->

In the dialog that opens, left click on `Settings` and left click on the `Show also Experimental Plugins`.

![Plugin_Experimental_Toggle](https://github.com/user-attachments/assets/d57d277d-bfac-4d5a-ac5c-c6712fc7b89f)

> QCity is marked as experimental until version 1.0 is released. Current builds of QCity are hardcoded to a projection of EPSG: 7844 and therefore only usable in Australia. Future development in the lead up to version 1.0 will enable QCity to be used in other projections.

Left click on `All` in the side panel and type *QCity* in the search bar.

In the middle panel, click on *QCity* and then click on `Install Experimental Plugin`.

![Plugin_Install](https://github.com/user-attachments/assets/99a83d51-f73d-4143-a1f4-05ebee580033)

The Plugin Manager will then install QCity for you. When the installation is complete, click on `Close`.

> Any further updates to QCity will be available to you within the Plugin Manager.

Once installed, QCity will appear as an icon in the Plugins Toolbar.

![Plugin_Toolbar](https://github.com/user-attachments/assets/f182d732-955a-494f-b4a5-adbf8de8bd6c)

If the Plugins Toolbar is not visible, right click on one of the existing toolbars and make sure the Plugins Toolbar is ticked to visible in the toolbars menu.

![Plugins_Toolbar_Visibility](https://github.com/user-attachments/assets/319fc9d7-496d-4b78-bd33-bf17258bf6b6)

Click on the QCity icon to show the QCity panel. The QCity panel can also be hidden by clicking on the QCity icon again.

![QCity_Panel_Empty](https://github.com/user-attachments/assets/b666b38d-4d79-4064-965d-b36e781c66ce)

> The QCity panel can be dragged over other panels such as the Layer Styling panel to maximize the QCity panel and present it in a tabbed interface as shown above.

## Updating QCity

Updates to **QCity** are available through the QGIS Plugin Manager and QGIS will let you know when a new version of QCity is available.

To update your version:

1. From within QGIS, open the **Plugin Manager**, by clicking on the top menu item `Plugins` &rarr; `Manage and Install Plugins`.

   ![QGIS_Plugin_Menu](https://github.com/user-attachments/assets/aa60118d-026a-4175-8102-7036299cbd7e)

2. In the left panel, click on `Upgradeable`.

3. In the middle panel, click on `QCity`. If `QCity` is not listed, then you're already running the latest release.

4. On the lower right, click on `Upgrade Plugin`. Once upgraded, click on `Close`.

> If you receive an error after the plugin updates, try restarting QGIS.
> If you still encounter an error, please raise an issue on the [QCity GitHub page](https://github.com/north-road/QCity/issues).
