from autoprotocol.util import parse_unit
from .unit import Unit
from autoprotocol import Well

_MAX_TIP_CAPACITY = dict(
    single=Unit("900:microliter"),
    multi_96=Unit("158:microliter"),
    multi_384=Unit("26.5:microliter")
)

_SUPPORTED_SHAPES = ["SBS96", "SBS384"]


def shape_builder(rows=1, columns=1, format="SBS96"):
    """
    Helper function for building a shape dictionary

    Parameters
    ----------
    rows: Int, optional
        Number of rows to be concurrently transferred
    columns: Int, optional
        Number of columns to be concurrently transferred
    format: String, optional
        Plate format in String form. Example formats are "SBS96" and "SBS384"
    Returns
    -------
    Shape parameters: Dictionary
    """
    if not isinstance(rows, int) or not isinstance(columns, int):
        raise TypeError("Rows/columns have to be of type integer")
    if format not in _SUPPORTED_SHAPES:
        raise ValueError("Invalid shape given. Shape has to be in {}".format(
            _SUPPORTED_SHAPES
        ))
    if (format == "SBS96" and (rows > 8 or columns > 12) or
            format == "SBS384" and (rows > 16 or columns > 24)):
        raise ValueError("Number of rows/columns exceed the defined format")

    arg_list = list(locals().items())
    arg_dict = {k: v for k, v in arg_list if v}
    return arg_dict


def location_builder(location=None, transports=None, cycles=None,
                     x_object_volume=None):
    """
    Helper function for building a location dictionary

    Parameters
    ----------
    location: Well, str, optional
        Location refers to the well location where the transports will be
        carried out
    transports: List[transport_builder()]
        Transports refer to the list of transports that will be carried out
         in the specified location
    cycles: Int, optional
        Number of cycles to repeat stated transports
    x_object_volume: :List[Unit, Str], optional
        Volume which we think is present in the aliquot. This will be used
        when the detection method "tracked" is used

    Returns
    -------
    Location Parameters: Dictionary
    """
    if cycles is not None and not isinstance(cycles, int):
        raise TypeError("Cycles {} is not of type int".format(cycles))
    if transports is not None and not isinstance(transports, list):
        raise TypeError("Transports {} is not of type list".format(transports))
    if location is not None and not isinstance(location, Well) and \
            not isinstance(location, str):
        raise TypeError("Location {} is not of type str or Well".format(
            location))
    if x_object_volume is not None and not isinstance(x_object_volume, list):
        raise TypeError("x_object_volume {} is not of type list".format(
            x_object_volume
        ))

    if transports is not None and len(transports) <= 0:
        raise ValueError("At least one transport has to be defined")
    if cycles is not None and cycles <= 0:
        raise ValueError("Cycles have to be positive")
    if x_object_volume is not None:
        if len(x_object_volume) <= 0:
            raise ValueError("At least one x_object_volume has to be specified")
        x_object_volume = [parse_unit(vol, "ul") for vol in x_object_volume]

    arg_list = list(locals().items())
    arg_dict = {k: v for k, v in arg_list if v is not None}
    return arg_dict if arg_dict else None


def transport_builder(volume=None, flowrate=None, delay_time=None,
                      mode_params=None, x_calibrated_volume=None):
    """
    Helper function for building a transport dictionary

    Parameters
    ----------
    volume: Unit, str, optional
        Volume to be aspirated/dispensed. Positive volume -> Dispense.
        Negative -> Aspirate
    flowrate: flowrate_builder(), optional
        Flowrate parameters, look at flowrate_builder for more details
    delay_time: Unit, str, optional
        Time spent waiting after executing mandrel and pump movement
    mode_params: mode_params_builder(), optional
        Mode parameters, look at mode_params_builder for more details
    x_calibrated_volume: Unit, str, optional
        Calibrated volume, volume which the pump will move

    Returns
    -------
    Transport Parameters: Dictionary
    """
    if volume is not None:
        volume = parse_unit(volume, "ul")
    if flowrate is not None and not isinstance(flowrate, dict):
        raise TypeError("Flowrate {} is not of type dict".format(flowrate))
    if delay_time is not None:
        delay_time = parse_unit(delay_time, "s")
    if mode_params is not None and not isinstance(mode_params, dict):
        raise TypeError("Mode Params {} is not of type dict."
                        "Please use flowrate_builder".format(mode_params)
                        )
    if x_calibrated_volume is not None:
        x_calibrated_volume = parse_unit(x_calibrated_volume, "ul")

    arg_list = list(locals().items())
    arg_dict = {k: v for k, v in arg_list if v is not None}
    return arg_dict if arg_dict else None


def flowrate_builder(target, initial=None, cutoff=None, x_acceleration=None,
                     x_deceleration=None, device="omni"):
    """
    Helper function for building a flowrate dictionary.

    Parameters
    ----------
    target: Unit, str
        Target flowrate
    initial: Unit, str, optional
        Initial flowrate
    cutoff: Unit, str, optional
        Cutoff flowrate
    x_acceleration: Int, optional
        Volumetric acceleration for initial to target (in ul/s^2)
    x_deceleration: Int, optional
        Volumetric deceleration for target to cutoff (in ul/s^2)
    device: String
        Checks parameters according to the specified device
    Returns
    -------
    Flowrate Parameters: Dictionary
    """
    _valid_devices = ["omni", "bravo"]

    target = parse_unit(target, "ul/s")
    if initial is not None:
        initial = parse_unit(initial, "ul/s")
    if cutoff is not None:
        cutoff = parse_unit(cutoff, "ul/s")
    if x_acceleration is not None and not isinstance(x_acceleration, int):
        raise TypeError("{} is not of type int".format(x_acceleration))
    if x_deceleration is not None and not isinstance(x_deceleration, int):
        raise TypeError("{} is not of type int".format(x_deceleration))

    if device is not None and device not in _valid_devices:
        raise ValueError("{} has to be in {}").format(
            device, _valid_devices
        )
    else:
        device = "omni"

    if initial is not None and device not in ["omni"]:
        raise ValueError("initial does not apply to {}".format(device))
    if x_deceleration is not None and device not in ["omni"]:
        raise ValueError("x_deceleration does not apply to {}".format(device))

    arg_list = list(locals().items())
    arg_dict = {k: v for k, v in arg_list if v is not None}
    arg_dict.pop("device", None)
    arg_dict.pop("_valid_devices", None)

    return arg_dict if arg_dict else None


