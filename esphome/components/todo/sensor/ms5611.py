from esphome.components import i2c, sensor
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_ADDRESS, CONF_ID, CONF_NAME, CONF_PRESSURE, \
    CONF_TEMPERATURE, CONF_UPDATE_INTERVAL


DEPENDENCIES = ['i2c']

MS5611Component = sensor.sensor_ns.class_('MS5611Component', PollingComponent, i2c.I2CDevice)
MS5611TemperatureSensor = sensor.sensor_ns.class_('MS5611TemperatureSensor',
                                                  sensor.EmptyPollingParentSensor)
MS5611PressureSensor = sensor.sensor_ns.class_('MS5611PressureSensor',
                                               sensor.EmptyPollingParentSensor)

PLATFORM_SCHEMA = sensor.PLATFORM_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(MS5611Component),
    cv.Optional(CONF_ADDRESS): cv.i2c_address,
    cv.Required(CONF_TEMPERATURE): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(MS5611TemperatureSensor),
    })),
    cv.Required(CONF_PRESSURE): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(MS5611PressureSensor),
    })),
    cv.Optional(CONF_UPDATE_INTERVAL): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    rhs = App.make_ms5611_sensor(config[CONF_TEMPERATURE][CONF_NAME],
                                 config[CONF_PRESSURE][CONF_NAME],
                                 config.get(CONF_UPDATE_INTERVAL))
    ms5611 = Pvariable(config[CONF_ID], rhs)

    if CONF_ADDRESS in config:
        cg.add(ms5611.set_address(config[CONF_ADDRESS]))

    sensor.setup_sensor(ms5611.Pget_temperature_sensor(), config[CONF_TEMPERATURE])
    sensor.setup_sensor(ms5611.Pget_pressure_sensor(), config[CONF_PRESSURE])
    register_component(ms5611, config)


BUILD_FLAGS = '-DUSE_MS5611'
