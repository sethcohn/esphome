from esphome import pins
from esphome.components import light
from esphome.components.light import AddressableLight
from esphome.components.power_supply import PowerSupplyComponent
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_CLOCK_PIN, CONF_DATA_PIN, CONF_MAKE_ID, CONF_METHOD, CONF_NAME, \
    CONF_NUM_LEDS, CONF_PIN, CONF_POWER_SUPPLY, CONF_TYPE, CONF_VARIANT
from esphome.core import CORE


NeoPixelBusLightOutputBase = light.light_ns.class_('NeoPixelBusLightOutputBase', Component,
                                                   AddressableLight)
ESPNeoPixelOrder = light.light_ns.namespace('ESPNeoPixelOrder')


def validate_type(value):
    value = cv.string(value).upper()
    if 'R' not in value:
        raise cv.Invalid("Must have R in type")
    if 'G' not in value:
        raise cv.Invalid("Must have G in type")
    if 'B' not in value:
        raise cv.Invalid("Must have B in type")
    rest = set(value) - set('RGBW')
    if rest:
        raise cv.Invalid("Type has invalid color: {}".format(', '.join(rest)))
    if len(set(value)) != len(value):
        raise cv.Invalid("Type has duplicate color!")
    return value


def validate_variant(value):
    value = cv.string(value).upper()
    if value == 'WS2813':
        value = 'WS2812X'
    if value == 'WS2812':
        value = '800KBPS'
    if value == 'LC8812':
        value = 'SK6812'
    return cv.one_of(*VARIANTS)(value)


def validate_method(value):
    if value is None:
        if CORE.is_esp32:
            return 'ESP32_I2S_1'
        if CORE.is_esp8266:
            return 'ESP8266_DMA'
        raise NotImplementedError

    if CORE.is_esp32:
        return cv.one_of(*ESP32_METHODS, upper=True, space='_')(value)
    if CORE.is_esp8266:
        return cv.one_of(*ESP8266_METHODS, upper=True, space='_')(value)
    raise NotImplementedError


def validate_method_pin(value):
    method = value[CONF_METHOD]
    method_pins = {
        'ESP8266_DMA': [3],
        'ESP8266_UART0': [1],
        'ESP8266_ASYNC_UART0': [1],
        'ESP8266_UART1': [2],
        'ESP8266_ASYNC_UART1': [2],
        'ESP32_I2S_0': list(range(0, 32)),
        'ESP32_I2S_1': list(range(0, 32)),
    }
    if CORE.is_esp8266:
        method_pins['BIT_BANG'] = list(range(0, 16))
    elif CORE.is_esp32:
        method_pins['BIT_BANG'] = list(range(0, 32))
    pins_ = method_pins[method]
    for opt in (CONF_PIN, CONF_CLOCK_PIN, CONF_DATA_PIN):
        if opt in value and value[opt] not in pins_:
            raise cv.Invalid("Method {} only supports pin(s) {}".format(
                method, ', '.join('GPIO{}'.format(x) for x in pins_)
            ), path=[CONF_METHOD])
    return value


VARIANTS = {
    'WS2812X': 'Ws2812x',
    'SK6812': 'Sk6812',
    '800KBPS': '800Kbps',
    '400KBPS': '400Kbps',
}

ESP8266_METHODS = {
    'ESP8266_DMA': 'NeoEsp8266Dma{}Method',
    'ESP8266_UART0': 'NeoEsp8266Uart0{}Method',
    'ESP8266_UART1': 'NeoEsp8266Uart1{}Method',
    'ESP8266_ASYNC_UART0': 'NeoEsp8266AsyncUart0{}Method',
    'ESP8266_ASYNC_UART1': 'NeoEsp8266AsyncUart1{}Method',
    'BIT_BANG': 'NeoEsp8266BitBang{}Method',
}
ESP32_METHODS = {
    'ESP32_I2S_0': 'NeoEsp32I2s0{}Method',
    'ESP32_I2S_1': 'NeoEsp32I2s1{}Method',
    'BIT_BANG': 'NeoEsp32BitBang{}Method',
}


def format_method(config):
    variant = VARIANTS[config[CONF_VARIANT]]
    method = config[CONF_METHOD]
    if CORE.is_esp8266:
        return ESP8266_METHODS[method].format(variant)
    if CORE.is_esp32:
        return ESP32_METHODS[method].format(variant)
    raise NotImplementedError


def validate(config):
    if CONF_PIN in config:
        if CONF_CLOCK_PIN in config or CONF_DATA_PIN in config:
            raise cv.Invalid("Cannot specify both 'pin' and 'clock_pin'+'data_pin'")
        return config
    if CONF_CLOCK_PIN in config:
        if CONF_DATA_PIN not in config:
            raise cv.Invalid("If you give clock_pin, you must also specify data_pin")
        return config
    raise cv.Invalid("Must specify at least one of 'pin' or 'clock_pin'+'data_pin'")


MakeNeoPixelBusLight = Application.struct('MakeNeoPixelBusLight')

PLATFORM_SCHEMA = cv.nameable(light.PLATFORM_SCHEMA.extend({
    cv.GenerateID(CONF_MAKE_ID): cv.declare_variable_id(MakeNeoPixelBusLight),

    cv.Optional(CONF_TYPE, default='GRB'): validate_type,
    cv.Optional(CONF_VARIANT, default='800KBPS'): validate_variant,
    cv.Optional(CONF_METHOD, default=None): validate_method,
    cv.Optional(CONF_PIN): pins.output_pin,
    cv.Optional(CONF_CLOCK_PIN): pins.output_pin,
    cv.Optional(CONF_DATA_PIN): pins.output_pin,

    cv.Required(CONF_NUM_LEDS): cv.positive_not_null_int,

    cv.Optional(CONF_POWER_SUPPLY): cv.use_variable_id(PowerSupplyComponent),
}).extend(light.ADDRESSABLE_LIGHT_SCHEMA.schema).extend(cv.COMPONENT_SCHEMA),
                              validate, validate_method_pin)


def to_code(config):
    type_ = config[CONF_TYPE]
    has_white = 'W' in type_
    if has_white:
        func = App.make_neo_pixel_bus_rgbw_light
        color_feat = global_ns.NeoRgbwFeature
    else:
        func = App.make_neo_pixel_bus_rgb_light
        color_feat = global_ns.NeoRgbFeature

    template = TemplateArguments(getattr(global_ns, format_method(config)), color_feat)
    rhs = func(template, config[CONF_NAME])
    make = variable(config[CONF_MAKE_ID], rhs, type=MakeNeoPixelBusLight.template(template))
    output = make.Poutput

    if CONF_PIN in config:
        cg.add(output.add_leds(config[CONF_NUM_LEDS], config[CONF_PIN]))
    else:
        cg.add(output.add_leds(config[CONF_NUM_LEDS], config[CONF_CLOCK_PIN], config[CONF_DATA_PIN]))

    cg.add(output.set_pixel_order(getattr(ESPNeoPixelOrder, type_)))

    if CONF_POWER_SUPPLY in config:
        power_supply = yield get_variable(config[CONF_POWER_SUPPLY])
        cg.add(output.set_power_supply(power_supply))

    light.setup_light(make.Pstate, output, config)
    register_component(output, config)


REQUIRED_BUILD_FLAGS = '-DUSE_NEO_PIXEL_BUS_LIGHT'

LIB_DEPS = 'NeoPixelBus@2.4.1'
