def routes(config):
    config.add_route('index', '/')
    config.add_route('sheet', '/c{uri:.*}', factory='ttfrog.webserver.controllers.CharacterSheet')
    config.add_route('data', '/_/{table_name}{uri:.*}', factory='ttfrog.webserver.controllers.JsonData')
