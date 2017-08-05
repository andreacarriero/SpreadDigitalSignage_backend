from flask import render_template, jsonify

def render_client():
    config = {
                'head': {
                            'active': True,
                            'text': 'Spread - Digital Signage',
                            'marquee': False,
                            'bg_color': '#000',
                            'text_color': '#fff'
                        },

                'footer': {
                            'active': True,
                            'text': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec tempus ultrices leo sed lacinia. Mauris eleifend luctus turpis et molestie. Donec ac lorem egestas leo varius feugiat quis eu tortor.',
                            'marquee': True,
                            'bg_color': '#000',
                            'text_color': 'red'
                },

                'body': {
                            'bg_color': 'red'
                        },

                'content': []
            }

    return render_template('client/v1/index.html', config=config)