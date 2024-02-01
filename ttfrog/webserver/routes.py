def routes(config):
    config.add_route('index', '/')
    config.add_route('sheet', '/sheet/{slug}/{name}', factory='ttfrog.webserver.controllers.CharacterSheet')
