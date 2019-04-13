from esphome.components import binary_sensor
from esphome.components.mpr121 import MPR121Component, CONF_MPR121_ID
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_CHANNEL, CONF_NAME
DEPENDENCIES = ['mpr121']
MPR121Channel = binary_sensor.binary_sensor_ns.class_(
    'MPR121Channel', binary_sensor.BinarySensor)

PLATFORM_SCHEMA = cv.nameable(binary_sensor.BINARY_SENSOR_PLATFORM_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(MPR121Channel),
    cv.GenerateID(CONF_MPR121_ID): cv.use_variable_id(MPR121Component),
    cv.Required(CONF_CHANNEL): cv.All(cv.Coerce(int), cv.Range(min=0, max=11))
}))


def to_code(config):
    hub = yield get_variable(config[CONF_MPR121_ID])
    rhs = MPR121Channel.new(config[CONF_NAME], config[CONF_CHANNEL])
    binary_sensor.register_binary_sensor(hub.add_channel(rhs), config)
