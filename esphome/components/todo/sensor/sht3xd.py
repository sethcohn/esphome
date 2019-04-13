from esphome.components import i2c, sensor
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_ADDRESS, CONF_HUMIDITY, CONF_ID, CONF_NAME, \
    CONF_TEMPERATURE, CONF_UPDATE_INTERVAL


DEPENDENCIES = ['i2c']

SHT3XDComponent = sensor.sensor_ns.class_('SHT3XDComponent', PollingComponent, i2c.I2CDevice)
SHT3XDTemperatureSensor = sensor.sensor_ns.class_('SHT3XDTemperatureSensor',
                                                  sensor.EmptyPollingParentSensor)
SHT3XDHumiditySensor = sensor.sensor_ns.class_('SHT3XDHumiditySensor',
                                               sensor.EmptyPollingParentSensor)

PLATFORM_SCHEMA = sensor.PLATFORM_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(SHT3XDComponent),
    cv.Required(CONF_TEMPERATURE): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(SHT3XDTemperatureSensor),
    })),
    cv.Required(CONF_HUMIDITY): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(SHT3XDHumiditySensor),
    })),
    cv.Optional(CONF_ADDRESS, default=0x44): cv.i2c_address,
    cv.Optional(CONF_UPDATE_INTERVAL): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA)


def to_code(config):
    rhs = App.make_sht3xd_sensor(config[CONF_TEMPERATURE][CONF_NAME],
                                 config[CONF_HUMIDITY][CONF_NAME],
                                 config[CONF_ADDRESS],
                                 config.get(CONF_UPDATE_INTERVAL))
    sht3xd = Pvariable(config[CONF_ID], rhs)

    sensor.setup_sensor(sht3xd.Pget_temperature_sensor(), config[CONF_TEMPERATURE])
    sensor.setup_sensor(sht3xd.Pget_humidity_sensor(), config[CONF_HUMIDITY])
    register_component(sht3xd, config)


BUILD_FLAGS = '-DUSE_SHT3XD'