def mode_params_builder(liquid_class=None, tip_x=None, tip_y=None, tip_z=None):
    """
    Helper function for creating transport/tip-movement mode parameters

    Parameters
    ----------
    liquid_class: str, optional
        Accepts only "air" or "default"
    tip_x: float, optional
        Target relative x-position of tip in well in unit square coordinates.
        Defaults to 0
    tip_y: float, optional
        Target relative y-position of tip in well in unit square coordinates.
        Defaults to 0
    tip_z: z_position_builder(), optional
        Target relative z-position of tip in well. Refer to z_position_builder
        for more details
    Returns
    -------
    Mode Parameters: Dictionary
    """
    if liquid_class and not isinstance(liquid_class, str):
        raise TypeError("Liquid class {} is not of type str".format(
            liquid_class
        ))
    if tip_x and not isinstance(tip_x, float) and not isinstance(tip_x, int):
        raise TypeError("Tip_x {} is not of type float/int".format(
            tip_x
        ))
    if tip_y and not isinstance(tip_y, float) and not isinstance(tip_y, int):
        raise TypeError("Tip_y {} is not of type float/int".format(
            tip_y
        ))
    if tip_z and not isinstance(tip_z, dict):
        raise TypeError("Tip_z {} is not of type dict. Consider"
                        "using the z_position_builder helper.".format(tip_z))

    _liquid_classes = ["air", "default"]
    if liquid_class:
        if liquid_class not in _liquid_classes:
            raise ValueError(liquid_class + " has to be in " + liquid_class)
    if tip_x and (tip_x > 1 or tip_x < -1):
        raise ValueError("Tip_x {} has to be in Unit coordinates")
    if tip_y and (tip_y > 1 or tip_y < -1):
        raise ValueError("Tip_y {} has to be in Unit coordinates")

    mode_params_dict = {k: v for k, v in [("liquid_class", liquid_class)] if v}
    tip_position_dict = {k: v for k, v in [("position_x", tip_x),
                                           ("position_y", tip_y),
                                           ("position_z", tip_z)] if v}
    if tip_position_dict is not None:
        mode_params_dict["tip_position"] = tip_position_dict
    return mode_params_dict


def z_position_builder(reference=None, offset=None,
                       detection_method=None, detection_threshold=None,
                       detection_duration=None, fallback=None,
                       device="omni"):
    """
    Helper function for creating z_positions, which refer to the position in
    the well where the tip is located

    Parameters
    ----------
    reference: String, optional
        Must be one of "well_top", "well_bottom", "liquid_surface",
         "preceding_position"
    offset: Unit, optional
        Offset from reference position
    detection_method: String, optional
        Must be one of "tracked", "pressure", "capacitance"
    detection_threshold: Unit, str, optional
        The threshold which must be crossed before a positive reading is
        registered.
        This is applicable for capacitance and pressure detection methods
    detection_duration: Unit, str, optional
        The contiguous duration where the threshold must be crossed before a
        positive reading is registered.
        This is applicable for pressure detection methods
    fallback: z_position_builder(), optional
        Fallback option which will be used if sensing fails
    device: String
        Checks parameters according to the specified device
    Returns
    -------
    Position Z Parameters: Dictionary
    """
    _valid_references = ["well_top", "well_bottom", "liquid_surface",
                         "preceding_position"]
    _valid_device_methods = {
        "omni": ["tracked", "pressure", "capacitance"],
        "bravo": ["tracked"]
    }
    _valid_devices = _valid_device_methods.keys()

    if reference is not None and not isinstance(reference, str):
        raise TypeError("Reference {} is not of type str".format(
            reference
        ))
    if offset is not None and not isinstance(offset, Unit):
        raise TypeError("Offset {} is not of type Unit".format(
            offset
        ))
    if detection_method is not None and not isinstance(detection_method, str):
        raise TypeError("Detection_method {} is not of type str".format(
            detection_method
        ))
    if detection_threshold is not None and not \
            isinstance(detection_threshold, Unit):
        raise TypeError("Detection_threshold {} is not of type Unit".format(
            detection_threshold
        ))
    if fallback is not None and not isinstance(fallback, dict):
        raise TypeError("Fallback {} is not of type dict".format(
            fallback
        ))
    if device is not None and not isinstance(device, str):
        raise TypeError("Device {} is not of type str".format(
            device
        ))

    position_z_dict = {}
    if device is not None and device not in _valid_devices:
        raise ValueError("{} has to be in {}").format(
            device, _valid_devices
        )
    else:
        device = "omni"
    _valid_methods = _valid_device_methods[device]

    if reference:
        position_z_dict = dict(reference=reference)
        if reference not in _valid_references:
            raise ValueError("{} has to be in {}".format(
                reference, _valid_references
            ))
    if (detection_duration or detection_threshold) and \
            not detection_method and detection_method != "tracked":
        raise ValueError("Detection method is required when specifying "
                         "detection threshold or duration")
    if offset:
        position_z_dict["offset"] = offset
    if detection_method:
        if detection_method not in _valid_methods:
            raise ValueError("{} has to be in {}".format(
                detection_method, _valid_methods
            ))
        if reference in ["well_top", "well_bottom"]:
            raise ValueError("Detection does not apply for well_top, "
                             "well_bottom references")
        position_z_dict["detection"] = dict(method=detection_method)
        if detection_threshold:
            position_z_dict["detection"]["threshold"] = parse_unit(
                detection_threshold, ["farad", "pascal"]
            )
        if detection_duration:
            position_z_dict["detection"]["duration"] = parse_unit(
                detection_duration, "s"
            )
        if fallback:
            position_z_dict["detection"]["fallback"] = fallback
    return position_z_dict


