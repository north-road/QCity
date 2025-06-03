from enum import Enum, auto


class LayerType(Enum):
    """
    QCity layer types
    """

    ProjectAreas = auto()
    DevelopmentSites = auto()
    BuildingLevels = auto()

    def as_title_case(self, plural=False):
        """
        Returns a title-cased string representation of the object.
        """
        return {
            LayerType.ProjectAreas: "Project Areas" if plural else "Project Area",
            LayerType.DevelopmentSites: "Development Sites"
            if plural
            else "Development Site",
            LayerType.BuildingLevels: "Building Levels" if plural else "Building Level",
        }[self]

    def as_sentence_case(self, plural=False):
        """
        Returns a sentence-cased string representation of the object.
        """
        return {
            LayerType.ProjectAreas: "project areas" if plural else "project area",
            LayerType.DevelopmentSites: "development sites"
            if plural
            else "development site",
            LayerType.BuildingLevels: "building levels" if plural else "building level",
        }[self]
