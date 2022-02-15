from acdesign.aircraft import Plane, Panel, Rib


def map_fusion_rib(self: Rib, component):
    self.component = component
    self.sketch = self.component.sketches[0]


def map_fusion_panel(self: Panel, parent):
    self.component = parent.occurrences.itemByName(f"{self.name}:1").component
    self.inbd.map_fusion(self.component.occurrences.itemByName("inbd:1").component)
    self.otbd.map_fusion(self.component.occurrences.itemByName("otbd:1").component)


def map_fusion_plane(self: Plane, doc):
    self.component = doc.design.rootComponent
    for panel in self.panels:
        panel.map_fusion(self.component)