def mix_transports_helper(volume=Unit("50:microliter"),
                          speed=Unit("100:microliter/second"),
                          repetitions=10,
                          z_height="1:mm",
                          new_defaults=None
                          ):
    """
    Helper function for creating mix transports

    Parameters
    ----------
    volume : str, Unit, optional
        volume of liquid to be aspirated and expelled during mixing
    speed : str, Unit, optional
        flowrate of liquid during mixing
    repetitions : int, optional
        number of times to aspirate and expel liquid during mixing
    z_height: Unit, str, optional
        If specified, moves to specified height above well_bottom before mixing.
        Otherwise, begins mixing from wherever the preceding position was
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before
    Return
    ------
    Mix transports: List
    """
    target_speed = Unit(speed) if speed else Unit("100:microliter/second")
    repetitions = repetitions if repetitions else 10
    mix_list = []
    if z_height:
        mix_list += [(
            transport_builder(
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_bottom",
                        offset=Unit(z_height)
                    )
                )
            )
        )]
    mix_vol = Unit(volume)
    mix_list += (
        [
            transport_builder(
                volume=-mix_vol,
                x_calibrated_volume=-mix_vol,
                flowrate=flowrate_builder(target_speed),
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position"
                    )
                )
            ),
            transport_builder(
                volume=mix_vol,
                x_calibrated_volume=mix_vol,
                flowrate=flowrate_builder(target_speed),
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position"
                    )
                )
            )
        ] * repetitions
    )
    return mix_list


def old_xfer_asp_transports(volume, aspirate_speed=None, dispense_speed=None,
                            aspirate_source=None, dispense_target=None,
                            pre_buffer=None, disposal_vol=None,
                            transit_vol=None, blowout_buffer=None,
                            new_defaults=None, **mix_kwargs):
    """
    Helper function for recreating aspirate behavior using transports

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    mix_after : bool, optional
        Specify whether to mix the liquid in the destination well after
        liquid is transferred.
    mix_before : bool, optional
        Specify whether to mix the liquid in the source well before
        liquid is transferred.
    mix_vol : str, Unit, optional
        Volume to aspirate and dispense in order to mix liquid in a wells
        before and/or after each transfer step.
    repetitions : int, optional
        Number of times to aspirate and dispense in order to mix
        liquid in well before and/or after each transfer step.
    flowrate : str, Unit, optional
        Speed at which to mix liquid in well before and/or after each
        transfer step.
    aspirate_speed : str, Unit, optional
        Speed at which to aspirate liquid from source well.  May not be
        specified if aspirate_source is also specified. By default this is
        the maximum aspiration speed, with the start speed being half of
        the speed specified.
    dispense_speed : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    aspirate_source : fn, optional
        Can't be specified if aspirate_speed is also specified.
    dispense_target : fn, optional
        Same but opposite of  aspirate_source.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Aspirate transports : List
    """
    arg_dict = {k: v for k, v in list(locals().items()) if v is not None}
    arg_dict.pop("dispense_target", None)
    arg_dict.pop("dispense_speed", None)
    arg_dict.pop("blowout_buffer", None)
    # Handle mix_kwargs by first removing non-applicable parameters
    if "mix_kwargs" in arg_dict:
        arg_dict.update(arg_dict.pop("mix_kwargs"))
        [arg_dict.pop(mix_param, None) for mix_param in ["mix_after",
                                                         "flowrate_a",
                                                         "repetitions_a"]]
        # Overwrite appropriate parameters
        if "repetitions_b" in arg_dict:
            arg_dict["repetitions"] = arg_dict.pop("repetitions_b")
        if "flowrate_b" in arg_dict:
            arg_dict["flowrate"] = arg_dict.pop("flowrate_b")
    return xfer_asp_helper(volume, **parse_xfer_params(**arg_dict))


def xfer_asp_helper(volume, aspirate_flowrate=None, pre_buffer=None,
                    disposal_vol=None, transit_vol=None, tip_z=None,
                    calibrated_vol=None, primer_vol=None,
                    following=None, mix_before=None, mix_speed=None,
                    repetitions=None, mix_vol=None, new_defaults=None):
    """
    Helper function for recreating similar transport behavior for aspirates.
    Note that volumes are not treated in the exact same manner, which may
    result in additional volume being aspirated for the ancillary operations

    Parameters
    ----------
    volume : str, Unit, list
            The volume(s) of liquid to be transferred from source wells to
            destination wells.  Volume can be specified as a single string or
            Unit, or can be given as a list of volumes.  The length of a list
            of volumes must match the number of destination wells given unless
            the same volume is to be transferred to each destination well.
    aspirate_flowrate : flowrate_builder()
        Flowrate at which to aspirate liquid from source well.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    tip_z: z_position_builder()
        z_position of dispense step
    calibrated_vol: Unit
        Calibrated volume that will be aspirated
    primer_vol: Unit
        Primer volume that will be aspirated in addition to volume
    following: bool
        If true, the tip will try to "follow" the liquid level as its aspirating
    mix_before: Bool
        Determines if mixing is carried out before aspirating
    mix_speed: Unit
        Mixing speed
    repetitions: Int
        Number of mixing repetitions
    mix_vol: Unit
        Volume of mix after dispensing
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Aspirate transports : List
    """
    # Setup aspirate
    aspirate_transport_list = []
    volume = Unit(volume)

    # Pre-Buffer
    if pre_buffer > Unit("0:uL"):
        aspirate_transport_list += [(
            transport_builder(
                x_calibrated_volume=-pre_buffer,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_top",
                        offset=Unit("1.0:mm")
                    ),
                    liquid_class="air"
                )
            )
        )]

    # Mix-before
    if mix_before:
        mix_vol = Unit(mix_vol or (volume / 2))
        aspirate_transport_list += mix_transports_helper(mix_vol, mix_speed,
                                                         repetitions, "0.5:mm")

    # Do liquid sensing with specified parameters
    aspirate_transport_list += [
        transport_builder(
            mode_params=mode_params_builder(
                tip_z=tip_z
            )
        )
    ]

    # Aspirate with primer + disposal vol
    if not primer_vol:
        primer_vol = Unit("5:uL")

    if following:
        aspirate_tip_z = z_position_builder(
                            reference="liquid_surface",
                            detection_method="tracked",
                            offset=Unit("-1:mm")
                        )
    else:
        aspirate_tip_z = z_position_builder(reference="preceding_position")

    cal_asp_vol = -(calibrated_vol + primer_vol + disposal_vol) if \
        calibrated_vol else None
    aspirate_transport_list += [
        transport_builder(
            volume=-(volume + primer_vol + disposal_vol),
            x_calibrated_volume=cal_asp_vol,
            flowrate=aspirate_flowrate,
            mode_params=mode_params_builder(
                tip_z=aspirate_tip_z
            )
        )
    ]

    # Dispense Prime Volume
    aspirate_transport_list += [(
        transport_builder(
            volume=primer_vol,
            x_calibrated_volume=primer_vol,
            flowrate=aspirate_flowrate,
            mode_params=mode_params_builder(
                tip_z=z_position_builder(
                    reference="preceding_position"
                )
            )
        )
    )]

    # Aspirate Transit Volume
    if transit_vol > Unit("0:uL"):
        aspirate_transport_list += [(
            transport_builder(
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_top",
                        offset=Unit("1.0:mm")
                    )
                )
            )
        )]
        aspirate_transport_list += [(
            transport_builder(
                x_calibrated_volume=-transit_vol,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position"
                    ),
                    liquid_class="air"
                )
            )
        )]

    return aspirate_transport_list


