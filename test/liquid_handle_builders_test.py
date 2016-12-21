import unittest
from autoprotocol.liquid_handle_builders import *


class LiquidHandleBuilder(unittest.TestCase):

    def test_shape_builder(self):
        with self.assertRaises(TypeError):
            shape_builder(rows="1")
        with self.assertRaises(TypeError):
            shape_builder(columns="1")

        with self.assertRaises(ValueError):
            shape_builder(format="SBS24")

    def test_location_builder(self):
        with self.assertRaises(TypeError):
            location_builder(location=1)
        with self.assertRaises(TypeError):
            location_builder(cycles="1")
        with self.assertRaises(TypeError):
            location_builder(transports=dict())
        with self.assertRaises(TypeError):
            location_builder(x_object_volume="1:ul")

        with self.assertRaises(ValueError):
            location_builder(transports=[])
        with self.assertRaises(ValueError):
            location_builder(cycles=0)

    def test_transport_builder(self):
        with self.assertRaises(TypeError):
            transport_builder(volume="1")
        with self.assertRaises(TypeError):
            transport_builder(flowrate="1")
        with self.assertRaises(TypeError):
            transport_builder(delay_time="1")
        with self.assertRaises(TypeError):
            transport_builder(mode_params="1")
        with self.assertRaises(TypeError):
            transport_builder(x_calibrated_volume="1")

    def test_flowrate_builder(self):
        with self.assertRaises(TypeError):
            flowrate_builder(target="1")
        with self.assertRaises(TypeError):
            flowrate_builder(initial="1")
        with self.assertRaises(TypeError):
            flowrate_builder(cutoff="1")
        with self.assertRaises(TypeError):
            flowrate_builder(x_acceleration="1")
        with self.assertRaises(TypeError):
            flowrate_builder(x_deceleration="1")

    def test_mode_params_builder(self):
        with self.assertRaises(TypeError):
            mode_params_builder(liquid_class=1)
        with self.assertRaises(TypeError):
            mode_params_builder(tip_x="1")
        with self.assertRaises(TypeError):
            mode_params_builder(tip_y="1")
        with self.assertRaises(TypeError):
            mode_params_builder(tip_z="1")

        with self.assertRaises(ValueError):
            mode_params_builder(liquid_class="DMSO")
        with self.assertRaises(ValueError):
            mode_params_builder(tip_x=2)
        with self.assertRaises(ValueError):
            mode_params_builder(tip_y=-2)

    def test_z_position_builder(self):
        with self.assertRaises(TypeError):
            z_position_builder(reference=1)
        with self.assertRaises(TypeError):
            z_position_builder(offset=1)
        with self.assertRaises(TypeError):
            z_position_builder(detection_method=1)
        with self.assertRaises(TypeError):
            z_position_builder(fallback=1)

        with self.assertRaises(ValueError):
            z_position_builder(reference="well_middle")
        with self.assertRaises(ValueError):
            z_position_builder(detection_duration=Unit("5:s"))
        with self.assertRaises(ValueError):
            z_position_builder(reference="well_top",
                               detection_method="tracked")
