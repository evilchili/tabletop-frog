def routes(config):
    config.add_route('index', '/')
    config.add_route('sheet', '/c{uri:.*}', factory='ttfrog.webserver.controllers.CharacterSheet')
