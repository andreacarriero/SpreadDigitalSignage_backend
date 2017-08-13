from flask import jsonify
from v1.engine.models import Screen, ScreenGroup

def render_client(id):
    screen = Screen.query.filter_by(id=id, deleted=False).first()
    if not screen:
        return jsonify(config={'status': {'active': False}})
    else:
        active = screen.active
        config_v = screen.config_v

    if screen.group_id:
        group = ScreenGroup.query.filter_by(id=screen.group_id).first()
        if group:
            if active == False:
                active = False
            else:
                active = group.active
            config_v = group.config_v
    else:
        class DummyGroup(object):
            pass
        group = DummyGroup()
        group.name = None

    config = {
                'status': {
                            'active': active,
                            'maintenanceText': 'Schermo in manutenzione',
                            'screenName': screen.name,
                            'groupName': group.name,
                            'configVersion': config_v
                },

                'head': {
                            'active': True,

                            'height': '70px',
                            'fontSize': '3em',
                            'bgColor': '#003459',
                            'textColor': '#fff',
                            'borderColor': '#fff',

                            'logo': {
                                'active': True,
                                'url': 'logo.png'
                            },

                            'content': {
                                'active': False,
                                'text': 'Digital Signage'
                            },

                            'clock': {
                                'active': True,
                                'textColor': '#fff',
                                'bgColor': '#003459'
                            }
                        },

                'bottom': {
                            'active': True,
                            'content': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec tempus ultrices leo sed lacinia. Mauris eleifend luctus turpis et molestie. Donec ac lorem egestas leo varius feugiat quis eu tortor.',
                            'marquee': True,

                            'height': '70px',
                            'fontSize': '2em',
                            'bgColor': '#003459',
                            'textColor': '#fff'
                },

                'body': {   
                            'background': {
                                'bgColor': '#00A8E8',
                                'bgImage': None
                            },

                            'content': {
                                'fixedContent': [
                                    {
                                        'active': True,
                                        'bgColor': '#007EA7',
                                        'textColor': '#fff',
                                        'borderColor': '#fff',
                                        'fontSize': '3em',
                                        'marquee': False,
                                        'content': 'Riunione ore 10 sala 210A'
                                    },
                                    {
                                        'active': True,
                                        'bgColor': '#007EA7',
                                        'textColor': '#fff',
                                        'borderColor': '#fff',
                                        'fontSize': '3em',
                                        'marquee': False,
                                        'content': 'Interruzione servizi web dal 01/08 al 10/08 per manutenzione'
                                    }
                                ],

                                'columns': [
                                    {
                                        'borderColor': '#fff',
                                        'textColor': '#fff',
                                        'html': '<h1>Titolo</h1><h2>Sottotitolo</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam lacinia enim fermentum metus venenatis ultrices.</p>'
                                    },
                                    {
                                        'borderColor': '#fff',
                                        'textColor': '#fff',
                                        'html': '<h1>Titolo</h1><h2>Sottotitolo</h2><p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam lacinia enim fermentum metus venenatis ultrices. Sed turpis sapien, posuere et nunc ac, sagittis egestas nibh. Nam egestas quam sed diam porttitor faucibus. Curabitur interdum justo non tellus pellentesque pharetra. Nam sed eros sem. Phasellus ac ipsum condimentum, rhoncus odio et, pellentesque elit. Curabitur posuere tempor vestibulum. Curabitur dolor magna, faucibus at felis nec, elementum blandit eros. Proin sit amet sagittis purus, quis molestie felis. Nulla sagittis urna libero, eu fringilla risus laoreet eget. Donec ac convallis nisi. Cras dictum elit ut faucibus bibendum. Duis sit amet eros et nunc fermentum sollicitudin. Aenean tincidunt, nunc vitae aliquet congue, sapien libero tincidunt nunc, nec auctor neque ante ac diam. Fusce auctor ultrices metus eget rutrum. Maecenas varius tellus eros, tempus interdum purus congue sed. Vivamus efficitur facilisis erat id mattis. Integer vitae libero diam. Phasellus egestas nulla leo, et sagittis nisi dapibus eget. Ut ut dictum erat. Vestibulum hendrerit luctus nunc at laoreet. Nullam a feugiat ante. Proin bibendum sollicitudin euismod. Suspendisse vehicula imperdiet molestie. Sed mollis dui eu urna gravida vestibulum vel quis tellus. Vestibulum et dapibus tortor, quis gravida ante. Aliquam at tempor justo. Nullam imperdiet finibus porta. In sed blandit purus. Sed faucibus sed lectus sed posuere. In convallis nunc eget sodales venenatis. Nam eu lorem ut augue sollicitudin semper. Aliquam eget sodales est, eget tempor magna. Vivamus vitae sapien bibendum, pulvinar nibh eget, lacinia sem. Praesent ornare lacus eget dolor lacinia sollicitudin. Phasellus commodo orci consequat ex varius elementum. Morbi eget tincidunt nisl. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris fringilla augue massa, in laoreet nisl vestibulum non. Vivamus ac mollis sem, finibus volutpat turpis. Praesent feugiat faucibus magna, vel egestas mi vehicula sit amet. Sed rutrum sapien mauris, eget volutpat mauris auctor ac. Nullam consequat sapien justo, a auctor tellus volutpat a. Maecenas maximus lacinia orci, eget mollis sapien feugiat ut. In aliquam, dolor ut auctor aliquam, lectus libero tristique magna, a elementum eros quam sed leo. Nunc non risus et ex sagittis posuere quis et turpis. Cras pellentesque magna id justo consequat porta. Maecenas pellentesque sed mauris nec mattis. Nam porta mauris vel blandit aliquam.Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam lacinia enim fermentum metus venenatis ultrices. Sed turpis sapien, posuere et nunc ac, sagittis egestas nibh. Nam egestas quam sed diam porttitor faucibus. Curabitur interdum justo non tellus pellentesque pharetra. Nam sed eros sem. Phasellus ac ipsum condimentum, rhoncus odio et, pellentesque elit. Curabitur posuere tempor vestibulum. Curabitur dolor magna, faucibus at felis nec, elementum blandit eros. Proin sit amet sagittis purus, quis molestie felis. Nulla sagittis urna libero, eu fringilla risus laoreet eget. Donec ac convallis nisi. Cras dictum elit ut faucibus bibendum. Duis sit amet eros et nunc fermentum sollicitudin. Aenean tincidunt, nunc vitae aliquet congue, sapien libero tincidunt nunc, nec auctor neque ante ac diam. Fusce auctor ultrices metus eget rutrum. Maecenas varius tellus eros, tempus interdum purus congue sed. Vivamus efficitur facilisis erat id mattis. Integer vitae libero diam. Phasellus egestas nulla leo, et sagittis nisi dapibus eget. Ut ut dictum erat. Vestibulum hendrerit luctus nunc at laoreet. Nullam a feugiat ante. Proin bibendum sollicitudin euismod. Suspendisse vehicula imperdiet molestie. Sed mollis dui eu urna gravida vestibulum vel quis tellus. Vestibulum et dapibus tortor, quis gravida ante. Aliquam at tempor justo. Nullam imperdiet finibus porta. In sed blandit purus. Sed faucibus sed lectus sed posuere. In convallis nunc eget sodales venenatis. Nam eu lorem ut augue sollicitudin semper. Aliquam eget sodales est, eget tempor magna. Vivamus vitae sapien bibendum, pulvinar nibh eget, lacinia sem. Praesent ornare lacus eget dolor lacinia sollicitudin. Phasellus commodo orci consequat ex varius elementum. Morbi eget tincidunt nisl. Interdum et malesuada fames ac ante ipsum primis in faucibus. Mauris fringilla augue massa, in laoreet nisl vestibulum non. Vivamus ac mollis sem, finibus volutpat turpis. Praesent feugiat faucibus magna, vel egestas mi vehicula sit amet. Sed rutrum sapien mauris, eget volutpat mauris auctor ac. Nullam consequat sapien justo, a auctor tellus volutpat a. Maecenas maximus lacinia orci, eget mollis sapien feugiat ut. In aliquam, dolor ut auctor aliquam, lectus libero tristique magna, a elementum eros quam sed leo. Nunc non risus et ex sagittis posuere quis et turpis. Cras pellentesque magna id justo consequat porta. Maecenas pellentesque sed mauris nec mattis. Nam porta mauris vel blandit aliquam.</p>'
                                    }                                    
                                ]
                            }
                        }
            }

    return jsonify(config=config)