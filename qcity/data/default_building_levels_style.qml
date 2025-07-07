<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis autoRefreshTime="0" readOnly="0" version="3.44.0-Solothurn" maxScale="0" simplifyDrawingTol="1" labelsEnabled="0" styleCategories="AllStyleCategories" autoRefreshMode="Disabled" symbologyReferenceScale="-1" hasScaleBasedVisibilityFlag="0" simplifyAlgorithm="0" minScale="100000000" simplifyLocal="1" simplifyDrawingHints="1" simplifyMaxScale="1">
  <renderer-3d layer="" type="vector">
    <vector-layer-3d-tiling show-bounding-boxes="0" zoom-levels-count="3"/>
    <symbol material_type="phong" type="polygon">
      <data invert-normals="0" extrusion-height="0" culling-mode="no-culling" offset="0" add-back-faces="0" alt-binding="centroid" alt-clamping="terrain" rendered-facade="3"/>
      <material ambient="90,90,90,255,rgb:0.3529412,0.3529412,0.3529412,1" shininess="0" opacity="1" kd="1" ks="1" specular="255,255,255,255,rgb:1,1,1,1" diffuse="160,160,160,255,rgb:0.627451,0.627451,0.627451,1" ka="1">
        <data-defined-properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data-defined-properties>
      </material>
      <data-defined-properties>
        <Option type="Map">
          <Option value="" name="name" type="QString"/>
          <Option name="properties" type="Map">
            <Option name="extrusionHeight" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="level_height" name="field" type="QString"/>
              <Option value="2" name="type" type="int"/>
            </Option>
            <Option name="height" type="Map">
              <Option value="true" name="active" type="bool"/>
              <Option value="base_height" name="field" type="QString"/>
              <Option value="2" name="type" type="int"/>
            </Option>
          </Option>
          <Option value="collection" name="type" type="QString"/>
        </Option>
      </data-defined-properties>
      <edges enabled="1" color="0,0,0,255,rgb:0,0,0,1" width="2"/>
    </symbol>
  </renderer-3d>
  <flags>
    <Identifiable>1</Identifiable>
    <Removable>1</Removable>
    <Searchable>1</Searchable>
    <Private>0</Private>
  </flags>
  <temporal accumulate="0" mode="0" enabled="0" durationField="fid" endExpression="" endField="" startField="" limitMode="0" durationUnit="min" fixedDuration="0" startExpression="">
    <fixedRange>
      <start></start>
      <end></end>
    </fixedRange>
  </temporal>
  <elevation clamping="Terrain" zscale="1" symbology="Line" zoffset="0" customToleranceEnabled="1" respectLayerSymbol="1" extrusionEnabled="1" extrusion="0" binding="Centroid" type="IndividualFeatures" showMarkerSymbolInSurfacePlots="0">
    <data-defined-properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties" type="Map">
          <Option name="ExtrusionHeight" type="Map">
            <Option value="true" name="active" type="bool"/>
            <Option value="level_height" name="field" type="QString"/>
            <Option value="2" name="type" type="int"/>
          </Option>
          <Option name="ZOffset" type="Map">
            <Option value="true" name="active" type="bool"/>
            <Option value="base_height" name="field" type="QString"/>
            <Option value="2" name="type" type="int"/>
          </Option>
        </Option>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </data-defined-properties>
    <profileLineSymbol>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="" force_rhr="0" type="line">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleLine" locked="0" id="{8de7868b-0681-4856-9938-0ef0a58627a4}">
          <Option type="Map">
            <Option value="0" name="align_dash_pattern" type="QString"/>
            <Option value="square" name="capstyle" type="QString"/>
            <Option value="5;2" name="customdash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="customdash_map_unit_scale" type="QString"/>
            <Option value="MM" name="customdash_unit" type="QString"/>
            <Option value="0" name="dash_pattern_offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="dash_pattern_offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="dash_pattern_offset_unit" type="QString"/>
            <Option value="0" name="draw_inside_polygon" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="183,72,75,255,rgb:0.7176471,0.2823529,0.2941176,1" name="line_color" type="QString"/>
            <Option value="solid" name="line_style" type="QString"/>
            <Option value="0.6" name="line_width" type="QString"/>
            <Option value="MM" name="line_width_unit" type="QString"/>
            <Option value="0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="0" name="ring_filter" type="QString"/>
            <Option value="0" name="trim_distance_end" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_end_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_end_unit" type="QString"/>
            <Option value="0" name="trim_distance_start" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="trim_distance_start_map_unit_scale" type="QString"/>
            <Option value="MM" name="trim_distance_start_unit" type="QString"/>
            <Option value="0" name="tweak_dash_pattern_on_corners" type="QString"/>
            <Option value="0" name="use_custom_dash" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="width_map_unit_scale" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileLineSymbol>
    <profileFillSymbol>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{8318db4f-35ba-46b4-b71c-db2f403e5a1a}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="183,72,75,255,rgb:0.7176471,0.2823529,0.2941176,1" name="color" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="0,0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="131,51,54,255,rgb:0.5125963,0.2016785,0.210071,1" name="outline_color" type="QString"/>
            <Option value="solid" name="outline_style" type="QString"/>
            <Option value="0.2" name="outline_width" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option value="solid" name="style" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileFillSymbol>
    <profileMarkerSymbol>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="" force_rhr="0" type="marker">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleMarker" locked="0" id="{cf02566a-8a03-4037-b362-9b9ffb8e0e9c}">
          <Option type="Map">
            <Option value="0" name="angle" type="QString"/>
            <Option value="square" name="cap_style" type="QString"/>
            <Option value="183,72,75,255,rgb:0.7176471,0.2823529,0.2941176,1" name="color" type="QString"/>
            <Option value="1" name="horizontal_anchor_point" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="diamond" name="name" type="QString"/>
            <Option value="0,0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="131,51,54,255,rgb:0.5125963,0.2016785,0.210071,1" name="outline_color" type="QString"/>
            <Option value="solid" name="outline_style" type="QString"/>
            <Option value="0.2" name="outline_width" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="outline_width_map_unit_scale" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option value="diameter" name="scale_method" type="QString"/>
            <Option value="3" name="size" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="size_map_unit_scale" type="QString"/>
            <Option value="MM" name="size_unit" type="QString"/>
            <Option value="1" name="vertical_anchor_point" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </profileMarkerSymbol>
  </elevation>
  <renderer-v2 forceraster="0" enableorderby="0" referencescale="-1" type="singleSymbol" symbollevels="0">
    <symbols>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="0" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{654a80fa-d772-4853-ae5d-1857db6add25}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="255,158,23,255,rgb:1,0.6196078,0.0901961,1" name="color" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="0,0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="35,35,35,255,rgb:0.1372549,0.1372549,0.1372549,1" name="outline_color" type="QString"/>
            <Option value="solid" name="outline_style" type="QString"/>
            <Option value="0.26" name="outline_width" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option value="solid" name="style" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </symbols>
    <rotation/>
    <sizescale/>
    <data-defined-properties>
      <Option type="Map">
        <Option value="" name="name" type="QString"/>
        <Option name="properties"/>
        <Option value="collection" name="type" type="QString"/>
      </Option>
    </data-defined-properties>
  </renderer-v2>
  <selection mode="Default">
    <selectionColor invalid="1"/>
    <selectionSymbol>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{789d779c-9723-48e6-a08b-f4cd0310bfe8}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="0,0,255,255,rgb:0,0,1,1" name="color" type="QString"/>
            <Option value="bevel" name="joinstyle" type="QString"/>
            <Option value="0,0" name="offset" type="QString"/>
            <Option value="3x:0,0,0,0,0,0" name="offset_map_unit_scale" type="QString"/>
            <Option value="MM" name="offset_unit" type="QString"/>
            <Option value="35,35,35,255,rgb:0.1372549,0.1372549,0.1372549,1" name="outline_color" type="QString"/>
            <Option value="solid" name="outline_style" type="QString"/>
            <Option value="0.26" name="outline_width" type="QString"/>
            <Option value="MM" name="outline_width_unit" type="QString"/>
            <Option value="solid" name="style" type="QString"/>
          </Option>
          <data_defined_properties>
            <Option type="Map">
              <Option value="" name="name" type="QString"/>
              <Option name="properties"/>
              <Option value="collection" name="type" type="QString"/>
            </Option>
          </data_defined_properties>
        </layer>
      </symbol>
    </selectionSymbol>
  </selection>
  <customproperties>
    <Option type="Map">
      <Option value="building_levels" name="_qcity_role" type="QString"/>
      <Option value="0" name="embeddedWidgets/count" type="int"/>
      <Option name="variableNames"/>
      <Option name="variableValues"/>
    </Option>
  </customproperties>
  <blendMode>0</blendMode>
  <featureBlendMode>0</featureBlendMode>
  <layerOpacity>1</layerOpacity>
  <geometryOptions removeDuplicateNodes="0" geometryPrecision="0">
    <activeChecks type="StringList">
      <Option value="" type="QString"/>
    </activeChecks>
    <checkConfiguration/>
  </geometryOptions>
  <legend showLabelLegend="0" type="default-vector"/>
  <referencedLayers>
    <relation strength="Association" layerId="development_sites_5d1018e5_fedb_4d41_b780_e8fbbf4de703" referencedLayer="development_sites_5d1018e5_fedb_4d41_b780_e8fbbf4de703" layerName="development_sites" dataSource="../../Temporary/QCity/perth.gpkg|layername=development_sites" referencingLayer="building_levels_b4ec6ca5_e7d2_44b0_8369_0a85bb5de10d" providerKey="ogr" id="development_sites_to_building_levels" name="development_sites_to_building_levels">
      <fieldRef referencedField="fid" referencingField="development_site_pk"/>
    </relation>
  </referencedLayers>
  <fieldConfiguration>
    <field configurationFlags="NoFlag" name="fid">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="name">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="development_site_pk">
      <editWidget type="RelationReference">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="level_index">
      <editWidget type="Range">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="level_height">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="base_height">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_commercial_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_office_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_residential_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_1_bedroom_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_2_bedroom_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_3_bedroom_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
    <field configurationFlags="NoFlag" name="percent_4_bedroom_floorspace">
      <editWidget type="TextEdit">
        <config>
          <Option/>
        </config>
      </editWidget>
    </field>
  </fieldConfiguration>
  <aliases>
    <alias index="0" field="fid" name=""/>
    <alias index="1" field="name" name=""/>
    <alias index="2" field="development_site_pk" name=""/>
    <alias index="3" field="level_index" name=""/>
    <alias index="4" field="level_height" name=""/>
    <alias index="5" field="base_height" name=""/>
    <alias index="6" field="percent_commercial_floorspace" name=""/>
    <alias index="7" field="percent_office_floorspace" name=""/>
    <alias index="8" field="percent_residential_floorspace" name=""/>
    <alias index="9" field="percent_1_bedroom_floorspace" name=""/>
    <alias index="10" field="percent_2_bedroom_floorspace" name=""/>
    <alias index="11" field="percent_3_bedroom_floorspace" name=""/>
    <alias index="12" field="percent_4_bedroom_floorspace" name=""/>
  </aliases>
  <defaults>
    <default expression="" field="fid" applyOnUpdate="0"/>
    <default expression="" field="name" applyOnUpdate="0"/>
    <default expression="" field="development_site_pk" applyOnUpdate="0"/>
    <default expression="" field="level_index" applyOnUpdate="0"/>
    <default expression="" field="level_height" applyOnUpdate="0"/>
    <default expression="" field="base_height" applyOnUpdate="0"/>
    <default expression="" field="percent_commercial_floorspace" applyOnUpdate="0"/>
    <default expression="" field="percent_office_floorspace" applyOnUpdate="0"/>
    <default expression="" field="percent_residential_floorspace" applyOnUpdate="0"/>
    <default expression="" field="percent_1_bedroom_floorspace" applyOnUpdate="0"/>
    <default expression="" field="percent_2_bedroom_floorspace" applyOnUpdate="0"/>
    <default expression="" field="percent_3_bedroom_floorspace" applyOnUpdate="0"/>
    <default expression="" field="percent_4_bedroom_floorspace" applyOnUpdate="0"/>
  </defaults>
  <constraints>
    <constraint exp_strength="0" field="fid" unique_strength="1" constraints="3" notnull_strength="1"/>
    <constraint exp_strength="0" field="name" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="development_site_pk" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="level_index" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="level_height" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="base_height" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_commercial_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_office_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_residential_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_1_bedroom_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_2_bedroom_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_3_bedroom_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
    <constraint exp_strength="0" field="percent_4_bedroom_floorspace" unique_strength="0" constraints="0" notnull_strength="0"/>
  </constraints>
  <constraintExpressions>
    <constraint field="fid" exp="" desc=""/>
    <constraint field="name" exp="" desc=""/>
    <constraint field="development_site_pk" exp="" desc=""/>
    <constraint field="level_index" exp="" desc=""/>
    <constraint field="level_height" exp="" desc=""/>
    <constraint field="base_height" exp="" desc=""/>
    <constraint field="percent_commercial_floorspace" exp="" desc=""/>
    <constraint field="percent_office_floorspace" exp="" desc=""/>
    <constraint field="percent_residential_floorspace" exp="" desc=""/>
    <constraint field="percent_1_bedroom_floorspace" exp="" desc=""/>
    <constraint field="percent_2_bedroom_floorspace" exp="" desc=""/>
    <constraint field="percent_3_bedroom_floorspace" exp="" desc=""/>
    <constraint field="percent_4_bedroom_floorspace" exp="" desc=""/>
  </constraintExpressions>
  <expressionfields/>
  <attributeactions>
    <defaultAction key="Canvas" value="{00000000-0000-0000-0000-000000000000}"/>
  </attributeactions>
  <attributetableconfig sortExpression="" actionWidgetStyle="dropDown" sortOrder="0">
    <columns>
      <column name="fid" width="-1" hidden="0" type="field"/>
      <column name="name" width="-1" hidden="0" type="field"/>
      <column name="development_site_pk" width="-1" hidden="0" type="field"/>
      <column name="level_index" width="-1" hidden="0" type="field"/>
      <column name="level_height" width="-1" hidden="0" type="field"/>
      <column name="base_height" width="-1" hidden="0" type="field"/>
      <column name="percent_commercial_floorspace" width="-1" hidden="0" type="field"/>
      <column name="percent_office_floorspace" width="-1" hidden="0" type="field"/>
      <column name="percent_residential_floorspace" width="-1" hidden="0" type="field"/>
      <column name="percent_1_bedroom_floorspace" width="-1" hidden="0" type="field"/>
      <column name="percent_2_bedroom_floorspace" width="-1" hidden="0" type="field"/>
      <column name="percent_3_bedroom_floorspace" width="-1" hidden="0" type="field"/>
      <column name="percent_4_bedroom_floorspace" width="-1" hidden="0" type="field"/>
      <column width="-1" hidden="1" type="actions"/>
    </columns>
  </attributetableconfig>
  <conditionalstyles>
    <rowstyles/>
    <fieldstyles/>
  </conditionalstyles>
  <storedexpressions/>
  <editform tolerant="1"></editform>
  <editforminit/>
  <editforminitcodesource>0</editforminitcodesource>
  <editforminitfilepath></editforminitfilepath>
  <editforminitcode><![CDATA[# -*- coding: utf-8 -*-
"""
QGIS forms can have a Python function that is called when the form is
opened.

Use this function to add extra logic to your forms.

Enter the name of the function in the "Python Init function"
field.
An example follows:
"""
from qgis.PyQt.QtWidgets import QWidget

def my_form_open(dialog, layer, feature):
    geom = feature.geometry()
    control = dialog.findChild(QWidget, "MyLineEdit")
]]></editforminitcode>
  <featformsuppress>0</featformsuppress>
  <editorlayout>generatedlayout</editorlayout>
  <editable>
    <field name="base_height" editable="1"/>
    <field name="development_site_pk" editable="1"/>
    <field name="fid" editable="1"/>
    <field name="level_height" editable="1"/>
    <field name="level_index" editable="1"/>
    <field name="name" editable="1"/>
    <field name="percent_1_bedroom_floorspace" editable="1"/>
    <field name="percent_2_bedroom_floorspace" editable="1"/>
    <field name="percent_3_bedroom_floorspace" editable="1"/>
    <field name="percent_4_bedroom_floorspace" editable="1"/>
    <field name="percent_commercial_floorspace" editable="1"/>
    <field name="percent_office_floorspace" editable="1"/>
    <field name="percent_residential_floorspace" editable="1"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="0" name="base_height"/>
    <field labelOnTop="0" name="development_site_pk"/>
    <field labelOnTop="0" name="fid"/>
    <field labelOnTop="0" name="level_height"/>
    <field labelOnTop="0" name="level_index"/>
    <field labelOnTop="0" name="name"/>
    <field labelOnTop="0" name="percent_1_bedroom_floorspace"/>
    <field labelOnTop="0" name="percent_2_bedroom_floorspace"/>
    <field labelOnTop="0" name="percent_3_bedroom_floorspace"/>
    <field labelOnTop="0" name="percent_4_bedroom_floorspace"/>
    <field labelOnTop="0" name="percent_commercial_floorspace"/>
    <field labelOnTop="0" name="percent_office_floorspace"/>
    <field labelOnTop="0" name="percent_residential_floorspace"/>
  </labelOnTop>
  <reuseLastValue>
    <field reuseLastValue="0" name="base_height"/>
    <field reuseLastValue="0" name="development_site_pk"/>
    <field reuseLastValue="0" name="fid"/>
    <field reuseLastValue="0" name="level_height"/>
    <field reuseLastValue="0" name="level_index"/>
    <field reuseLastValue="0" name="name"/>
    <field reuseLastValue="0" name="percent_1_bedroom_floorspace"/>
    <field reuseLastValue="0" name="percent_2_bedroom_floorspace"/>
    <field reuseLastValue="0" name="percent_3_bedroom_floorspace"/>
    <field reuseLastValue="0" name="percent_4_bedroom_floorspace"/>
    <field reuseLastValue="0" name="percent_commercial_floorspace"/>
    <field reuseLastValue="0" name="percent_office_floorspace"/>
    <field reuseLastValue="0" name="percent_residential_floorspace"/>
  </reuseLastValue>
  <dataDefinedFieldProperties/>
  <widgets/>
  <previewExpression>"name"</previewExpression>
  <mapTip enabled="1"></mapTip>
  <layerGeometryType>2</layerGeometryType>
</qgis>
