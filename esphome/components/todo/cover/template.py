from esphome import automation
from esphome.automation import ACTION_REGISTRY
from esphome.components import cover
import esphome.config_validation as cv
import esphome.codegen as cg
from esphome.const import CONF_ASSUMED_STATE, CONF_CLOSE_ACTION, CONF_CURRENT_OPERATION, CONF_ID, \
    CONF_LAMBDA, CONF_NAME, CONF_OPEN_ACTION, CONF_OPTIMISTIC, CONF_POSITION, CONF_RESTORE_MODE, \
    CONF_STATE, CONF_STOP_ACTION


TemplateCover = cover.cover_ns.class_('TemplateCover', cover.Cover)
CoverPublishAction = cover.cover_ns.class_('CoverPublishAction', Action)

TemplateCoverRestoreMode = cover.cover_ns.enum('TemplateCoverRestoreMode')
RESTORE_MODES = {
    'NO_RESTORE': TemplateCoverRestoreMode.NO_RESTORE,
    'RESTORE': TemplateCoverRestoreMode.RESTORE,
    'RESTORE_AND_CALL': TemplateCoverRestoreMode.RESTORE_AND_CALL,
}

PLATFORM_SCHEMA = cv.nameable(cover.COVER_PLATFORM_SCHEMA.extend({
    cv.GenerateID(): cv.declare_variable_id(TemplateCover),
    cv.Optional(CONF_LAMBDA): cv.lambda_,
    cv.Optional(CONF_OPTIMISTIC): cv.boolean,
    cv.Optional(CONF_ASSUMED_STATE): cv.boolean,
    cv.Optional(CONF_OPEN_ACTION): automation.validate_automation(single=True),
    cv.Optional(CONF_CLOSE_ACTION): automation.validate_automation(single=True),
    cv.Optional(CONF_STOP_ACTION): automation.validate_automation(single=True),
    cv.Optional(CONF_RESTORE_MODE): cv.one_of(*RESTORE_MODES, upper=True),
}).extend(cv.COMPONENT_SCHEMA))


def to_code(config):
    rhs = App.register_component(TemplateCover.new(config[CONF_NAME]))
    var = Pvariable(config[CONF_ID], rhs)
    cover.register_cover(var, config)
    register_component(var, config)

    if CONF_LAMBDA in config:
        template_ = yield process_lambda(config[CONF_LAMBDA], [],
                                         return_type=optional.template(float))
        cg.add(var.set_state_lambda(template_))
    if CONF_OPEN_ACTION in config:
        automation.build_automations(var.get_open_trigger(), [],
                                     config[CONF_OPEN_ACTION])
    if CONF_CLOSE_ACTION in config:
        automation.build_automations(var.get_close_trigger(), [],
                                     config[CONF_CLOSE_ACTION])
    if CONF_STOP_ACTION in config:
        automation.build_automations(var.get_stop_trigger(), [],
                                     config[CONF_STOP_ACTION])
    if CONF_OPTIMISTIC in config:
        cg.add(var.set_optimistic(config[CONF_OPTIMISTIC]))
    if CONF_ASSUMED_STATE in config:
        cg.add(var.set_assumed_state(config[CONF_ASSUMED_STATE]))
    if CONF_RESTORE_MODE in config:
        cg.add(var.set_restore_mode(RESTORE_MODES[config[CONF_RESTORE_MODE]]))


BUILD_FLAGS = '-DUSE_TEMPLATE_COVER'

CONF_COVER_TEMPLATE_PUBLISH = 'cover.template.publish'
COVER_TEMPLATE_PUBLISH_ACTION_SCHEMA = cv.Schema({
    cv.Required(CONF_ID): cv.use_variable_id(cover.Cover),
    cv.Exclusive(CONF_STATE, 'pos'): cv.templatable(cover.validate_cover_state),
    cv.Exclusive(CONF_POSITION, 'pos'): cv.templatable(cv.zero_to_one_float),
    cv.Optional(CONF_CURRENT_OPERATION): cv.templatable(cover.validate_cover_operation),
})


@ACTION_REGISTRY.register(CONF_COVER_TEMPLATE_PUBLISH,
                          COVER_TEMPLATE_PUBLISH_ACTION_SCHEMA)
def cover_template_publish_to_code(config, action_id, template_arg, args):
    var = yield get_variable(config[CONF_ID])
    type = CoverPublishAction.template(template_arg)
    rhs = type.new(var)
    action = Pvariable(action_id, rhs, type=type)
    if CONF_STATE in config:
        template_ = yield templatable(config[CONF_STATE], args, float,
                                      to_exp=cover.COVER_STATES)
        cg.add(action.set_position(template_))
    if CONF_POSITION in config:
        template_ = yield templatable(config[CONF_POSITION], args, float,
                                      to_exp=cover.COVER_STATES)
        cg.add(action.set_position(template_))
    if CONF_CURRENT_OPERATION in config:
        template_ = yield templatable(config[CONF_CURRENT_OPERATION], args, cover.CoverOperation,
                                      to_exp=cover.COVER_OPERATIONS)
        cg.add(action.set_current_operation(template_))
    yield action