def old_xfer_dsp_transports(volume, aspirate_speed=None, dispense_speed=None,
                            aspirate_source=None, dispense_target=None,
                            pre_buffer=None, disposal_vol=None,
                            transit_vol=None, blowout_buffer=None,
                            new_defaults=None, **mix_kwargs):
    """
    Helper function for recreating dispense behavior using transports

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    mix_after : bool, optional
        Specify whether to mix the liquid in the destination well after
        liquid is transferred.
    mix_before : bool, optional
        Specify whether to mix the liquid in the source well before
        liquid is transferred.
    mix_vol : str, Unit, optional
        Volume to aspirate and dispense in order to mix liquid in a wells
        before and/or after each transfer step.
    repetitions : int, optional
        Number of times to aspirate and dispense in order to mix
        liquid in well before and/or after each transfer step.
    flowrate : str, Unit, optional
        Speed at which to mix liquid in well before and/or after each
        transfer step.
    aspirate_speed : str, Unit, optional
        Speed at which to aspirate liquid from source well.  May not be
        specified if aspirate_source is also specified. By default this is
        the maximum aspiration speed, with the start speed being half of
        the speed specified.
    dispense_speed : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    aspirate_source : fn, optional
        Can't be specified if aspirate_speed is also specified.
    dispense_target : fn, optional
        Same but opposite of  aspirate_source.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Dispense transports : List
    """
    arg_dict = {k: v for k, v in list(locals().items()) if v}
    arg_dict.pop("aspirate_source", None)
    arg_dict.pop("aspirate_speed", None)
    # Handle mix_kwargs by first removing non-applicable parameters
    if "mix_kwargs" in arg_dict:
        arg_dict.update(arg_dict.pop("mix_kwargs"))
        [arg_dict.pop(mix_param, None) for mix_param in ["mix_before",
                                                         "flowrate_b",
                                                         "repetitions_b"]]
        # Overwrite appropriate parameters
        if "repetitions_a" in arg_dict:
            arg_dict["repetitions"] = arg_dict.pop("repetitions_a")
        if "flowrate_a" in arg_dict:
            arg_dict["flowrate"] = arg_dict.pop("flowrate_a")
    return xfer_dsp_helper(volume, **parse_xfer_params(**arg_dict))


def xfer_dsp_helper(volume, dispense_flowrate=None, pre_buffer=None,
                    disposal_vol=None, transit_vol=None,
                    blowout_buffer=None, tip_z=None,
                    following=None, calibrated_vol=None,
                    mix_speed=None, repetitions=None,
                    mix_vol=None, mix_after=None, new_defaults=None):
    """
    Helper function for creating dispense behavior using transports

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    dispense_flowrate : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    tip_z: z_position_builder()
        Z_position of dispense step
    following: bool
        If true, the tip will try to "follow" the liquid level as its dispensing
    calibrated_vol: Unit
        Calibrated volume that will be aspirated
    mix_after: Bool
        Determines if mixing is carried out after dispensing
    mix_speed: Unit
        Mixing speed
    repetitions: Int
        Number of mixing repetitions
    mix_vol: Unit
        Volume of mix after dispensing
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Dispense transports : List
    """
    # Setup dispense
    dispense_transport_list = []

    # Dispense Transit Volume
    if transit_vol > Unit("0:uL"):
        dispense_transport_list += [(
            transport_builder(
                x_calibrated_volume=transit_vol,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_top",
                        offset=Unit("1:mm")
                    ),
                    liquid_class="air"
                )
            )
        )]

    # Dispense
    dispense_transport_list += [
        transport_builder(
            mode_params=mode_params_builder(
                tip_z=tip_z
            )
        )
    ]

    if following:
        dispense_tip_z = z_position_builder(
                            reference="liquid_surface",
                            detection_method="tracked",
                            offset=Unit("-1:mm")
                        )
    else:
        dispense_tip_z = z_position_builder(reference="preceding_position")

    dispense_transport_list += [
        transport_builder(
            volume=volume,
            x_calibrated_volume=calibrated_vol,
            flowrate=dispense_flowrate,
            mode_params=mode_params_builder(
                tip_z=dispense_tip_z
            )
        )
    ]

    # Mix-after
    if mix_after:
        mix_vol = Unit(mix_vol or (volume / 2))
        dispense_transport_list += mix_transports_helper(mix_vol, mix_speed,
                                                         repetitions, "0.5:mm")

    if blowout_buffer and pre_buffer > Unit("0:uL"):
        if new_defaults:
            dispense_transport_list += [
                transport_builder(
                    mode_params=mode_params_builder(
                        tip_z=z_position_builder(
                            reference="well_top",
                            offset=Unit("-2:mm")
                        ),
                    )
                )
            ]
        else:
            dispense_transport_list += [
                transport_builder(
                    mode_params=mode_params_builder(
                        tip_z=z_position_builder(
                            reference="well_bottom",
                            offset=Unit("1:mm")
                        ),
                    )
                )
            ]
        dispense_transport_list += [(
            transport_builder(
                x_calibrated_volume=pre_buffer,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position"
                    ),
                    liquid_class="air"
                )
            )
        )]

    return dispense_transport_list


