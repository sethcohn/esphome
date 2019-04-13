from esphome.components import sensor, uart
from esphome.components.uart import UARTComponent
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_CURRENT, CONF_ID, CONF_NAME, CONF_POWER, CONF_UART_ID, \
    CONF_UPDATE_INTERVAL, CONF_VOLTAGE


DEPENDENCIES = ['uart']

CSE7766Component = sensor.sensor_ns.class_('CSE7766Component', PollingComponent, uart.UARTDevice)
CSE7766VoltageSensor = sensor.sensor_ns.class_('CSE7766VoltageSensor',
                                               sensor.EmptySensor)
CSE7766CurrentSensor = sensor.sensor_ns.class_('CSE7766CurrentSensor',
                                               sensor.EmptySensor)
CSE7766PowerSensor = sensor.sensor_ns.class_('CSE7766PowerSensor',
                                             sensor.EmptySensor)

PLATFORM_SCHEMA = cv.All(sensor.PLATFORM_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(CSE7766Component),
    cv.GenerateID(CONF_UART_ID): cv.use_variable_id(UARTComponent),

    cv.Optional(CONF_VOLTAGE): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(CSE7766VoltageSensor),
    })),
    cv.Optional(CONF_CURRENT): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(CSE7766CurrentSensor),
    })),
    cv.Optional(CONF_POWER): cv.nameable(sensor.SENSOR_SCHEMA.extend({
        cv.GenerateID(): cv.declare_variable_id(CSE7766PowerSensor),
    })),
    cv.Optional(CONF_UPDATE_INTERVAL): cv.update_interval,
}).extend(cv.COMPONENT_SCHEMA), cv.has_at_least_one_key(CONF_VOLTAGE, CONF_CURRENT,
                                                               CONF_POWER))


def to_code(config):
    uart_ = yield get_variable(config[CONF_UART_ID])

    rhs = App.make_cse7766(uart_, config.get(CONF_UPDATE_INTERVAL))
    cse = Pvariable(config[CONF_ID], rhs)

    if CONF_VOLTAGE in config:
        conf = config[CONF_VOLTAGE]
        sensor.register_sensor(cse.make_voltage_sensor(conf[CONF_NAME]), conf)
    if CONF_CURRENT in config:
        conf = config[CONF_CURRENT]
        sensor.register_sensor(cse.make_current_sensor(conf[CONF_NAME]), conf)
    if CONF_POWER in config:
        conf = config[CONF_POWER]
        sensor.register_sensor(cse.make_power_sensor(conf[CONF_NAME]), conf)
    register_component(cse, config)


BUILD_FLAGS = '-DUSE_CSE7766'
