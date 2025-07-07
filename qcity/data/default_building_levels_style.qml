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
  <renderer-v2 attr="level_index" forceraster="0" enableorderby="0" referencescale="-1" type="categorizedSymbol" symbollevels="0">
    <categories>
      <category label="1" uuid="{85c8e030-223f-4436-aabd-0ddb70d5d8c6}" symbol="0" value="1" type="long" render="true"/>
      <category label="2" uuid="{49d1f7b8-ac46-46a9-9048-d862e1bf7e96}" symbol="1" value="2" type="long" render="true"/>
      <category label="3" uuid="{0e3e8aad-5ec3-437b-81bb-b4c6c4509877}" symbol="2" value="3" type="long" render="true"/>
      <category label="4" uuid="{0e785622-6e78-4565-8801-d9a11177d6cd}" symbol="3" value="4" type="long" render="true"/>
      <category label="5" uuid="{3ff076ba-333e-46ba-ae77-d65e4fef6054}" symbol="4" value="5" type="long" render="true"/>
      <category label="6" uuid="{1eb32a0c-dab1-483a-a51e-24571bc07c65}" symbol="5" value="6" type="long" render="true"/>
      <category label="7" uuid="{e30416ea-f3fe-42d5-9c71-8f6e1495e568}" symbol="6" value="7" type="string" render="true"/>
      <category label="8" uuid="{6623737f-3d63-44cb-a660-eb4d240c1d8c}" symbol="7" value="8" type="double" render="true"/>
      <category label="9" uuid="{8b375a12-304e-4dda-9c8e-e9c33d674271}" symbol="8" value="9" type="double" render="true"/>
      <category label="10" uuid="{02a46bde-5519-4ef7-a3c2-16a7177973fd}" symbol="9" value="10" type="double" render="true"/>
      <category label="11" uuid="{c56a4eb7-8e4b-4805-a8d0-314e849a54c9}" symbol="10" value="11" type="double" render="true"/>
      <category label="12" uuid="{f742edbc-83e8-4321-9987-51b7f09cec09}" symbol="11" value="12" type="double" render="true"/>
      <category label="13" uuid="{eeb2ef1b-adb4-4f27-928a-b0322b66d519}" symbol="12" value="13" type="double" render="true"/>
      <category label="14" uuid="{50779927-a527-4b04-92c1-b74892af1c5f}" symbol="13" value="14" type="double" render="true"/>
      <category label="15" uuid="{2f3396e5-c8ff-4397-bf08-a99d6e2eda7e}" symbol="14" value="15" type="double" render="true"/>
      <category label="16" uuid="{f3cc0432-3104-4d2b-883c-4a668c4fc27d}" symbol="15" value="16" type="double" render="true"/>
      <category label="17" uuid="{954b488a-4eed-4490-9f44-d28243fbfcf7}" symbol="16" value="17" type="double" render="true"/>
      <category label="18" uuid="{95408c6e-6bf9-4fc8-aaa2-51684a149d7c}" symbol="17" value="18" type="double" render="true"/>
      <category label="19" uuid="{1cc357bd-7589-4bd1-a17e-e9e106df31eb}" symbol="18" value="19" type="double" render="true"/>
      <category label="20" uuid="{0a6ac3f9-c103-46a8-9ccd-4042f5fe46e9}" symbol="19" value="20" type="double" render="true"/>
      <category label="21" uuid="{a4c89cff-84bd-4ac6-a3e3-2b8c8bf18b06}" symbol="20" value="21" type="double" render="true"/>
      <category label="22" uuid="{795988d5-fc7f-459e-bf79-7e1f74e084a5}" symbol="21" value="22" type="double" render="true"/>
      <category label="23" uuid="{27a34b50-edae-4570-a002-d72ca56a2174}" symbol="22" value="23" type="double" render="true"/>
      <category label="24" uuid="{a087c9b2-34aa-4796-a6ca-4eb89d947188}" symbol="23" value="24" type="double" render="true"/>
      <category label="25" uuid="{8f6ab8a7-0f4e-429e-a44b-2f8c7954b9f3}" symbol="24" value="25" type="double" render="true"/>
      <category label="26" uuid="{a70c8fe0-730b-414d-b625-a4ecb7a78e11}" symbol="25" value="26" type="double" render="true"/>
      <category label="27" uuid="{abb91b00-9bad-4bd1-86dc-c33cf6340a14}" symbol="26" value="27" type="double" render="true"/>
      <category label="28" uuid="{58348d18-e7a5-4c2f-9dce-fe858d649f4b}" symbol="27" value="28" type="double" render="true"/>
      <category label="29" uuid="{89973089-3815-4dbf-9d5a-d2d98e895546}" symbol="28" value="29" type="double" render="true"/>
      <category label="30" uuid="{d5ad8e26-9675-4fc2-948a-953d07f1f4f7}" symbol="29" value="30" type="double" render="true"/>
      <category label="" uuid="{9b36cc96-8bc7-4929-accf-5d14ccd6a927}" symbol="30" value="NULL" type="NULL" render="true"/>
    </categories>
    <symbols>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="0" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{10eef94c-d056-4f1e-9dcc-8d9a060a0aa0}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="178,232,15,255,hsv:0.20833333333333334,0.93725490196078431,0.90980392156862744,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="1" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{1f2e3e1b-2c49-4068-ade9-0df66f24a743}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="44,226,220,255,hsv:0.49444444444444446,0.80392156862745101,0.88627450980392153,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="10" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{3c6e5a97-1073-418a-a524-09eeb03b4346}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="243,166,178,255,rgb:0.9529412,0.6509804,0.6980392,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="11" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{f2ad36cc-2942-43f9-9ed2-59458985f6b5}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="114,155,111,255,rgb:0.4470588,0.6078431,0.4352941,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="12" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{7806ec2b-8ca9-4b9c-8c72-e851e6137e18}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="213,180,60,255,rgb:0.8352941,0.7058824,0.2352941,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="13" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{c429abe0-9f72-4629-a4fe-1fcef311cecc}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="164,113,88,255,rgb:0.6431373,0.4431373,0.345098,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="14" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{6d519d18-68ea-49e9-bd28-dda4ea493d5d}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="133,182,111,255,rgb:0.5215686,0.7137255,0.4352941,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="15" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{d5d5e076-6dfb-4614-baf9-f04dec4ab2be}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="125,139,143,255,rgb:0.4901961,0.545098,0.5607843,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="16" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{9aa9db30-9f08-4adf-93e2-945e92d91a3b}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="145,82,45,255,rgb:0.5686275,0.3215686,0.1764706,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="17" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{ef8c6427-7263-4e3a-b23e-c75dc46490ed}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="190,178,151,255,rgb:0.745098,0.6980392,0.5921569,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="18" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{0a16bbc2-2351-4729-bc8d-bd652e372abb}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="196,60,57,255,rgb:0.7686275,0.2352941,0.2235294,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="19" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{c0108554-5e72-463d-9c3a-a57b5315c890}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="229,182,54,255,rgb:0.8980392,0.7137255,0.2117647,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="2" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{ea0c1c80-0553-418c-a975-5d3fffaed2af}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="206,92,22,255,hsv:0.06388888888888888,0.89411764705882357,0.80784313725490198,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="20" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{9b721dd6-a125-4c88-8274-8f1f7ec828d9}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="225,89,137,255,rgb:0.8823529,0.3490196,0.5372549,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="21" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{e08615c7-1c6a-4cb4-92fc-be4afaa4d943}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="190,207,80,255,rgb:0.745098,0.8117647,0.3137255,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="22" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{c3f59ff2-b1a2-4927-8ca5-8838117c3a11}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="152,125,183,255,rgb:0.5960784,0.4901961,0.7176471,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="23" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{84d9a363-90cd-43bb-80d3-e78c28dbda02}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="231,113,72,255,rgb:0.9058824,0.4431373,0.2823529,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="24" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{f4fbe2ee-62bb-4be0-8cfd-f50e0484273d}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="183,72,75,255,rgb:0.7176471,0.2823529,0.2941176,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="25" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{441ca9cc-5c1d-4fb9-b8ab-2dfbeb7b8b60}">
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="26" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{b4e623d0-16a0-40d7-b5c2-a1d7838997fd}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="232,113,141,255,rgb:0.9098039,0.4431373,0.5529412,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="27" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{f52b172d-69e3-4e8f-9b67-b06664db9809}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="141,90,153,255,rgb:0.5529412,0.3529412,0.6,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="28" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{d4491358-78be-48e8-8760-a3e78cec734c}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="243,166,178,255,rgb:0.9529412,0.6509804,0.6980392,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="29" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{5e75371e-2f57-482b-ad8f-b18657f4c221}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="114,155,111,255,rgb:0.4470588,0.6078431,0.4352941,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="3" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{ada77895-86fe-4dab-809d-ead65e3792f9}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="177,120,205,255,hsv:0.77777777777777779,0.41568627450980394,0.80392156862745101,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="30" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{52b0caa4-5539-46d3-af13-0ec81e66536c}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="213,180,60,255,rgb:0.8352941,0.7058824,0.2352941,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="4" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{d65bf193-bee7-4963-ba1d-fb7d2aef197e}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="211,89,146,255,hsv:0.92222222222222228,0.58039215686274515,0.82745098039215681,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="5" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{57ef3dc6-8414-4c87-a97a-637956694fc9}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="129,218,139,255,hsv:0.3527777777777778,0.40784313725490196,0.85490196078431369,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="6" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{6e17ebb1-a4cf-4361-ab95-e0b68a31dc33}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="77,104,222,255,hsv:0.63611111111111107,0.65098039215686276,0.87058823529411766,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="7" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{f9d5371b-c11d-460e-b44b-5fc84e7e0a62}">
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="8" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{31786a13-9e98-41c3-b1ba-7f25a4e3fc85}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="232,113,141,255,rgb:0.9098039,0.4431373,0.5529412,1" name="color" type="QString"/>
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
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="9" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{6abb022c-635a-4657-a195-f848d4e3babf}">
          <Option type="Map">
            <Option value="3x:0,0,0,0,0,0" name="border_width_map_unit_scale" type="QString"/>
            <Option value="141,90,153,255,rgb:0.5529412,0.3529412,0.6,1" name="color" type="QString"/>
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
    <source-symbol>
      <symbol is_animated="0" clip_to_extent="1" alpha="1" frame_rate="10" name="0" force_rhr="0" type="fill">
        <data_defined_properties>
          <Option type="Map">
            <Option value="" name="name" type="QString"/>
            <Option name="properties"/>
            <Option value="collection" name="type" type="QString"/>
          </Option>
        </data_defined_properties>
        <layer pass="0" enabled="1" class="SimpleFill" locked="0" id="{821bf1be-7c2b-4749-8b60-df97137a3503}">
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
    </source-symbol>
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
    <relation strength="Association" layerId="development_sites_483b9f26_a9de_46c5_806a_dd19d060e2b0" referencedLayer="development_sites_483b9f26_a9de_46c5_806a_dd19d060e2b0" layerName="development_sites" dataSource="../../Temporary/QCity/perth.gpkg|layername=development_sites" referencingLayer="building_levels_33863393_4f5b_4fc1_8485_85a58b3f5831" providerKey="ogr" id="development_sites_to_building_levels" name="development_sites_to_building_levels">
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