def parse_xfer_params(volume, aspirate_speed=None, dispense_speed=None,
                      aspirate_source=None, dispense_target=None,
                      pre_buffer=None, disposal_vol=None, transit_vol=None,
                      blowout_buffer=None, mix_before=None, mix_after=None,
                      mix_vol=None, repetitions=None, flowrate=None,
                      new_defaults=None):
    """
    Helper function for mapping old pipetting parameters to transport
    specific parameters

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    mix_after : bool, optional
        Specify whether to mix the liquid in the destination well after
        liquid is transferred.
    mix_before : bool, optional
        Specify whether to mix the liquid in the source well before
        liquid is transferred.
    mix_vol : str, Unit, optional
        Volume to aspirate and dispense in order to mix liquid in a wells
        before and/or after each transfer step.
    repetitions : int, optional
        Number of times to aspirate and dispense in order to mix
        liquid in well before and/or after each transfer step.
    flowrate : str, Unit, optional
        Speed at which to mix liquid in well before and/or after each
        transfer step.
    aspirate_speed : str, Unit, optional
        Speed at which to aspirate liquid from source well.  May not be
        specified if aspirate_source is also specified. By default this is
        the maximum aspiration speed, with the start speed being half of
        the speed specified.
    dispense_speed : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    aspirate_source : fn, optional
        Can't be specified if aspirate_speed is also specified.
    dispense_target : fn, optional
        Same but opposite of  aspirate_source.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before
    """
    if aspirate_source and dispense_target:
        raise ValueError("parse_xfer_params only supports either "
                         "aspirate_source or dispense_target")

    # Helpers for generating old defaults
    def old_pre_buffer(v):
        if v < Unit("10:uL"):
            return Unit("5:uL")
        elif v <= Unit("25:uL"):
            return Unit("10:uL")
        elif v <= Unit("75:uL"):
            return Unit("15:uL")
        elif v <= Unit("100:uL"):
            return Unit("20:uL")
        else:
            return Unit("25:uL")

    def old_transit_vol(v):
        return Unit("2:uL")

    # Used only in `Distribute`
    def old_disposal_vol(v):
        if v <= Unit("50.uL"):
            return Unit("0:uL")
        else:
            return (v / 5)

    # Helper for constructing z_position from depth
    def parse_depth(depth):
        z_pos_dict = {}
        following = True
        _reference_map = {"ll_following": "liquid_surface",
                          "ll_top": "well_top",
                          "ll_bottom": "well_bottom",
                          "ll_surface": "liquid_surface"}
        _method_map = {"capacitive": "capacitance",
                       "pressure": "pressure"}
        for k, v in depth.items():
            if k == "method":
                z_pos_dict["reference"] = _reference_map[v]
            if k == "method" and v == "ll_surface":
                following = False
            if k == "distance":
                z_pos_dict["offset"] = Unit(v)
            if k in _method_map:
                z_pos_dict["detection_method"] = _method_map[v]
        return following, z_pos_dict

    if pre_buffer:
        pre_buffer = Unit(pre_buffer)
    else:
        pre_buffer = old_pre_buffer(volume)

    if disposal_vol:
        disposal_vol = Unit(disposal_vol)
    else:
        disposal_vol = Unit("0:microliter")

    if transit_vol:
        transit_vol = Unit(transit_vol)
    else:
        transit_vol = old_transit_vol(volume)

    if aspirate_speed:
        aspirate_flowrate = flowrate_builder(Unit(aspirate_speed))

    if dispense_speed:
        dispense_flowrate = flowrate_builder(Unit(dispense_speed))

    clld_unit = Unit("0.009740:picofarad")
    plld_unit = Unit("0.000109867:psi")
    # TCLE fallback defaults to 1:mm above well_bottom if capacitance fails
    z_pos_dict = {
        "reference": "liquid_surface",
        "offset": Unit("-1:mm"),
        "detection_method": "capacitance",
        "detection_threshold": clld_unit * 63
    }
    # Following is true by default
    following = True

    # Intepret old `pipette_tools` builders
    if aspirate_source:
        for k, v in aspirate_source.items():
            if k == "aspirate_speed":
                aspirate_flowrate = flowrate_builder(Unit(v["max"]),
                                                     initial=Unit(v["start"]))
            calibrated_vol = Unit(v) if k == "volume" else None
            primer_vol = Unit(v) if k == "primer_vol" else None
            if k == "depth":
                following, tip_z = parse_depth(v)
                z_pos_dict.update(tip_z)
            if k == "clld_sensitivity":
                z_pos_dict["detection_threshold"] = clld_unit * v
            if k == "plld_threshold":
                z_pos_dict["detection_threshold"] = plld_unit * v["sensitivity"]
                z_pos_dict["detection_duration"] = v["duration"]

    if dispense_target:
        for k, v in dispense_target.items():
            if k == "dispense_speed":
                dispense_flowrate = flowrate_builder(Unit(v["max"]),
                                                     initial=Unit(v["start"]))
            calibrated_vol = Unit(v) if k == "volume" else None
            if k == "depth":
                following, tip_z = parse_depth(v)
                z_pos_dict.update(tip_z)
            if k == "clld_sensitivity":
                z_pos_dict["detection_threshold"] = clld_unit * v
            if k == "plld_threshold":
                z_pos_dict["detection_threshold"] = plld_unit * v["sensitivity"]
                z_pos_dict["detection_duration"] = v["duration"]

    # Purge detection parameters if reference is not liquid surface
    if z_pos_dict["reference"] in ["well_top", "well_bottom"]:
        z_pos_dict.pop("detection_method", None)
        z_pos_dict.pop("detection_threshold", None)
        z_pos_dict.pop("detection_duration", None)

    tip_z = z_position_builder(**z_pos_dict) if z_pos_dict else None

    pipette_params = ["aspirate_flowrate", "dispense_flowrate", "pre_buffer",
                      "disposal_vol", "transit_vol", "blowout_buffer",
                      "primer_vol", "calibrated_vol", "tip_z", "following",
                      "flowrate", "mix_before", "mix_after", "repetitions",
                      "mix_vol", "new_defaults"]

    arg_list = list(locals().items())
    pipette_args = {k: v for k, v in arg_list if k in pipette_params and v is
                    not None}

    # Handling mix kwargs
    pipette_args["mix_speed"] = pipette_args.pop("flowrate", None)
    return pipette_args


