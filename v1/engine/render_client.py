from flask import jsonify
from v1.engine.models import Screen, ScreenGroup, Configuration

def render_client(id):
    screen = Screen.query.filter_by(id=id, deleted=False).first()
    if not screen:
        return jsonify(config={'status': {'active': False}})
    else:
        active = screen.active
        config_v = screen.config_v
        config_id = screen.config_id

    if screen.group_id:
        group = ScreenGroup.query.filter_by(id=screen.group_id).first()
        if group:
            if active == False:
                active = False
            else:
                active = group.active
            config_v = group.config_v
            config_id = group.config_id
    else:
        class DummyGroup(object):
            pass
        group = DummyGroup()
        group.name = None

    conf = Configuration.query.filter_by(id=config_id, deleted=False).first().serialize()

    config = {
                'status': {
                            'active': active,
                            'maintenanceText': 'Schermo in manutenzione',
                            'screenName': screen.name,
                            'groupName': group.name,
                            'configVersion': config_v,
                            'configID': config_id
                },

                'head': conf['head'],
                'bottom': conf['bottom'],
                'body': conf['body']
            }

    return jsonify(config=config)