def move_over_transport(z_height=None):
    """
    Helper function for generating a transport which hovers above the target
    location

    Parameters
    ----------
    z_height: Unit, str, Optional
        If specified, controls the height above the bottom of the well
        at which the head will travel to
    Returns
    -------
    transport_list: List
    """
    transport_list = []
    if z_height:
        transport_list += [
            transport_builder(
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_bottom",
                        offset=Unit(z_height)
                    )
                )
            )
        ]
    else:
        transport_list += [
            transport_builder(
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position"
                    )
                )
            )
        ]
    return transport_list


def old_stamp_dsp_transports(volume, aspirate_speed=None, dispense_speed=None,
                             aspirate_source=None, dispense_target=None,
                             pre_buffer=None, disposal_vol=None,
                             transit_vol=None, blowout_buffer=None,
                             mix_before=None, mix_after=None, mix_vol=None,
                             repetitions=None, flowrate=None,
                             shape_format=None, new_defaults=None):
    """
    Helper function for recreating aspirate behavior using transports

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    mix_after : bool, optional
        Specify whether to mix the liquid in the destination well after
        liquid is transferred.
    mix_before : bool, optional
        Specify whether to mix the liquid in the source well before
        liquid is transferred.
    mix_vol : str, Unit, optional
        Volume to aspirate and dispense in order to mix liquid in a wells
        before and/or after each transfer step.
    repetitions : int, optional
        Number of times to aspirate and dispense in order to mix
        liquid in well before and/or after each transfer step.
    flowrate : str, Unit, optional
        Speed at which to mix liquid in well before and/or after each
        transfer step.
    aspirate_speed : str, Unit, optional
        Speed at which to aspirate liquid from source well.  May not be
        specified if aspirate_source is also specified. By default this is
        the maximum aspiration speed, with the start speed being half of
        the speed specified.
    dispense_speed : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    aspirate_source : fn, optional
        Can't be specified if aspirate_speed is also specified.
    dispense_target : fn, optional
        Same but opposite of  aspirate_source.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    shape_format: str
        Specifies the format of the shape that will be used for the stamp.
        Choose between "SBS96" and "SBS384"
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Aspirate transports : List
    """
    arg_dict = {k: v for k, v in list(locals().items()) if v}
    arg_dict.pop("aspirate_source", None)
    arg_dict.pop("aspirate_speed", None)
    arg_dict.pop("mix_before", None)

    old_params = parse_stamp_params(**arg_dict)
    return stamp_dsp_helper(volume, **old_params)


def stamp_dsp_helper(volume, dispense_flowrate=None, pre_buffer=None,
                     blowout_buffer=None, tip_z=None,
                     following=None, calibrated_vol=None,
                     mix_speed=None, repetitions=None,
                     mix_vol=None, mix_after=None,
                     transit_vol=None, new_defaults=None):
    """
    Helper function for creating dispense behavior using transports

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    dispense_flowrate : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    tip_z: z_position_builder()
        Z_position of dispense step
    following: bool
        If true, the tip will try to "follow" the liquid level as its dispensing
    calibrated_vol: Unit
        Calibrated volume that will be aspirated
    mix_after: Bool
        Determines if mixing is carried out after dispensing
    mix_speed: Unit
        Mixing speed
    repetitions: Int
        Number of mixing repetitions
    mix_vol: Unit
        Volume of mix after dispensing
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Dispense transports : List
    """
    # Setup dispense
    dispense_transport_list = []

    # Dispense Transit Volume
    if new_defaults and transit_vol > Unit("0:uL"):
        dispense_transport_list += [(
            transport_builder(
                x_calibrated_volume=transit_vol,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_top",
                        offset=Unit("1:mm")
                    ),
                    liquid_class="air"
                )
            )
        )]

    # Move to dispense position
    if not tip_z:
        tip_z = z_position_builder(
            reference="well_bottom",
            offset=Unit("1:mm")
        )
    dispense_transport_list += [
        transport_builder(
            mode_params=mode_params_builder(
                tip_z=tip_z
            )
        )
    ]

    if following:
        dispense_tip_z = z_position_builder(
                            reference="liquid_surface",
                            detection_method="tracked",
                            offset=Unit("-1:mm")
                        )
    else:
        dispense_tip_z = z_position_builder(reference="preceding_position")

    dispense_transport_list += [
        transport_builder(
            volume=volume,
            x_calibrated_volume=calibrated_vol,
            flowrate=dispense_flowrate,
            mode_params=mode_params_builder(
                tip_z=dispense_tip_z
            )
        )
    ]

    # Mix-after
    if mix_after:
        mix_vol = Unit(mix_vol or (volume / 2))
        dispense_transport_list += mix_transports_helper(mix_vol, mix_speed,
                                                         repetitions)

    # Blowout pre_buffer
    if blowout_buffer and pre_buffer > Unit("0:uL"):
        if new_defaults:
            dispense_transport_list += [
                transport_builder(
                    mode_params=mode_params_builder(
                        tip_z=z_position_builder(
                            reference="well_top",
                            offset=Unit("-2:mm")
                        ),
                    )
                )
            ]
        else:
            dispense_transport_list += [
                transport_builder(
                    mode_params=mode_params_builder(
                        tip_z=z_position_builder(
                            reference="well_bottom",
                            offset=Unit("1:mm")
                        ),
                    )
                )
            ]
        dispense_transport_list += [(
            transport_builder(
                x_calibrated_volume=pre_buffer,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position",
                    ),
                    liquid_class="air"
                )
            )
        )]

    return dispense_transport_list


def old_stamp_asp_transports(volume, aspirate_speed=None, dispense_speed=None,
                             aspirate_source=None, dispense_target=None,
                             pre_buffer=None, disposal_vol=None,
                             transit_vol=None, blowout_buffer=None,
                             mix_before=None, mix_after=None, mix_vol=None,
                             repetitions=None, flowrate=None,
                             shape_format=None, new_defaults=None):
    """
    Helper function for recreating aspirate behavior using transports

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    mix_after : bool, optional
        Specify whether to mix the liquid in the destination well after
        liquid is transferred.
    mix_before : bool, optional
        Specify whether to mix the liquid in the source well before
        liquid is transferred.
    mix_vol : str, Unit, optional
        Volume to aspirate and dispense in order to mix liquid in a wells
        before and/or after each transfer step.
    repetitions : int, optional
        Number of times to aspirate and dispense in order to mix
        liquid in well before and/or after each transfer step.
    flowrate : str, Unit, optional
        Speed at which to mix liquid in well before and/or after each
        transfer step.
    aspirate_speed : str, Unit, optional
        Speed at which to aspirate liquid from source well.  May not be
        specified if aspirate_source is also specified. By default this is
        the maximum aspiration speed, with the start speed being half of
        the speed specified.
    dispense_speed : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    aspirate_source : fn, optional
        Can't be specified if aspirate_speed is also specified.
    dispense_target : fn, optional
        Same but opposite of  aspirate_source.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    disposal_vol : str, Unit, optional
        Volume of extra liquid to aspirate that will be dispensed into
        trash afterwards.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    shape_format: str
        Specifies the format of the shape that will be used for the stamp.
        Choose between "SBS96" and "SBS384"
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Aspirate transports : List
    """
    arg_dict = {k: v for k, v in list(locals().items()) if v is not None}
    arg_dict.pop("dispense_target", None)
    arg_dict.pop("dispense_speed", None)
    arg_dict.pop("mix_after", None)
    arg_dict.pop("blowout_buffer", None)

    old_params = parse_stamp_params(**arg_dict)
    # Following did not apply for stamp aspirates
    old_params.pop("following", None)

    return stamp_asp_helper(volume, **old_params)


def stamp_asp_helper(volume, aspirate_flowrate=None, pre_buffer=None,
                     tip_z=None, calibrated_vol=None, primer_vol=None,
                     blowout_buffer=None, transit_vol=None,
                     mix_before=None, mix_speed=None,
                     repetitions=None, mix_vol=None,
                     new_defaults=None):
    """
    Helper function for recreating similar transport behavior for aspirates.
    Note that volumes are not treated in the exact same manner, which may
    result in additional volume being aspirated for the ancillary operations

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    aspirate_flowrate : flowrate_builder()
        Flowrate at which to aspirate liquid from source well.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    tip_z: z_position_builder()
        Z_position of dispense step
    calibrated_vol: Unit
        Calibrated volume that will be aspirated
    primer_vol: Unit
        Primer volume that will be aspirated in addition to volume
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    mix_before: Bool
        Determines if mixing is carried out before aspirating
    mix_speed: Unit
        Mixing speed
    repetitions: Int
        Number of mixing repetitions
    mix_vol: Unit
        Volume of mix after dispensing
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before

    Returns
    -------
    Aspirate transports : List
    """

    # Setup aspirate
    aspirate_transport_list = []
    volume = Unit(volume)
    safe_offset = Unit("10:mm")

    # Pre-Buffer
    if pre_buffer > Unit("0:uL"):
        aspirate_transport_list += [(
            transport_builder(
                x_calibrated_volume=-pre_buffer,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_top",
                        offset=safe_offset
                    ),
                    liquid_class="air"
                )
            )
        )]

    # Move to specified z-location
    aspirate_transport_list += [(
        transport_builder(
            mode_params=mode_params_builder(
                tip_z=tip_z
            )
        )
    )]

    # Mix-before
    if mix_before:
        mix_vol = Unit(mix_vol or (volume / 2))
        aspirate_transport_list += mix_transports_helper(mix_vol, mix_speed,
                                                         repetitions,
                                                         z_height=None)

    # Aspirate with primer + disposal vol
    if not primer_vol:
        primer_vol = Unit("5:uL")

    # No following unless explicitly stated since Bravo doesn't have sensing
    aspirate_tip_z = z_position_builder(reference="preceding_position")

    cal_asp_vol = -(calibrated_vol + primer_vol) if \
        calibrated_vol else None
    aspirate_transport_list += [
        transport_builder(
            volume=-(volume + primer_vol),
            x_calibrated_volume=cal_asp_vol,
            flowrate=aspirate_flowrate,
            mode_params=mode_params_builder(
                tip_z=aspirate_tip_z
            )
        )
    ]

    # Dispense Prime Volume
    aspirate_transport_list += [(
        transport_builder(
            volume=primer_vol,
            x_calibrated_volume=primer_vol,
            flowrate=aspirate_flowrate,
            mode_params=mode_params_builder(
                tip_z=z_position_builder(
                    reference="preceding_position"
                )
            )
        )
    )]

    # Aspirate Transit Volume
    if new_defaults and transit_vol > Unit("0:uL"):
        aspirate_transport_list += [(
            transport_builder(
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="well_top",
                        offset=Unit("1.0:mm")
                    )
                )
            )
        )]
        aspirate_transport_list += [(
            transport_builder(
                x_calibrated_volume=-transit_vol,
                mode_params=mode_params_builder(
                    tip_z=z_position_builder(
                        reference="preceding_position"
                    ),
                    liquid_class="air"
                )
            )
        )]

    return aspirate_transport_list


def parse_stamp_params(volume, aspirate_speed=None, dispense_speed=None,
                       aspirate_source=None, dispense_target=None,
                       pre_buffer=None, blowout_buffer=None, mix_before=None,
                       mix_after=None, mix_vol=None, repetitions=None,
                       flowrate=None, transit_vol=None, shape_format=None,
                       new_defaults=None):
    """
    Helper function for mapping old stamp parameters to transport
    specific parameters

    Parameters
    ----------
    volume : str, Unit, list
        The volume(s) of liquid to be transferred from source wells to
        destination wells.  Volume can be specified as a single string or
        Unit, or can be given as a list of volumes.  The length of a list
        of volumes must match the number of destination wells given unless
        the same volume is to be transferred to each destination well.
    mix_after : bool, optional
        Specify whether to mix the liquid in the destination well after
        liquid is transferred.
    mix_before : bool, optional
        Specify whether to mix the liquid in the source well before
        liquid is transferred.
    mix_vol : str, Unit, optional
        Volume to aspirate and dispense in order to mix liquid in a wells
        before and/or after each transfer step.
    repetitions : int, optional
        Number of times to aspirate and dispense in order to mix
        liquid in well before and/or after each transfer step.
    flowrate : str, Unit, optional
        Speed at which to mix liquid in well before and/or after each
        transfer step.
    aspirate_speed : str, Unit, optional
        Speed at which to aspirate liquid from source well.  May not be
        specified if aspirate_source is also specified. By default this is
        the maximum aspiration speed, with the start speed being half of
        the speed specified.
    dispense_speed : str, Unit, optional
        Speed at which to dispense liquid into the destination well.  May
        not be specified if dispense_target is also specified.
    aspirate_source : fn, optional
        Can't be specified if aspirate_speed is also specified.
    dispense_target : fn, optional
        Same but opposite of  aspirate_source.
    pre_buffer : str, Unit, optional
        Volume of air aspirated before aspirating liquid.
    blowout_buffer : bool, optional
        If true the operation will dispense the pre_buffer along with the
        dispense volume. Cannot be true if disposal_vol is specified.
    transit_vol : str, Unit, optional
        Volume of air aspirated after aspirating liquid to reduce presence
        of bubbles at pipette tip.
    shape_format: str
        Specifies the format of the shape that will be used for the stamp.
        Choose between "SBS96" and "SBS384"
    new_defaults: bool, optional
        Specifies if recommended pipetting defaults will be used.
        This is false by default to maintain backwards compatibility and
        produce exactly the same behavior as before
    """
    if aspirate_source and dispense_target:
        raise ValueError("parse_stamp_params only supports either "
                         "aspirate_source or dispense_target")

    # Helpers for generating old defaults
    def old_pre_buffer(v):
        return Unit("5:uL")

    def old_transit_vol(v):
        return Unit("1:uL")

    # Helper for constructing z_position from depth
    def parse_depth(depth):
        z_pos_dict = {}
        following = True
        _reference_map = {"ll_following": "liquid_surface",
                          "ll_top": "well_top",
                          "ll_bottom": "well_bottom",
                          "ll_surface": "liquid_surface"}
        _method_map = {"capacitive": "capacitance",
                       "pressure": "pressure"}
        for k, v in depth.items():
            if k == "method":
                z_pos_dict["reference"] = _reference_map[v]
            if k == "method" and v == "ll_surface":
                following = False
            if k == "distance":
                z_pos_dict["offset"] = Unit(v)
            if k in _method_map:
                raise ValueError("No detection methods supported for "
                                 "multichannel")
        return following, z_pos_dict

    # Helper for generating old calibrated vol
    def get_cal_vol(v):
        if shape_format == "SBS384":
            if v <= Unit("0.5:ul"):
                return v * 1.16
            elif v <= Unit("1:ul"):
                return v * 1.24 - Unit("0.04:ul")
            elif v <= Unit("2.5:ul"):
                return v * 1.153 + Unit("0.047:ul")
            elif v <= Unit("5:ul"):
                return v * 1.048 + Unit("0.31:ul")
            elif v <= Unit("10:ul"):
                return v * 1.042 + Unit("0.34:ul")
            elif v <= Unit("15:ul"):
                return v * 1.148 - Unit("0.72:ul")
            else:
                return v * 1.148 - Unit("0.72:ul")
        else:
            return v

    if pre_buffer:
        pre_buffer = Unit(pre_buffer)
    else:
        pre_buffer = old_pre_buffer(volume)

    if transit_vol:
        transit_vol = Unit(transit_vol)
    else:
        transit_vol = old_transit_vol(volume)

    if not blowout_buffer and pre_buffer > Unit("0:ul"):
        blowout_buffer = True

    if aspirate_speed:
        aspirate_flowrate = flowrate_builder(Unit(aspirate_speed))

    if dispense_speed:
        dispense_flowrate = flowrate_builder(Unit(dispense_speed))

    # TCLE fallback defaults to 1:mm above well_bottom
    z_pos_dict = {
        "reference": "well_bottom",
        "offset": Unit("1:mm"),
    }
    # Following is true by default if new_defaults
    following = True if new_defaults else False

    # Intepret old `pipette_tools` builders
    calibrated_vol = None
    if aspirate_source:
        for k, v in aspirate_source.items():
            if k == "aspirate_speed":
                aspirate_flowrate = flowrate_builder(Unit(v["max"]),
                                                     initial=Unit(v["start"]))
            calibrated_vol = Unit(v) if k == "volume" else None
            primer_vol = Unit(v) if k == "primer_vol" else None
            if k == "depth":
                following, tip_z = parse_depth(v)
                z_pos_dict.update(tip_z)

    if dispense_target:
        for k, v in dispense_target.items():
            if k == "dispense_speed":
                dispense_flowrate = flowrate_builder(Unit(["max"]),
                                                     initial=Unit(v["start"]))
            calibrated_vol = Unit(v) if k == "volume" else None
            if k == "depth":
                following, tip_z = parse_depth(v)
                z_pos_dict.update(tip_z)

    # Purge detection parameters if reference is not liquid surface
    if z_pos_dict["reference"] in ["well_top", "well_bottom"]:
        z_pos_dict.pop("detection_method", None)
        z_pos_dict.pop("detection_threshold", None)
        z_pos_dict.pop("detection_duration", None)

    tip_z = z_position_builder(**z_pos_dict) if z_pos_dict else None

    if not calibrated_vol:
        if shape_format == "SBS386":
            calibrated_vol = get_cal_vol(volume)

    pipette_params = ["aspirate_flowrate", "dispense_flowrate", "pre_buffer",
                      "blowout_buffer", "primer_vol", "calibrated_vol", "tip_z",
                      "following", "flowrate", "mix_before", "mix_after",
                      "repetitions", "mix_vol", "transit_vol", "new_defaults"]

    arg_list = list(locals().items())
    pipette_args = {k: v for k, v in arg_list if k in pipette_params and v is
                    not None}

    # Handling mix kwargs
    pipette_args["mix_speed"] = pipette_args.pop("flowrate", None)

    return pipette_args
